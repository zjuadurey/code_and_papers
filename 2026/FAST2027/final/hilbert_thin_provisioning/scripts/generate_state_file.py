import _ssd_common as common
import argparse,subprocess,shutil,json
from pathlib import Path
from htp.storage.benchmark_config import disk_plan
from htp.storage.environment_probe import host_free
p=argparse.ArgumentParser();p.add_argument('--q',type=int,required=True);p.add_argument('--output',required=True);p.add_argument('--seed',type=int,default=20260916)
a=p.parse_args()
directory=common.bench_dir();output=Path(a.output).resolve()
if directory not in output.parents:raise ValueError('Output must be within HTP_SSD_BENCH_DIR / configured benchmark directory')
env=json.loads((common.OUT/'environment.json').read_text())
letter=(env.get('host_volume') or {}).get('DriveLetter');host=host_free(letter)
if letter and host is None:raise RuntimeError('Host free-space audit unavailable')
plan=disk_plan(a.q,shutil.disk_usage(directory).free,host)
if not plan['fits']:raise RuntimeError(f'Insufficient capacity for input plus benchmark output: {plan}')
subprocess.run([str(common.BINARY),'--action','generate','--q',str(a.q),'--output',str(output),'--seed',str(a.seed)],check=True)
