#!/usr/bin/env python3
"""Build pinned native ArtCraft packages and install only in the Faculdade pilot."""
from pathlib import Path
import urllib.request,json,hashlib,tarfile,shutil,subprocess,os
assert Path('/etc/hostname').read_text().strip() == 'apx-host'
assert Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() == 'e83e08ac-a723-11eb-80ef-38f3aba440bc'
leader=subprocess.check_output(['machinectl','show','apx-ge9b0898','-p','Leader','--value'],text=True).strip()
assert leader.isdigit()
base=Path('/var/lib/apx/backups/20261012-artcraft');base.mkdir(mode=0o700,exist_ok=True)
art=Path('/var/lib/apx/package-artifacts');art.mkdir(exist_ok=True)
for name,version in [('gridcraft','0.6.1'),('wordcraft','0.6.1'),('deckcraft','0.5.0')]:
 # Preserve the locally tested asynchronous-Open build rather than replacing it
 # with the upstream binary that blocks the desktop event loop in its picker.
 manifest=art/f'{name}-v1.json'
 if name=='gridcraft' and manifest.exists():
  record=json.loads(manifest.read_text())
  if record.get('apx_patch')=='async-open-v1':
   filename=record['filename'];assert Path(filename).name==filename
   artifact=art/filename;assert hashlib.sha256(artifact.read_bytes()).hexdigest()==record['sha256']
   root=Path('/var/lib/apx/environments/faculdade/root');cached=root/'var/cache/pacman/pkg'/filename
   shutil.copy2(artifact,cached)
   subprocess.run(['nsenter','-t',leader,'-m','-U','-n','-p','--','pacman','-U','--noconfirm','/var/cache/pacman/pkg/'+filename],check=True)
   cached.unlink();print('gridcraft: installed pinned APX async Open build',flush=True);continue
 d=base/name;d.mkdir(exist_ok=True);f=f'{name}-{version}-linux-x86_64.tar.gz';url=f'https://github.com/storytold/{name}/releases/download/v{version}/'
 if name=='gridcraft':shutil.copy2('/var/lib/apx/backups/20261012-gridcraft-install/'+f,d/f)
 else:urllib.request.urlretrieve(url+f,d/f)
 urllib.request.urlretrieve(url+'SHA256SUMS.txt',d/'SHA256SUMS.txt')
 digest=hashlib.sha256((d/f).read_bytes()).hexdigest();assert any(l.split()[0]==digest and l.split()[-1].lstrip('*')==f for l in (d/'SHA256SUMS.txt').read_text().splitlines())
 with tarfile.open(d/f) as t:t.extractall(d/'unpack',filter='data')
 src=next((d/'unpack').iterdir());pkg=d/'package';(pkg/'usr').mkdir(parents=True,exist_ok=True)
 for sub in ['bin','share']:
  if (src/sub).exists():shutil.copytree(src/sub,pkg/'usr'/sub,dirs_exist_ok=True)
 for directory in [pkg,*[x for x in pkg.rglob('*') if x.is_dir()]]: os.chmod(directory,0o755)
 for file in [x for x in pkg.rglob('*') if x.is_file()]: os.chmod(file,0o755 if file.parent.name=='bin' else 0o644)
 # Upstream forces X11 for drag-and-drop; prefer crisp native Wayland at fractional scale.
 if name in {'wordcraft', 'deckcraft'}:
  desktop=pkg/'usr/share/applications'/f'ai.storyteller.{name}.desktop'
  desktop.write_text(desktop.read_text().replace(f'Exec={name} %F', f'Exec=env {name.upper()}_WAYLAND=1 {name} %F'))
 release=2 if name in {'wordcraft', 'deckcraft'} else 1
 size=sum(p.stat().st_size for p in pkg.rglob('*') if p.is_file())
 (pkg/'.PKGINFO').write_text(f'pkgname = {name}\npkgbase = {name}\npkgver = {version}-{release}\npkgdesc = Native ArtCraft {name} (official binary)\nurl = https://github.com/storytold/{name}\nbuilddate = 1791828000\npackager = APX physical pilot\nsize = {size}\narch = x86_64\nlicense = MIT\nlicense = Apache-2.0\ndepend = glibc\ndepend = gcc-libs\n')
 filename=f'{name}-{version}-{release}-x86_64.pkg.tar.zst';out=art/filename
 subprocess.run(['tar','--zstd','-cf',str(out),'-C',str(pkg),'.PKGINFO','usr'],check=True)
 record={'schema':1,'package':name,'filename':filename,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'upstream_archive_sha256':digest,'upstream_url':url+f}
 (art/f'{name}-v1.json').write_text(json.dumps(record,indent=2)+'\n');os.chmod(out,0o644);os.chmod(art/f'{name}-v1.json',0o644)
 root=Path('/var/lib/apx/environments/faculdade/root');shutil.copy2(out,root/'var/cache/pacman/pkg'/filename)
 subprocess.run(['nsenter','-t',leader,'-m','-U','-n','-p','--','pacman','-U','--noconfirm','/var/cache/pacman/pkg/'+filename],check=True);(root/'var/cache/pacman/pkg'/filename).unlink()
 print(name,version,digest,flush=True)
