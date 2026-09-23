from pathlib import Path
import json,socket,sys
lab=Path(__file__).resolve().parent/'windows-lab'
s=socket.socket(socket.AF_UNIX);s.settimeout(5);s.connect(str(lab/'qmp.sock'));f=s.makefile('rwb');f.readline()
def command(name,arguments=None):
 f.write(json.dumps(dict(execute=name,arguments=arguments or {})).encode()+b'\n');f.flush()
 while True:
  value=json.loads(f.readline())
  if 'return' in value or 'error' in value:return value
command('qmp_capabilities')
if len(sys.argv)>1 and sys.argv[1]=='screenshot':print(command('screendump',dict(filename=str(lab/'screen.ppm'))))
elif len(sys.argv)>1 and sys.argv[1]=='key':print(command('send-key',{'keys':[dict(type='qcode',data=k) for k in sys.argv[2].split('-')],'hold-time':100}))
else:print(command('query-status'))

if len(sys.argv)>1 and sys.argv[1]=='screenshot':
 import zlib,struct
 p=lab/'screen.ppm';magic,wh,maxv,pixels=p.read_bytes().split(b'\n',3);w,h=map(int,wh.split())
 assert magic==b'P6' and maxv==b'255'
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d))
 p.with_suffix('.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+pixels[i*w*3:(i+1)*w*3] for i in range(h))))+chunk(b'IEND',b''))
