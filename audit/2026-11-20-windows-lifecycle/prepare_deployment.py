"""Prepare the review artifact; never write live metadata or guest files."""
from pathlib import Path
import json, hashlib, subprocess, sys
root=Path(__file__).resolve().parents[2]; native=Path('/var/lib/apx/native-environments')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(root/'src'))
from apx_native_instances_v3 import digest,validate_slot_layout,free_slot_record,validate_instances
manifest=Path('/usr/share/apx/native-v3-enabled.json');release=json.loads(manifest.read_text())
table=json.loads(subprocess.check_output(['sfdisk','--json','/dev/nvme0n1'],text=True))['partitiontable']
source=json.loads((native/'migrations-v3/2770478b-480f-4aea-8910-e3201d5334c5/plan.json').read_text())
expected={1:('9625f250-9acc-453a-ae63-0c863ade440f',2048,2097152),2:('8835c8f0-f02f-4fc2-9035-5dbbc191df9e',2099200,453871616),3:('099c31d8-313a-4aba-b0e0-2b59502c9674',455970816,356515840),4:('309bebb6-5c32-4e21-9c92-6d758e51389d',981340160,18874368),5:('eddf4dba-7748-5ad6-a640-c9af195f5e1e',813568000,161480704),6:('10783707-92f8-5f8a-9407-1c4fb92ab0ea',812486656,1048576),7:('b6bebab8-76cf-5a5e-9c07-fa54650ab638',813535232,32768),8:('b9aceef4-c85b-4ec5-8250-815dc69df0ee',975048704,4194304)}
assert len(table['partitions'])==8
for p in table['partitions']:assert (p['uuid'].lower(),p['start'],p['size'])==expected[int(p['node'].rsplit('p',1)[1])]
checkpoint=dict(schema=3,profile='apx-native-slot-layout-v3',source_plan_sha256=source['plan_sha256'],layout=table);checkpoint['sha256']=digest(checkpoint)
validate_slot_layout(source,table,checkpoint)
original=json.loads((native/'instances-v3/windows.json').read_text());records=[json.loads(p.read_text()) for p in (native/'instances-v3').glob('*.json')];validate_instances(records,table,'S4DYNX0R253702')
marker=free_slot_record(source,table,[original],source['new']['generation'],checkpoint=checkpoint)
files={Path('/usr/lib/apx')/name:root/'scripts/physical-pilot'/name for name in ['apx-native-lifecycle-v3.py','apx-native-windows-plan-v3.py','apx-native-boot-runner-v1.py','apx-native-windows-lifecycle-finalize-v1.py']}
files.update({Path('/usr/lib/apx')/name:root/'src'/name for name in ['apx_native_instances_v3.py','apx_native_hub_v3.py','apx_native_slot_wipe_v3.py']})
for name in ['APX-ReturnToHub.ps1','APX-ReturnToHub.vbs','README.txt','APX-ProvisionHardware.cmd']:files[Path('/usr/share/apx/native-windows-lifecycle-v1/return')/name]=root/'config/native-windows-return-v1'/name
before={n:sha(Path(n)) for n in release['files']};mismatches={Path(n).name for n in before if before[n]!=release['files'][n]}
assert mismatches=={'apx-environment-switch-v1.py','apx-environment-switch-client-v1.py','apx_environment_switch_contract.py'},mismatches
for n in mismatches:
 p=Path('/usr/lib/apx')/n;q=(root/'src'/n) if n.endswith('_contract.py') else (root/'scripts/physical-pilot'/n);assert p.read_bytes()==q.read_bytes()
after={n:sha(files[Path(n)]) if Path(n) in files else h for n,h in before.items()}
rel={'APX-ReturnToHub.ps1':'/ProgramData/APX/ReturnToHub/APX-ReturnToHub.ps1','README.txt':'/ProgramData/APX/ReturnToHub/README.txt','APX-ReturnToHub.vbs':'/ProgramData/Microsoft/Windows/Start Menu/Programs/Startup/APX-ReturnToHub.vbs'}
guests={}
for num in (3,5):
 guests[str(num)]=dict(partuuid=expected[num][0],files={name:hashlib.sha256(subprocess.check_output(['ntfscat','/dev/nvme0n1p'+str(num),path])).hexdigest() for name,path in rel.items()})
plan=dict(schema=1,layout=table,checkpoint=checkpoint,manifest_before=sha(manifest),release_before=before,release_after=after,host=[dict(target=str(p),source=str(q.relative_to(root)),before=sha(p),after=sha(q)) for p,q in files.items()],guest_sources={name:sha(root/'config/native-windows-return-v1'/name) for name in rel},guests=guests)
path=Path(__file__).with_name('deployment-plan.json');path.write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n')
print('Deployment plan SHA256:',sha(path));print('Host replacements:',len(files),'Guest payloads:',len(guests),'Slot:',marker['size_sectors']*512//1024**3,'GiB')
