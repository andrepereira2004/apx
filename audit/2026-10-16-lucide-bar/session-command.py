#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
marker=Path('/run/apx/active-graphical-environment-v1.json')
if not marker.exists():marker=Path('/run/apx/official-hub-graphical-v1.json')
state=json.loads(marker.read_text());pid=int(state['pid'])
env={}
for entry in Path(f'/proc/{pid}/environ').read_bytes().split(b'\0'):
 k,_,v=entry.partition(b'=')
 if k in (b'XDG_RUNTIME_DIR',b'DBUS_SESSION_BUS_ADDRESS',b'HYPRLAND_INSTANCE_SIGNATURE',b'WAYLAND_DISPLAY'):env[k.decode()]=v.decode()
base=Path(f'/proc/{pid}/root')/env['XDG_RUNTIME_DIR'].lstrip('/')
if 'WAYLAND_DISPLAY' not in env:env['WAYLAND_DISPLAY']=next(p.name for p in base.glob('wayland-*') if p.is_socket())
if 'HYPRLAND_INSTANCE_SIGNATURE' not in env:env['HYPRLAND_INSTANCE_SIGNATURE']=next(p.name for p in (base/'hypr').iterdir() if p.is_dir())
cmd=['/usr/bin/nsenter','-t',str(pid),'-m','-U','-p','-n','--','/usr/bin/setpriv','--reuid=1000','--regid=1000','--init-groups','/usr/bin/env','-i','HOME=/home/apx','USER=apx','PATH=/home/apx/.local/bin:/usr/bin','XDG_CURRENT_DESKTOP=Hyprland']+[k+'='+v for k,v in env.items()]+sys.argv[1:]
sys.exit(subprocess.run(cmd,cwd='/').returncode)
