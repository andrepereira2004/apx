"""Run an isolated, time-limited headless compositor with official classic motion."""
from pathlib import Path
import subprocess,time,os,json,signal
out=Path(__file__).resolve().parent
runtime=Path('/proc/3267/root/run/apx/session-1000');cfg=runtime/'apx-motion-clean.lua'
assert not cfg.exists()
text=(out.parent/'2026-10-26-window-reflow/installed-default.lua').read_text().replace('spring = "easy"','bezier = "easeOutQuint"')
text+='\nhl.monitor({output="",mode="1280x720@60",position="0x0",scale=1})\n'
cfg.write_text(text);os.chown(cfg,98108392,98108392)
prefix=['nsenter','-t','3267','-U','-m','-p','-n','--','setpriv','--reuid=1000','--regid=1000','--clear-groups','env','HOME=/home/apx','XDG_RUNTIME_DIR=/run/apx/session-1000']
displays_before={p.name for p in runtime.glob('wayland-*') if p.is_socket()}
before={p.name for p in (runtime/'hypr').iterdir()};log=open(out/'clean-session.log','w')
proc=subprocess.Popen(prefix+['AQ_BACKEND=wayland','WAYLAND_DISPLAY='+next(iter(displays_before)),'timeout','15','Hyprland','-c','/run/apx/session-1000/apx-motion-clean.lua'],stdout=log,stderr=log,start_new_session=True)
try:
 for _ in range(80):
  new=[p for p in (runtime/'hypr').iterdir() if p.name not in before and (p/'.socket.sock').is_socket()]
  if len(new)==1:break
  if proc.poll() is not None:break
  time.sleep(.05)
 if len(new)!=1:raise RuntimeError('isolated compositor did not start; inspect clean-session.log')
 sig=new[0].name
 ctl=prefix+['HYPRLAND_INSTANCE_SIGNATURE='+sig,'hyprctl']
 def query(*args):return subprocess.check_output(ctl+list(args),text=True,timeout=4)
 print('errors',query('configerrors'))
 print(query('output','create','headless'))
 print(query('eval','hl.monitor({output="WAYLAND-1",disabled=true});hl.monitor({output="HEADLESS-1",mode="1280x720@60",position="0x0",scale=1})'))
 print('monitors',query('monitors','-j'))
 (out/'clean-monitors.json').write_text(query('monitors','-j'))
 (out/'clean-animations.json').write_text(query('animations','-j'))
 displays_after={p.name for p in runtime.glob('wayland-*') if p.is_socket()}
 display=next(iter(displays_after-displays_before))
 query('eval','hl.exec_cmd("kitty --class apx-clean-blue --override background=#0000ff --override background_opacity=1 /bin/sleep 6")')
 for _ in range(80):
  if any(w['class']=='apx-clean-blue' for w in json.loads(query('clients','-j'))):break
  time.sleep(.025)
 else:raise RuntimeError('blue probe missing')
 time.sleep(.65)
 def capture():
  args=prefix+['WAYLAND_DISPLAY='+display,'grim','-s','1','-g','0,300 1280x8','-t','ppm','-']
  r=subprocess.run(args,check=True,capture_output=True,timeout=3);head=r.stdout.split(b'\n',3);w,h=map(int,head[1].split());data=head[3];boxes={}
  for color in ['blue','red']:
   xs=[]
   for x in range(w):
    i=(w*3+x)*3;a,b,c=data[i:i+3]
    if (c>180 and a<25 and b<25) if color=='blue' else (a>180 and b<25 and c<25):xs.append(x)
   boxes[color]=[min(xs),max(xs)] if xs else None
  return boxes
 rows=[{'ms':0,'boxes':capture()}]
 query('eval','hl.exec_cmd("kitty --class apx-clean-red --override background=#ff0000 --override background_opacity=1 /bin/sleep 3")')
 t=time.monotonic()
 while time.monotonic()-t<1.2:rows.append({'ms':round((time.monotonic()-t)*1000),'boxes':capture()})
 (out/'clean-colored.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(rows)
 print('headless comparison finished')
finally:
 try:os.killpg(proc.pid,signal.SIGTERM)
 except ProcessLookupError:pass
 try:proc.wait(timeout=3)
 except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
 cfg.unlink(missing_ok=True)
