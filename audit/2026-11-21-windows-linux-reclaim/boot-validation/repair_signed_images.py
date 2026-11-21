from pathlib import Path
import datetime,hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile
repo=Path('/root/apx-host-development-mode-v1/apx');sys.path.insert(0,str(repo/'src'))
path=repo/'scripts/physical-pilot/apx-reclaim-windows-linux-v3.py';s=importlib.util.spec_from_file_location('reclaim_fixed',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
work=Path('/var/lib/apx/native-environments/linux-reclaim-v3/2770478b-480f-4aea-8910-e3201d5334c5')
backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-reclaim-signed-boot-fix');backup.mkdir(mode=0o700)
for p in m.IMAGES:shutil.copy2(p,backup/p.name)
for image in m.IMAGES:
 initrd=work/('nouveau-initramfs.img' if image.name=='apx-nouveau-recovery-v1.efi' else 'initramfs.img')
 cmdline=work/(image.stem+'.cmdline');output=backup/('repaired-'+image.name)
 m.run('ukify','--config=/etc/kernel/uki.conf','build','--linux=/boot/vmlinuz-linux','--initrd='+str(initrd),'--cmdline=@'+str(cmdline),'--uname='+os.uname().release,'--output='+str(output))
 m.run('sbverify','--cert','/etc/kernel/secure-boot-certificate.pem',str(output))
 before=hashlib.sha256(output.read_bytes()).hexdigest()
 with tempfile.TemporaryDirectory(dir=backup) as d:
  actual=m.extract(output,'.cmdline',Path(d)/'cmdline').decode().strip()
  assert actual==cmdline.read_text().strip()
 assert hashlib.sha256(output.read_bytes()).hexdigest()==before
 m.run('sbverify','--cert','/etc/kernel/secure-boot-certificate.pem',str(output))
 m.atomic(work/image.name,output.read_bytes())
m.install_boot(work)
manifest=Path('/usr/share/apx/native-v3-enabled.json');release=json.loads(manifest.read_bytes())
installed=Path('/usr/lib/apx/apx-reclaim-windows-linux-v3.py')
shutil.copy2(installed,backup/installed.name);shutil.copy2(manifest,backup/manifest.name)
# Renew only the reviewed helper entry; other entries must still match.
for name,expected in release['files'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected,name
m.atomic(installed,path.read_bytes(),installed.stat().st_mode&0o777)
release['files'][str(installed)]=hashlib.sha256(installed.read_bytes()).hexdigest()
m.atomic(manifest,json.dumps(release,sort_keys=True).encode(),0o400)
print(json.dumps({'backup':str(backup),'all_three_installed_signatures':'verified','extract_preserves_signed_image':True}))
