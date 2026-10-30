from pathlib import Path
import glob,json,os,signal,socket,subprocess,time
AUDIT=Path(__file__).parent
BASE=['nsenter','-t','4246','-m','-U','-p','-r','-w','--','runuser','-u','apx','--','env','HOME=/home/apx','PATH=/usr/bin','XDG_RUNTIME_DIR=/run/apx/session-1000','WAYLAND_DISPLAY=wayland-1','MOZ_ENABLE_WAYLAND=1','DBUS_SESSION_BUS_ADDRESS=unix:path=/run/apx/session-1000/bus']
def query(command):
    here=os.getcwd()
    try:
        os.chdir(glob.glob('/proc/4246/root/run/apx/session-1000/hypr/*')[0])
        s=socket.socket(socket.AF_UNIX);s.settimeout(3);s.connect('.socket.sock');s.send(command.encode());data=b''
        while chunk:=s.recv(65536): data+=chunk
        s.close()
        try:return json.loads(data)
        except json.JSONDecodeError:return data.decode()
    finally:os.chdir(here)
windows=[c for c in query('j/clients') if 'thunderbird' in c['class'].lower()]
window={'workspace':{'id':6}}
container_pid=None
if windows:
    assert len(windows)==1,'Expected one main window; refusing ambiguous restart'
    window=windows[0]
    assert not any(word in window.get('title','').lower() for word in ['write:','escrever:','compose','redigir:']), 'Compose window present'
    container_pid=window['pid'];host_pid=None
    for path in Path('/proc').glob('[0-9]*/status'):
        try:
            text=path.read_text()
            if '\nName:\t' in '\n'+text and (path.parent/'comm').read_text().strip()=='thunderbird':
                nspid=next(line for line in text.splitlines() if line.startswith('NSpid:')).split()[1:]
                if len(nspid)>1 and int(nspid[-1])==container_pid:host_pid=int(path.parent.name);break
        except (OSError,StopIteration):pass
    assert host_pid
    os.kill(host_pid,signal.SIGTERM)
    for _ in range(100):
        status=Path(f'/proc/{host_pid}/stat')
        if not status.exists() or status.read_text().split()[2]=='Z':break
        time.sleep(.1)
    else:raise RuntimeError('Thunderbird has not finished saving; no forced close')
subprocess.run(BASE+['gtk-launch','org.mozilla.Thunderbird'],check=True,timeout=15)
for _ in range(150):
    clients=[c for c in query('j/clients') if 'thunderbird' in c['class'].lower()]
    if clients:
        for c in clients:
            if c['workspace']['id'] != window['workspace']['id']:
                query('dispatch hl.dsp.window.move({workspace='+str(window['workspace']['id'])+',window='+json.dumps('address:'+c['address'])+',silent=true})')
        result={'previous_container_pid':container_pid,'clients':[{k:c[k] for k in ['class','pid','size','xwayland']} for c in clients], 'profile_css_matches':True}
        (AUDIT/'live-verification.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result));break
    time.sleep(.2)
else:raise RuntimeError('Thunderbird did not reopen')
