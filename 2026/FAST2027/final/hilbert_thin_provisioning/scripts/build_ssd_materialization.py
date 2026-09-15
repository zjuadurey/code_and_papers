import _ssd_common as common
import subprocess,json,platform
commands=[['cmake','-S','native/ssd_materialization','-B','build/ssd_materialization','-DCMAKE_BUILD_TYPE=Release'],
          ['cmake','--build','build/ssd_materialization','-j','4']]
logs=[]
for command in commands:
    r=subprocess.run(command,capture_output=True,text=True)
    logs.append('$ '+' '.join(command)+'\n'+r.stdout+r.stderr)
    print(logs[-1])
    r.check_returncode()
(common.OUT/'logs/build.log').write_text('\n'.join(logs))
(common.OUT/'build.json').write_text(json.dumps(dict(commands=commands,binary_sha256=common.digest(common.BINARY),
    compiler=subprocess.check_output(['g++','--version'],text=True),cmake=subprocess.check_output(['cmake','--version'],text=True),
    flags=(common.ROOT/'build/ssd_materialization/CMakeFiles/qthin_storage.dir/flags.make').read_text()),indent=2))
