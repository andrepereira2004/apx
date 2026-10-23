from pathlib import Path
import subprocess,time,json
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent
runner=['python',str(r/'audit/2026-10-16-lucide-bar/session-command.py')]
def cmd(*args):return subprocess.check_output(runner+list(args),text=True)
def ipc(name):return cmd('quickshell','-c','apx','ipc','call','host',name)
def status():return json.loads(ipc('popupStatus'))
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());h=Path('/var/lib/apx/environments')/state['name']/'home/apx'
def capture(name):
 s=status();cmd('grim','-g',f"{round(s['visual_x'])},{round(s['panel_y'])} {round(s['visual_width'])}x{round(s['visual_height'])}",'/home/apx/.cache/apx-controls-refine.png')
 p=h/'.cache/apx-controls-refine.png';(a/name).write_bytes(p.read_bytes());p.unlink()
if status()['visible']:ipc('toggleControls');time.sleep(.4)
results={}
ipc('openControls');t=time.monotonic();time.sleep(.6)
s=status();assert s['ghost_visible'];capture('dashboard.png');results['initial']=s
while time.monotonic()-t<3.5:time.sleep(.1)
assert not status()['ghost_visible'];results['three_second_expiry']=True
ipc('toggleControls');time.sleep(.4);ipc('openControls');time.sleep(.4)
assert status()['ghost_visible'];ipc('toggleControls');time.sleep(.1)
assert not status()['ghost_visible'];results['close_hides_greeting']=True
time.sleep(.4);ipc('openBrightnessControls');time.sleep(.6)
s=status();assert s['displayed_controls']['controlsBrightnessOpen'] and not s['displayed_controls']['controlsAudioOpen'],s
results['brightness']=s;capture('brightness.png')
ipc('openVolumeControls');time.sleep(.5)
s=status();assert s['displayed_controls']['controlsAudioOpen'] and not s['displayed_controls']['controlsBrightnessOpen'],s
results['audio_navigation']=True
ipc('toggleControls');time.sleep(.4)
results['configerrors']=cmd('hyprctl','configerrors').strip();assert not results['configerrors']
(a/'live-results.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS: greeting expires at 3 seconds and hides on close; brightness/audio menus open independently')
