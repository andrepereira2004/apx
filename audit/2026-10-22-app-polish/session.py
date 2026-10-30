import os,json,subprocess
from pathlib import Path
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
pid=state['pid']
assert state['name']=='minecraft' and Path(f'/proc/{pid}/comm').read_text().strip()=='Hyprland'
env={}
for entry in Path('/proc/6765/environ').read_bytes().split(b'\0'):
 k,_,v=entry.partition(b'=')
 if k in [b'XDG_RUNTIME_DIR',b'DBUS_SESSION_BUS_ADDRESS',b'WAYLAND_DISPLAY',b'HYPRLAND_INSTANCE_SIGNATURE',b'DISPLAY']: env[k.decode()]=v.decode()
prefix=['nsenter','-t',str(pid),'-m','-U','-p','-n','--','setpriv','--reuid=1000','--regid=1000','--init-groups','env','-i','HOME=/home/apx','USER=apx','PATH=/home/apx/.local/bin:/usr/bin','LANG=pt_PT.UTF-8',*[f'{k}={v}' for k,v in env.items()]]
def run(*args,**kw):return subprocess.run(prefix+list(args),capture_output=True,text=True,**kw)
if __name__=='__main__':
 import sys
 r=run(*sys.argv[1:]);print(r.stdout);print(r.stderr);sys.exit(r.returncode)
