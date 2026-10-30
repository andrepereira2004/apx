import json, subprocess, time, os
from pathlib import Path
out=Path(__file__).resolve().parent
pid=json.loads(Path('/run/apx/official-hub-graphical-v1.json').read_text())['pid']
root=Path(f'/proc/{pid}/root');runtime=root/'run/apx/session-1000'
stage=root/'run/apx/unplug-check';stage.mkdir(exist_ok=True);stage.chmod(0o755)
(stage/'hyprland.lua').write_text('hl.bind("SUPER + F12",hl.dsp.no_op())\n');(stage/'hyprland.lua').chmod(0o644)
before={p.name for p in (runtime/'hypr').iterdir()}
prefix=['nsenter','-t',str(pid),'-U','-m','-p','-n','--','setpriv','--reuid=1000','--regid=1000','--clear-groups','env','HOME=/home/apx','XDG_RUNTIME_DIR=/run/apx/session-1000']
log=(out/'unplug-hyprland.log').open('w')
proc=subprocess.Popen(prefix+['WAYLAND_DISPLAY=wayland-1','AQ_BACKEND=wayland','timeout','35','Hyprland','-c','/run/apx/unplug-check/hyprland.lua'],stdout=log,stderr=log)
apps=[]
try:
 for i in range(100):
  new=[p.name for p in (runtime/'hypr').iterdir() if p.name not in before and (p/'.socket.sock').is_socket()]
  if len(new)==1:break
  time.sleep(.05)
 assert len(new)==1
 prefix+=['WAYLAND_DISPLAY=wayland-2','HYPRLAND_INSTANCE_SIGNATURE='+new[0]]
 def ctl(*args):return subprocess.run(prefix+['hyprctl',*args],check=True,capture_output=True,text=True,timeout=4).stdout
 def j(q):return json.loads(ctl('-j',q))
 for i in range(2):ctl('output','create','headless')
 ctl('eval','hl.monitor({output="WAYLAND-1",disabled=true})')
 ctl('eval','hl.monitor({output="",mode="1280x720",position="auto-right",scale=1})')
 time.sleep(.2)
 for index,monitor in enumerate(['HEADLESS-1','HEADLESS-2']):
  ctl('eval','hl.dispatch(hl.dsp.focus({monitor="'+monitor+'"}))')
  apps.append(subprocess.Popen(prefix+['kitty','--class','apx-unplug-'+str(index),'sh','-c','sleep 25'],stdout=log,stderr=log))
  for _ in range(100):
   if any(c['class']=='apx-unplug-'+str(index) for c in j('clients')):break
   time.sleep(.05)
 initial=j('clients');assert len(initial)==2,initial
 ctl('output','remove','HEADLESS-2');time.sleep(.5)
 monitors=j('monitors');clients=j('clients');workspaces=j('workspaces')
 assert len(monitors)==1
 assert {c['address'] for c in clients}=={c['address'] for c in initial}
 assert all(c['monitor']==monitors[0]['id'] for c in clients),clients
 assert all(w['monitor']==monitors[0]['name'] for w in workspaces),workspaces
 (out/'windows-on-monitor-removal.json').write_text(json.dumps(dict(before=initial,after=clients,monitors=monitors,workspaces=workspaces),indent=2))
 print('PASS: both windows and all workspaces moved to the remaining monitor')
finally:
 for p in apps:p.terminate()
 if 'ctl' in locals():
  try:ctl('dispatch','exit')
  except Exception:pass
 proc.terminate()
