from pathlib import Path
import json,subprocess,sys,shlex,hashlib
repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo/'src'))
from apx_native_offline_v3 import render
from apx_native_instances_v3 import canonical_layout
lab=Path(__file__).resolve().parent/'migration-lab';plan=json.loads((lab/'plan.json').read_text());manifest=json.loads((lab/'manifest.json').read_text());loop=(lab/'loop.txt').read_text().strip();root=lab/'root'
assert Path('/sys/class/block/'+Path(loop).name+'/loop/backing_file').read_text().strip()==str(lab/'disk.raw')
subprocess.run(['btrfs','property','set',str(lab/'disk.raw'),'compression','zstd'],check=True)
helper=repo/'scripts/physical-pilot/apx-native-offline-layout-v3.py'
adapter=lab/'layout_adapter.py';adapter.write_text('''import importlib.util,json,sys\nfrom pathlib import Path\nsys.path.insert(0,'''+repr(str(repo/'src'))+''')\nspec=importlib.util.spec_from_file_location('checks','''+repr(str(helper))+''');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)\nif sys.argv[1]=='--authorize':m.authorize(Path(sys.argv[2]),json.loads(Path(sys.argv[3]).read_text()),sys.argv[4])\nelse:\n table=json.loads(Path(sys.argv[1]).read_text())['partitiontable']\n table['device']='/dev/nvme0n1'\n for p in table['partitions']:p['node']='/dev/nvme0n1p'+p['node'].rsplit('p',1)[1]\n m.validate(table,json.loads(Path(sys.argv[2]).read_text()),sys.argv[3])\n''')
for rollback in (True,):
 action='rollback' if rollback else 'relocate'
 if rollback:subprocess.run(['cryptsetup','open','--key-file',str(lab/'key'),loop+'p2','apx-native-migration-lab'],check=True)
 subprocess.run(['mount','-o','subvol=@','/dev/mapper/apx-native-migration-lab',str(root)],check=True)
 job=root/'var/lib/apx/native-environments/migrations-v3'/plan['new']['generation'];authorization=job/'authorization.json'
 authorization.write_text(json.dumps(dict(schema=3,profile='apx-native-offline-authorization-v3',generation=plan['new']['generation'],plan_sha256=plan['plan_sha256'],action=action,state='approved')));authorization.chmod(0o400)
 subprocess.run(['umount',str(root)],check=True)
 script=render(plan,manifest,rollback=rollback)
 script='\n'.join(line for line in script.splitlines() if '/etc/initrd-release' not in line and '/proc/cmdline' not in line and '/sys/class/block/nvme0n1/device/serial' not in line)+'\n'
 script=script.replace('/dev/nvme0n1',loop).replace('/dev/mapper/cryptroot','/dev/mapper/apx-native-migration-lab').replace('work=/run/apx-native-v3-root','work='+shlex.quote(str(root))).replace('status_dir=/run/apx-native-v3-esp','status_dir='+shlex.quote(str(lab/'esp')))
 script=script.replace('/usr/lib/apx/apx-native-offline-layout-v3.py',str(adapter)).replace('/usr/share/apx/native-v3-plan.json',str(lab/'plan.json')).replace('/run/apx-observed-gpt.json',str(lab/'observed.json'))
 script=script.replace('systemctl stop systemd-cryptsetup@cryptroot.service','cryptsetup close apx-native-migration-lab').replace('systemctl --no-block --force reboot || true','exit 1').replace('systemctl --no-block --force reboot','exit 0').replace('while :; do sleep 1; done','')
 assert 'systemctl' not in script and '/dev/nvme' not in script
 path=lab/(action+'-lab.sh');path.write_text(script)
 print('START',action,flush=True)
 subprocess.run(['bash',str(path)],check=True)
 observed=json.loads(subprocess.check_output(['sfdisk','--json',loop],text=True))['partitiontable'];observed['device']='/dev/nvme0n1'
 for p in observed['partitions']:p['node']='/dev/nvme0n1p'+p['node'].rsplit('p',1)[1]
 assert canonical_layout(observed)==canonical_layout(plan['before' if rollback else 'after'])
 payload=subprocess.check_output(['ntfscat','-f',loop+'p3','/payload.txt']);assert payload==(lab/'payload').read_bytes()
 print('PASS',action,'Windows payload and exact GPT verified',flush=True)
subprocess.run(['cryptsetup','open','--key-file',str(lab/'key'),loop+'p2','apx-native-migration-lab'],check=True)
subprocess.run(['mount','-o','ro,subvol=@','/dev/mapper/apx-native-migration-lab',str(root)],check=True)
try:assert (root/'linux-sentinel.txt').read_text()=='APX root data must survive relocation and rollback.\n'
finally:subprocess.run(['umount',str(root)],check=True);subprocess.run(['cryptsetup','close','apx-native-migration-lab'],check=True)
subprocess.run(['losetup','-d',loop],check=True)
(lab.parent/'native-offline-relocation-result.json').write_text(json.dumps(dict(relocation='passed',rollback='passed',linux_payload='preserved',windows_payload='preserved',physical_disk_modified=False),indent=2))
