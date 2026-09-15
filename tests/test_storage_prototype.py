import json,subprocess
import numpy as np
import pytest
from htp.storage.benchmark_config import BINARY,disk_plan,product_vector,logical_mapping,factor_args
from htp.storage.result_schema import parse_native

def invoke(args,success=True):
    assert BINARY.exists(),'Build native prototype first: python scripts/build_ssd_materialization.py'
    r=subprocess.run([str(BINARY)]+args,capture_output=True,text=True)
    if success:assert r.returncode==0,r.stderr
    else:assert r.returncode!=0
    return r

def test_mapping_appends_preserves_existing():
    m=logical_mapping(7,'v');assert m['v']==7 and all(m[i]==i for i in range(7))
    with pytest.raises(ValueError):logical_mapping(7,3)

@pytest.mark.parametrize('seed',range(5))
def test_product_normalization(seed):
    assert abs(np.linalg.norm(product_vector('random_seeded',seed))-1)<1e-14

def test_low_disk_skip():
    assert not disk_plan(30,800*1024**3,43*1024**3)['fits']
    assert disk_plan(29,800*1024**3,43*1024**3)['fits']

@pytest.mark.parametrize('q,chunk,target',[(-1,4096,0),(41,4096,0),(10,5000,0),(10,2**28,0),(20,4096,15)])
def test_invalid_sizes_fail(tmp_path,q,chunk,target):
    invoke(['--q',str(q),'--chunk-bytes',str(chunk),'--target',str(target),'--input',str(tmp_path/'missing'),
            '--output',str(tmp_path/'out'),'--policy','PRODUCT_FUSED','--gate','cz'],False)

def test_no_raw_device_output():
    invoke(['--action','generate','--q','8','--output','/dev/qthin-forbidden'],False)

def test_file_sizing_generation_and_no_overwrite(tmp_path):
    output=tmp_path/'input';args=['--action','generate','--q','8','--output',str(output),'--chunk-bytes','4096']
    invoke(args);assert output.stat().st_size==4096
    original=output.read_bytes();invoke(args,False);assert output.read_bytes()==original

@pytest.mark.parametrize('gate',['cx_product_control','cx_product_target','cz'])
def test_native_fused_and_traffic(tmp_path,gate):
    q=9;rng=np.random.default_rng(7);x=rng.normal(size=1<<q)+1j*rng.normal(size=1<<q);x/=np.linalg.norm(x)
    inp=tmp_path/'input';x.tofile(inp);v=product_vector('random_seeded',9);ys=[]
    for policy in ['NAIVE_PRODUCT','PRODUCT_FUSED']:
        output=tmp_path/policy
        raw=invoke(['--input',str(inp),'--output',str(output),'--q',str(q),'--chunk-bytes','4096','--policy',policy,'--gate',gate]+factor_args(v))
        metrics=parse_native(raw.stdout);assert metrics['configured_buffer_bytes']<=256*1024**2
        ys.append(np.fromfile(output,complex))
    assert np.max(np.abs(ys[0]-ys[1]))<1e-13

def test_sparse_extent_sizing(tmp_path):
    inp=tmp_path/'input';invoke(['--action','generate','--q','16','--output',str(inp)])
    out=tmp_path/'thin'
    m=parse_native(invoke(['--input',str(inp),'--output',str(out),'--q','16','--policy','THIN_BASIS','--gate','cx_product_target']+factor_args(product_vector('basis0',0))).stdout)
    assert m['logical_output_bytes']==2*(16<<16)
    assert m['allocated_output_bytes_before_gate']<m['allocated_output_bytes_after_gate']

def test_result_parsing_rejects_fake_success():
    with pytest.raises(ValueError):parse_native(json.dumps({'status':'FAIL'}))

def test_statistics_keep_outliers_and_missing_counters():
    from htp.storage.analysis import statistic,ratio
    s=statistic([1,2,9])
    assert s['median']==2 and s['min']==1 and s['max']==9 and s['cv']>0
    assert np.isnan(statistic([np.nan])['median']) and np.isnan(ratio(1,0))

def test_direct_aligned_probe(tmp_path):
    from htp.storage.environment_probe import direct_probe
    if not direct_probe(tmp_path)['supported']:pytest.skip('O_DIRECT unsupported on temporary filesystem')
    result=invoke(['--action','probe','--output',str(tmp_path/'aligned')])
    assert json.loads(result.stdout)['alignment']==4096

def test_unsupported_direct_reports_reason_and_cleans_probe(tmp_path,monkeypatch):
    import errno
    import htp.storage.environment_probe as probe
    original_open=probe.os.open
    def unsupported(path,flags,*args,**kwargs):
        if flags & probe.os.O_DIRECT:
            raise OSError(errno.EOPNOTSUPP,'Direct I/O not supported')
        return original_open(path,flags,*args,**kwargs)
    monkeypatch.setattr(probe.os,'open',unsupported)
    result=probe.direct_probe(tmp_path)
    assert not result['supported'] and 'not supported' in result['reason']
    assert not list(tmp_path.iterdir())
