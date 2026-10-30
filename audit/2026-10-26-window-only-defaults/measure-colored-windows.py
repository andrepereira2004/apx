"""Measure rendered disposable window bounds; discard screenshots and app contents."""
from pathlib import Path
import socket,json,time,os,subprocess,sys
out=Path(__file__).resolve().parent
p=next(Path('/proc/3267/root/run/apx/session-1000/hypr').glob('*/.socket.sock'));os.chdir(p.parent)
def query(q):
 with socket.socket(socket.AF_UNIX) as s:
  s.settimeout(4);s.connect('.socket.sock');s.sendall(q.encode());data=b''
  while d:=s.recv(65536):data+=d
  return data.decode()
runtime=Path('/proc/3267/root/run/apx/session-1000');display=next(x.name for x in runtime.glob('wayland-*') if x.is_socket())
cmd=['nsenter','-t','3267','-m','-r','-w','--','env','XDG_RUNTIME_DIR=/run/apx/session-1000','WAYLAND_DISPLAY='+display,'grim','-g','100,0 8x864','-t','ppm','-']
label=sys.argv[1]
def capture():
 r=subprocess.run(cmd,capture_output=True,check=True);head=r.stdout.split(b'\n',3);w,h=map(int,head[1].split());data=head[3];boxes={}
 for color in ['blue','red']:
  xs=[];ys=[]
  for y in range(20,h-10):
   for x in range(1,w-1,2):
    i=(y*w+x)*3;a,b,c=data[i:i+3]
    ok=(c>180 and a<25 and b<25) if color=='blue' else (a>180 and b<25 and c<25)
    if ok:xs.append(x);ys.append(y)
  boxes[color]=[min(xs),min(ys),max(xs),max(ys)] if xs else None
 return boxes
assert not any(w['class'].startswith('apx-motion-') for w in json.loads(query('j/clients')))
ws=json.loads(query('j/activeworkspace'))['id']
print(query('eval hl.exec_cmd("kitty --class apx-motion-blue --override background=#0000ff --override background_opacity=1 /bin/sleep 5")'))
for n in range(50):
 if any(w['class']=='apx-motion-blue' for w in json.loads(query('j/clients'))):break
 time.sleep(.02)
else:raise RuntimeError('probe did not open')
time.sleep(.65)
if label=='explicit':assert query('eval hl.animation({leaf="windowsMove",enabled=true,speed=4.79,bezier="easeOutQuint"})').strip()=='ok'
rows=[{'ms':0,'boxes':capture()}]
print(query('eval hl.exec_cmd("kitty --class apx-motion-red --override background=#ff0000 --override background_opacity=1 /bin/sleep 2")'))
t=time.monotonic()
try:
 while time.monotonic()-t<1.2:
  start=time.monotonic();boxes=capture();rows.append({'ms':round((time.monotonic()-t)*1000),'boxes':boxes})
finally:
 if label=='explicit':print(query('reload config-only'))
endws=json.loads(query('j/activeworkspace'))['id'];result={'workspace':ws,'workspace_end':endws,'rows':rows};(out/('colored-'+label+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
