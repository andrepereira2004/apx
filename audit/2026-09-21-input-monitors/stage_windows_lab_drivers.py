from pathlib import Path
import json,subprocess,sys,shutil,tempfile,re
repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo/'src'));from apx_native_winpe_v3 import render
out=Path(__file__).resolve().parent;lab=out/'windows-lab';plan=json.loads((lab/'plan.json').read_text());loop=subprocess.check_output(['losetup','-f','--show','-P',str(lab/'disk.raw')],text=True).strip();source=Path(tempfile.mkdtemp(prefix='apx-lab-drivers-',dir='/run'));target=lab/'inspect-media';drivers=[]
try:
 subprocess.run(['mount','-t','ntfs3','-o','ro,nosuid,nodev,noexec','/dev/nvme0n1p3',str(source)],check=True)
 subprocess.run(['mount',loop+'p3',str(target)],check=True)
 try:
  dest=target/'Windows/System32/DriverStore/FileRepository';dest.mkdir(parents=True,exist_ok=True)
  for directory in sorted((source/'Windows/System32/DriverStore/FileRepository').iterdir()):
   if not re.fullmatch(r'(?:nv|u)[a-z0-9_.]+_amd64_[0-9a-f]{16}',directory.name):continue
   for inf in directory.glob('*.inf'):
    raw=inf.read_bytes();text=raw.decode('utf-16' if raw[:2] in (b'\xff\xfe',b'\xfe\xff') else 'utf-8',errors='replace')
    if re.search(r'^\s*Class\s*=\s*Display\s*$',text,re.MULTILINE|re.IGNORECASE):
     drivers.append(directory.name);shutil.copytree(directory,dest/directory.name);break
  assets=render(plan,(repo/'config/system-images-v1/windows-internal-winpe/apx-media.cmd').read_text(),display_drivers=drivers)
  (target/('APX-'+plan['new']['generation']+'.ini')).write_bytes(assets['contract'].encode())
 finally:subprocess.run(['umount',str(target)],check=True);subprocess.run(['umount',str(source)],check=True)
 subprocess.run(['ntfslabel','-f',loop+'p3','APXWINTARGET'],check=True)
 (lab/'apx-media.cmd').write_bytes(assets['script'].encode());(lab/'apx-expected.ini').write_bytes(assets['contract'].encode());(lab/'display-drivers.json').write_text(json.dumps(drivers))
 subprocess.run(['mkntfs','-F','-Q','-L',assets['windows_label'],loop+'p5'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 subprocess.run(['mkfs.fat','-F','32','-n',assets['efi_label'],loop+'p6'],check=True,stdout=subprocess.DEVNULL)
 for number in [4,5,6]:
  subprocess.run(['mount',loop+'p'+str(number),str(target)],check=True)
  try:
   if number==4:
    old=target/'efi/boot/bootx64.installer-saved';old.rename(old.with_name('bootx64.efi'))
    dest=target/assets['media_directory'].replace('\\','/')/'install-contract-v3.ini';dest.write_bytes(assets['contract'].encode())
    subprocess.run(['wimlib-imagex','update',str(target/'sources/boot.wim'),'2','--check'],input=f'add "{lab}/apx-media.cmd" /Windows/System32/apx-media.cmd\nadd "{lab}/apx-expected.ini" /Windows/System32/apx-expected.ini\n',text=True,check=True,stdout=subprocess.DEVNULL)
   else:
    dest=target/('APX' if number==5 else 'EFI/APX/native-windows');dest.mkdir(parents=True,exist_ok=True);(dest/'install-contract-v3.ini').write_bytes(assets['contract'].encode())
  finally:subprocess.run(['umount',str(target)],check=True)
finally:subprocess.run(['losetup','-d',loop],check=True);source.rmdir()
print('Driver-equipped installer staged:',drivers)
