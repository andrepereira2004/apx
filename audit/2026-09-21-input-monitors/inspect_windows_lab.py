import socket,json,subprocess
from pathlib import Path
lab=Path(__file__).resolve().parent/'windows-lab'
s=socket.socket(socket.AF_UNIX);s.connect(str(lab/'qmp.sock'));f=s.makefile('rwb');f.readline()
def q(name):
 f.write(json.dumps(dict(execute=name)).encode()+b'\n');f.flush()
 while True:
  value=json.loads(f.readline())
  if 'return' in value:return value
q('qmp_capabilities');q('stop')
try:subprocess.run(['cp','--reflink=always',str(lab/'disk.raw'),str(lab/'inspect.raw')],check=True)
finally:q('cont')
loop=subprocess.check_output(['losetup','-r','-f','--show','-P',str(lab/'inspect.raw')],text=True).strip();mount=lab/'inspect-media';mount.mkdir(exist_ok=True)
try:
 subprocess.run(['mount','-o','ro',loop+'p4',str(mount)],check=True)
 try:
  for p in (mount/'APX/Native').rglob('*'):
   if p.is_file():
    print(p.relative_to(mount),p.stat().st_size)
    if 'status' in p.name or 'log-v3' in p.name:print(p.read_text(errors='replace')[-4000:])
 finally:subprocess.run(['umount',str(mount)],check=True)
 subprocess.run(['ntfsls','-f',loop+'p5'],check=False)
finally:
 subprocess.run(['losetup','-d',loop],check=True);(lab/'inspect.raw').unlink()
