"""Capture a narrow screen strip during a disposable, self-closing terminal launch."""
from pathlib import Path
import socket,json,time,os,subprocess,struct,zlib,sys
out=Path(__file__).resolve().parent/'timing-capture';out.mkdir(exist_ok=True)
label=sys.argv[1]
p=next(Path('/proc/3267/root/run/apx/session-1000/hypr').glob('*/.socket.sock'));os.chdir(p.parent)
def query(q):
 with socket.socket(socket.AF_UNIX) as s:
  s.settimeout(4);s.connect('.socket.sock');s.sendall(q.encode());data=b''
  while d:=s.recv(65536):data+=d
  return data.decode()
runtime=Path('/proc/3267/root/run/apx/session-1000');display=next(x.name for x in runtime.glob('wayland-*') if x.is_socket())
cmd=['nsenter','-t','3267','-m','-r','-w','--','env','XDG_RUNTIME_DIR=/run/apx/session-1000','WAYLAND_DISPLAY='+display,'grim','-s','1','-g','0,430 1536x8','-t','ppm','-']
if label=='explicit':
 assert query('eval hl.animation({leaf="windowsMove",enabled=true,speed=4.79,bezier="easeOutQuint"})').strip()=='ok'
print(query('eval hl.exec_cmd("kitty --class apx-motion-probe --title APX-MOTION-PROBE --override background=#ff0000 /bin/sleep 2")'))
t=time.monotonic();strips=[]
try:
 for n in range(32):
  r=subprocess.run(cmd,capture_output=True,check=True);parts=r.stdout.split(b'\n',3)
  assert parts[0]==b'P6' and parts[1]==b'1536 8',r.stdout[:80]
  strips.append((round((time.monotonic()-t)*1000),parts[3]))
finally:
 if label=='explicit':print('Restore:',query('reload config-only'))
raw=b''
for ms,pixels in strips:
 for y in range(8):raw+=b'\x00'+pixels[y*1536*3:(y+1)*1536*3]
 for y in range(4):raw+=b'\x00'+bytes([255])*1536*3
def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data))
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',1536,len(strips)*12,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
(out/(label+'.png')).write_bytes(png);(out/(label+'.json')).write_text(json.dumps([t for t,_ in strips]))
print(label,[t for t,_ in strips])
