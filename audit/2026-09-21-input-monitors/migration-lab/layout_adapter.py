import importlib.util,json,sys
from pathlib import Path
sys.path.insert(0,'/root/apx-host-development-mode-v1/apx/src')
spec=importlib.util.spec_from_file_location('checks','/root/apx-host-development-mode-v1/apx/scripts/physical-pilot/apx-native-offline-layout-v3.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
if sys.argv[1]=='--authorize':m.authorize(Path(sys.argv[2]),json.loads(Path(sys.argv[3]).read_text()),sys.argv[4])
else:
 table=json.loads(Path(sys.argv[1]).read_text())['partitiontable']
 table['device']='/dev/nvme0n1'
 for p in table['partitions']:p['node']='/dev/nvme0n1p'+p['node'].rsplit('p',1)[1]
 m.validate(table,json.loads(Path(sys.argv[2]).read_text()),sys.argv[3])
