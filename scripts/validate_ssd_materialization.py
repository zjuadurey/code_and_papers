import _ssd_common as common
import json,subprocess,tempfile,datetime
from pathlib import Path
import numpy as np
import pandas as pd
from qiskit.quantum_info import Statevector,Operator,random_unitary
from qiskit.circuit.library import CXGate,CZGate
from htp.storage.benchmark_config import factor_args,product_vector
from htp.storage.result_schema import parse_native

common.frozen_check()
cfg=common.config();rng=np.random.default_rng(cfg['random_seed'])
env=json.loads((common.OUT/'environment.json').read_text())
report=dict(status='RUNNING',correctness_cases=0,incorrect_cases=0,native_executions=0,
            max_abs_error=0.,max_infidelity=0.,seed=cfg['random_seed'],threshold=1e-12)
records=[]
(common.OUT/'correctness.json').write_text(json.dumps(report,indent=2))
try:
    with tempfile.TemporaryDirectory(prefix='qthin-validation-',dir=common.bench_dir()) as tmp:
        directory=Path(tmp);inp=directory/'input.bin';matrix_path=directory/'unitary.bin'
        for index in range(cfg['correctness_cases']+96):
            direct=index>=cfg['correctness_cases']+64 and env['direct_io']['supported']
            q=int(rng.integers(8,13) if direct else rng.integers(1,13));target=int(rng.integers(q))
            backing=rng.normal(size=1<<q)+1j*rng.normal(size=1<<q);backing/=np.linalg.norm(backing)
            backing.astype(np.complex128).tofile(inp)
            basis=cfg['correctness_cases']<=index<cfg['correctness_cases']+64
            v=product_vector('basis'+str(index%2) if basis else 'random_seeded',cfg['random_seed']+index)
            name=['cx_product_control','cx_product_target','cz','generic'][index%4]
            u=Operator(CXGate() if name.startswith('cx') else CZGate()).data if name!='generic' else random_unitary(4,seed=cfg['random_seed']+index).data
            u.astype(np.complex128).tofile(matrix_path)
            ids=[target,q] if name=='cx_product_target' else [q,target]
            reference=Statevector(np.kron(v,backing)).evolve(Operator(u),qargs=ids).data
            policies=['NAIVE_BASIS','THIN_BASIS','FUSED_BASIS'] if basis else ['NAIVE_PRODUCT','PRODUCT_FUSED']
            errors=[];infs=[];outputs=[]
            for policy in policies:
                output=directory/(policy+'.bin')
                cmd=[str(common.BINARY),'--input',str(inp),'--output',str(output),'--q',str(q),'--mode','direct' if direct else 'buffered',
                     '--policy',policy,'--gate',name,'--target',str(target),'--matrix',str(matrix_path)]+factor_args(v)
                r=subprocess.run(cmd,capture_output=True,text=True);r.check_returncode();metrics=parse_native(r.stdout)
                result=np.fromfile(output,dtype=np.complex128);output.unlink();outputs.append(result)
                error=float(np.max(np.abs(reference-result)))
                fidelity=float(abs(np.vdot(reference,result))**2/(np.vdot(reference,reference).real*np.vdot(result,result).real))
                errors.append(error);infs.append(max(0.,1-fidelity));report['native_executions']+=1
                assert error<=1e-12 and 1-fidelity<=1e-12,(index,policy,error,fidelity)
            assert np.max(np.abs(outputs[0]-outputs[-1]))<=1e-12
            report['correctness_cases']+=1
            report['max_abs_error']=max(report['max_abs_error'],max(errors));report['max_infidelity']=max(report['max_infidelity'],max(infs))
            records.append(dict(case=index,q_old=q,target=target,gate=name,basis=basis,io_mode='direct' if direct else 'buffered',
                                native_policies=';'.join(policies),max_abs_error=max(errors),infidelity=max(infs),passed=True))
            if (index+1)%200==0:print('Native cross-file correctness',index+1,flush=True)
    report['status']='PASS'
except Exception as e:
    report.update(status='FAIL',incorrect_cases=1,error=str(e));raise
finally:
    report.update(binary_sha256=common.digest(common.BINARY),code_sha256=common.code_hashes(),timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (common.OUT/'correctness.json').write_text(json.dumps(report,indent=2))
    pd.DataFrame(records).to_csv(common.OUT/'correctness_cases.csv',index=False)
common.frozen_check()
print(json.dumps({k:v for k,v in report.items() if k!='code_sha256'},indent=2))
