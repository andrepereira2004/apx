"""Record a regular, self-closing Kitty window beside the current application."""
from pathlib import Path
import socket,json,time,os,subprocess,sys
out=Path(__file__).resolve().parent/('normal-recording-'+sys.argv[1] if len(sys.argv)>1 else 'normal-recording');out.mkdir(exist_ok=True)
p=next(Path('/proc/3267/root/run/apx/session-1000/hypr').glob('*/.socket.sock'));os.chdir(p.parent)
def query(q):
 with socket.socket(socket.AF_UNIX) as s:
  s.settimeout(4);s.connect('.socket.sock');s.sendall(q.encode());data=b''
  while d:=s.recv(65536):data+=d
  return data.decode()
prefix=['nsenter','-t','3267','-m','-r','-w','--','env','XDG_RUNTIME_DIR=/run/apx/session-1000']
display=next(x.name for x in Path('/proc/3267/root/run/apx/session-1000').glob('wayland-*') if x.is_socket())
grim=prefix+['WAYLAND_DISPLAY='+display,'grim','-s','0.6','-t','ppm','-']
old=json.loads(query('j/activewindow'));workspace=json.loads(query('j/activeworkspace'));assert old and not old['floating']
frames=[];metadata=[]
frames.append(subprocess.check_output(grim,timeout=3))
assert query('eval hl.exec_cmd("kitty --title Terminal /bin/sleep 2")').strip()=='ok'
t=time.monotonic()
while time.monotonic()-t<3.2:
 start=time.monotonic();frame=subprocess.check_output(grim,timeout=3);elapsed=time.monotonic()-t
 frames.append(frame);metadata.append({'frame':len(frames)-1,'ms':round(elapsed*1000),'clients':json.loads(query('j/clients'))})
 if len(frames)>180:break
(out/'timing.json').write_text(json.dumps({'initial':old,'workspace':workspace,'samples':metadata},indent=2)+'\n')
# Encode a slow-motion clip so both window edges can be inspected repeatedly.
args=prefix+['ffmpeg','-v','error','-f','image2pipe','-vcodec','ppm','-framerate','12','-i','pipe:0','-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2','-c:v','libx264','-pix_fmt','yuv420p','-movflags','frag_keyframe+empty_moov','-f','mp4','pipe:1']
with (out/'normal-windows-slow.mp4').open('wb') as video:
 subprocess.run(args,input=b''.join(frames),stdout=video,check=True,timeout=20)
# An opening contact sheet makes the captured movement directly inspectable.
args=prefix+['ffmpeg','-v','error','-f','image2pipe','-vcodec','ppm','-i','pipe:0','-vf','scale=384:-1,tile=6x5','-frames:v','1','-f','image2','-vcodec','png','pipe:1']
with (out/'opening-sheet.png').open('wb') as picture:
 subprocess.run(args,input=b''.join(frames[:30]),stdout=picture,check=True,timeout=20)
print('Frames:',len(frames),'first frame ms:',metadata[0]['ms'],'last:',metadata[-1]['ms'])
print('Opening times:',[r['ms'] for r in metadata[:29]])
print('Workspace preserved:',json.loads(query('j/activeworkspace'))['id']==workspace['id'])
