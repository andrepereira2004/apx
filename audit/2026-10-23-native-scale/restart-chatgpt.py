from pathlib import Path
import glob,json,os,signal,socket,subprocess,time
AUDIT=Path(__file__).parent
OLD=342310
BASE=['/usr/bin/nsenter','-t','4246','-m','-U','-p','-r','-w','--','/usr/bin/runuser','-u','apx','--','/usr/bin/env','HOME=/home/apx','PATH=/usr/bin','XDG_RUNTIME_DIR=/run/apx/session-1000','WAYLAND_DISPLAY=wayland-1','XDG_SESSION_TYPE=wayland','DBUS_SESSION_BUS_ADDRESS=unix:path=/run/apx/session-1000/bus']
def query(command):
    here=os.getcwd()
    try:
        os.chdir(glob.glob('/proc/4246/root/run/apx/session-1000/hypr/*')[0])
        client=socket.socket(socket.AF_UNIX);client.settimeout(3);client.connect('.socket.sock');client.send(command.encode());data=b''
        while chunk:=client.recv(65536):data+=chunk
        client.close();return json.loads(data)
    finally:os.chdir(here)
time.sleep(3)
try:
    if Path(f'/proc/{OLD}/comm').exists():
        assert Path(f'/proc/{OLD}/comm').read_text().strip()=='ChatGPT'
        os.kill(OLD,signal.SIGTERM)
    for _ in range(100):
        if not Path(f'/proc/{OLD}/stat').exists() or Path(f'/proc/{OLD}/stat').read_text().split()[2]=='Z':break
        time.sleep(.1)
    else:raise RuntimeError('Old ChatGPT process did not exit')
    subprocess.run(BASE+['/usr/bin/gtk-launch','chatgpt'],check=True,timeout=10)
    for _ in range(100):
        windows=[c for c in query('j/clients') if c['class'].lower()=='chatgpt']
        if windows:
            result={'old_host_pid':OLD,'clients':[{k:c.get(k) for k in ['class','pid','xwayland','size']} for c in windows], 'monitors':[{k:m[k] for k in ['width','height','scale']} for m in query('j/monitors')]}
            (AUDIT/'restarted-main-profile.json').write_text(json.dumps(result,indent=2)+'\n')
            if any(c['xwayland'] for c in windows):raise RuntimeError('ChatGPT reopened in X11')
            print('Verified: main signed-in profile is native Wayland',flush=True)
            break
        time.sleep(.2)
    else:raise RuntimeError('ChatGPT window did not appear')
except Exception as error:
    (AUDIT/'restart-error.txt').write_text(str(error)+'\n')
    raise
