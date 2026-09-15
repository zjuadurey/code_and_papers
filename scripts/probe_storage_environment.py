import _ssd_common as common
from htp.storage.environment_probe import probe
import json
common.OUT.mkdir(exist_ok=True)
common.frozen_check()
r=probe()
(common.OUT/'environment.json').write_text(json.dumps(r,indent=2))
(common.OUT/'environment.txt').write_text('\n'.join('$ '+' '.join(c['command'])+'\n'+c.get('stdout',c.get('error',''))+c.get('stderr','') for c in r['commands'])+'\n'+json.dumps({k:v for k,v in r.items() if k!='commands'},indent=2))
print(json.dumps({k:v for k,v in r.items() if k!='commands'},indent=2))
