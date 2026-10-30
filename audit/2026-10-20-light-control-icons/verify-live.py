import json, subprocess, time
from pathlib import Path
runner=['python','audit/2026-10-16-lucide-bar/session-command.py']
def cmd(*args):return subprocess.check_output(runner+list(args),text=True)
def ipc(name):return cmd('quickshell','-c','apx','ipc','call','host',name)
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
home=Path('/var/lib/apx/environments')/state['name']/'home/apx'
out=Path('audit/2026-10-20-light-control-icons');results={}
for action,name in [('openBrightnessControls','sound-brightness'),('openConnectivityControls','connectivity'),('openWifiControls','wifi')]:
    ipc(action);time.sleep(1)
    status=json.loads(ipc('popupStatus'));assert status['visible'] and not status['animation_running']
    target='/home/apx/.cache/apx-light-icons-live.png'
    cmd('grim','-g',f"{round(status['visual_x'])},65 340x{round(status['settled_height'])}",target)
    (out/(name+'.png')).write_bytes((home/'.cache/apx-light-icons-live.png').read_bytes())
    (home/'.cache/apx-light-icons-live.png').unlink()
    results[name]=status
    cmd('hyprctl','eval','hl.dispatch(hl.dsp.send_shortcut({mods="",key="Escape"}))');time.sleep(.3)
(out/'live-validation.json').write_text(json.dumps(results,indent=2)+'\n')
print('Live Wi-Fi and more options verified; no network or settings changed.')
