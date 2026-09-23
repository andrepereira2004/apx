from pathlib import Path
import json, os, subprocess, sys, shutil
repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo/'src'))
from apx_native_winpe_v3 import render
from apx_native_migration_v3 import copy_range
out=Path(__file__).resolve().parent;lab=out/'windows-lab';lab.mkdir(mode=0o700)
plan=json.loads((out/'hub-native-preview.json').read_text())['plan']
assets=render(plan,(repo/'config/system-images-v1/windows-internal-winpe/apx-media.cmd').read_text())
(lab/'plan.json').write_text(json.dumps(plan,indent=2))
(lab/'apx-media.cmd').write_bytes(assets['script'].encode())
(lab/'apx-expected.ini').write_bytes(assets['contract'].encode())
(lab/'assets.json').write_text(json.dumps(assets|{'script':'omitted','contract':'omitted'}))
disk=lab/'disk.raw'
with disk.open('xb') as stream:stream.truncate(512110190592)
table=plan['after'];lines=['label: gpt','label-id: '+table['id'],'unit: sectors','first-lba: '+str(table['firstlba']),'last-lba: '+str(table['lastlba'])]
# sfdisk input partition slots retain original numbers despite physical order.
for p in table['partitions']:
 number=p['node'].rsplit('p',1)[1]
 lines.append(f'{number}: start={p["start"]}, size={p["size"]}, type={p["type"]}, uuid={p["uuid"]}, name="{p["name"]}"')
subprocess.run(['sfdisk',str(disk)],input='\n'.join(lines)+'\n',text=True,check=True,stdout=subprocess.DEVNULL)
source=os.open('/dev/nvme0n1p4',os.O_RDONLY);target=os.open(disk,os.O_RDWR)
try:copy_range(source,target,table['partitions'][3]['start']*512,table['partitions'][3]['size']*512)
finally:os.close(source);os.close(target)
loop=subprocess.check_output(['losetup','--find','--show','--partscan',str(disk)],text=True).strip()
(lab/'loop.txt').write_text(loop)
assert Path('/sys/class/block/'+Path(loop).name+'/loop/backing_file').read_text().strip()==str(disk)
for number,label in [(1,'APX_EFI'),(6,assets['efi_label'])]:subprocess.run(['mkfs.fat','-F','32','-n',label,loop+'p'+str(number)],check=True,stdout=subprocess.DEVNULL)
for number,label in [(3,'APXLEGACY'),(5,assets['windows_label'])]:subprocess.run(['mkntfs','-F','-Q','-L',label,loop+'p'+str(number)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
sentinel=lab/'legacy-sentinel.txt';sentinel.write_text('The existing Windows must retain this data.\n')
subprocess.run(['ntfscp',loop+'p3',str(sentinel),'/legacy-sentinel.txt'],check=True)
for number,kind in [(1,'efi-old'),(4,'media'),(5,'windows'),(6,'efi-new')]:
 mount=lab/kind;mount.mkdir();subprocess.run(['mount',loop+'p'+str(number),str(mount)],check=True)
 try:
  if kind=='efi-old':
   (mount/'sentinel.txt').write_text('Existing shared Linux/Windows EFI must not change.\n')
  elif kind=='media':
   destination=mount/assets['media_directory'].replace('\\','/');destination.mkdir(parents=True)
   (destination/'install-contract-v3.ini').write_bytes(assets['contract'].encode())
   commands=f'add "{lab}/apx-media.cmd" /Windows/System32/apx-media.cmd\nadd "{lab}/apx-expected.ini" /Windows/System32/apx-expected.ini\n'
   subprocess.run(['wimlib-imagex','update',str(mount/'sources/boot.wim'),'2','--check'],input=commands,text=True,check=True,stdout=subprocess.DEVNULL)
  elif kind=='windows':
   (mount/'APX').mkdir();(mount/'APX/install-contract-v3.ini').write_bytes(assets['contract'].encode())
  else:
   destination=mount/'EFI/APX/native-windows';destination.mkdir(parents=True);(destination/'install-contract-v3.ini').write_bytes(assets['contract'].encode())
 finally:subprocess.run(['umount',str(mount)],check=True)
subprocess.run(['losetup','-d',loop],check=True)
shutil.copyfile(out/'windows-lab-tools/usr/share/edk2/x64/OVMF_VARS.4m.fd',lab/'OVMF_VARS.fd')
print('LAB READY',lab,flush=True)
