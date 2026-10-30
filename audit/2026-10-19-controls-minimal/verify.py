import subprocess,json,time
from pathlib import Path
runner=['python','audit/2026-10-16-lucide-bar/session-command.py']
def cmd(*a):return subprocess.check_output(runner+list(a),text=True)
def ipc(name):return cmd('quickshell','-c','apx','ipc','call','host',name)
def key(k):cmd('hyprctl','eval','hl.dispatch(hl.dsp.send_shortcut({mods="",key="'+k+'"}))')
a=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/a['name']/'home/apx';out=Path('audit/2026-10-19-controls-minimal');results={}
def capture(name):
 time.sleep(.6);s=json.loads(ipc('popupStatus'));assert s['visible'];assert not s['animation_running'];p=home/'.cache/apx-controls-minimal.png'
 cmd('grim','-g',f"{round(s['visual_x'])},50 {min(350,1280-round(s['visual_x']))}x650",'/home/apx/.cache/apx-controls-minimal.png');(out/(name+'.png')).write_bytes(p.read_bytes());p.unlink();results[name]={k:s[k] for k in ['visible','displayed_controls','keyboard_items']}
for action,name in [('openBluetoothControls','bluetooth'),('openVolumeControls','sound'),('openMicrophoneControls','microphone'),('openBrightnessControls','brightness'),('openMoreControls','more')]:
 ipc(action);capture(name);key('Escape');time.sleep(.25)
ipc('openMoreControls');time.sleep(.5)
key('Tab');key('Tab');key('Return');capture('personalization')
key('Tab');key('Tab');key('Return');capture('personalization-section')
key('Escape');(out/'validation.json').write_text(json.dumps(results,indent=2)+'\n');print('Captured and verified',list(results))
