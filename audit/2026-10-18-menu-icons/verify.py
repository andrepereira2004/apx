import subprocess,json,time
from pathlib import Path
runner=['python','audit/2026-10-16-lucide-bar/session-command.py']
def cmd(*a):return subprocess.check_output(runner+list(a),text=True)
def ipc(name):return cmd('quickshell','-c','apx','ipc','call','host',name)
def state():return json.loads(ipc('popupStatus'))
def esc():return cmd('hyprctl','eval','hl.dispatch(hl.dsp.send_shortcut({mods="",key="Escape"}))')
assert not state()['visible'] and not state()['launcher_running']
results={}
for toggle in ['toggleCalendar','toggleControls','toggleBattery','openMedia']:
 ipc(toggle);time.sleep(.6);assert state()['visible'];esc();time.sleep(.5)
 results[toggle]=not state()['visible'];assert results[toggle]
ipc('openApplications');time.sleep(.6);assert state()['launcher_running'];ipc('openApplications');time.sleep(.3);assert not state()['launcher_running'];results['rofi_toggle']=True
ipc('openApplications');time.sleep(.6);esc();time.sleep(.4);assert not state()['launcher_running'];results['rofi_escape']=True
Path('audit/2026-10-18-menu-icons/results.json').write_text(json.dumps(results,indent=2)+'\n');print(results)
