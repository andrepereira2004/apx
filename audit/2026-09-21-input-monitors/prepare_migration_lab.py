from pathlib import Path
import json,os,subprocess,sys,uuid
repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo/'src'))
from apx_native_instances_v3 import plan_second_windows
from apx_native_backup_v3 import prepare_images
from apx_native_offline_v3 import render
out=Path(__file__).resolve().parent;lab=out/'migration-lab';lab.mkdir(mode=0o700)
base=json.loads((out/'hub-native-preview.json').read_text())['plan'];table=base['before'];table['id']=str(uuid.uuid4()).upper()
for p in table['partitions']:p['uuid']=str(uuid.uuid4()).upper()
legacy=dict(schema=2,profile='apx-native-environment-v2',name='windows',state='ready',generation=str(uuid.uuid4()),disk_id=table['id'],disk_serial='APX-MIGRATION-LAB',windows_partuuid=table['partitions'][2]['uuid'],windows_esp_partuuid=table['partitions'][0]['uuid'],windows_bytes=table['partitions'][2]['size']*512)
plan=plan_second_windows(table,legacy,new_name='windows-lab',new_generation=str(uuid.uuid4()),**base['measurements'])
(lab/'plan.json').write_text(json.dumps(plan,indent=2));disk=lab/'disk.raw'
with disk.open('xb') as f:f.truncate(512110190592)
lines=['label: gpt','label-id: '+table['id'],'unit: sectors']
for i,p in enumerate(table['partitions'],1):lines.append(f'{i}: start={p["start"]}, size={p["size"]}, type={p["type"]}, uuid={p["uuid"]}, name="{p["name"]}"')
subprocess.run(['sfdisk',str(disk)],input='\n'.join(lines)+'\n',text=True,check=True,stdout=subprocess.DEVNULL)
loop=subprocess.check_output(['losetup','-f','--show','-P',str(disk)],text=True).strip();(lab/'loop.txt').write_text(loop)
key=lab/'key';key.write_bytes(os.urandom(32));key.chmod(0o600)
subprocess.run(['cryptsetup','luksFormat','--batch-mode','--type','luks2','--pbkdf','pbkdf2','--key-file',str(key),loop+'p2'],check=True)
subprocess.run(['cryptsetup','open','--key-file',str(key),loop+'p2','apx-native-migration-lab'],check=True)
subprocess.run(['mkfs.btrfs','-f','/dev/mapper/apx-native-migration-lab'],check=True,stdout=subprocess.DEVNULL)
root=lab/'root';root.mkdir();subprocess.run(['mount','/dev/mapper/apx-native-migration-lab',str(root)],check=True)
subprocess.run(['btrfs','subvolume','create',str(root/'@')],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['umount',str(root)],check=True);subprocess.run(['mount','-o','subvol=@','/dev/mapper/apx-native-migration-lab',str(root)],check=True)
(root/'linux-sentinel.txt').write_text('APX root data must survive relocation and rollback.\n')
for number,label in [(1,'APX_EFI'),(4,'APXWINSETUP')]:subprocess.run(['mkfs.fat','-F','32','-n',label,loop+'p'+str(number)],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['mkntfs','-F','-Q','-L','APXLEGACY',loop+'p3'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
payload=lab/'payload';payload.write_bytes(b'APX legacy Windows data\n'*4096);subprocess.run(['ntfscp',loop+'p3',str(payload),'/payload.txt'],check=True)
job=root/'var/lib/apx/native-environments/migrations-v3'/plan['new']['generation'];job.mkdir(parents=True,mode=0o700)
print('Preparing and hashing backup images inside encrypted Btrfs test volume',flush=True)
manifest=prepare_images(Path(loop+'p3'),job/'images',120*1024**3)
(lab/'manifest.json').write_text(json.dumps(manifest,indent=2));(lab/'offline.sh').write_text(render(plan,manifest));(lab/'rollback.sh').write_text(render(plan,manifest,rollback=True))
print('MIGRATION LAB PREPARED',str(lab),flush=True)
subprocess.run(['umount',str(root)],check=True)
