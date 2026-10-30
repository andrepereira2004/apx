from pathlib import Path
import subprocess,json
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent
runner=['python',str(r/'audit/2026-10-16-lucide-bar/session-command.py')]
program='''import subprocess,json,time
base=['quickshell','-c','apx','ipc','call','host']
def ipc(name):return subprocess.check_output(base+[name],text=True)
def state():return json.loads(ipc('popupStatus'))
assert not state()['visible']
ipc('openControls');frames=[]
for i in range(24):
 s=state();frames.append(s);time.sleep(.012)
assert any(0<s['island_progress']<1 for s in frames)
settled=state()
assert settled['island_progress']==1
for s in frames:
 assert abs(s['visual_height']-settled['visual_height'])<.1,s
 assert abs(s['visual_width']-settled['visual_width'])<.1,s
assert any(0<s['popup_opacity']<1 for s in frames)
ipc('openMoreControls');time.sleep(.45)
assert state()['displayed_controls']['controlsMoreOpen']
ipc('openControls');time.sleep(.45)
assert not state()['displayed_controls']['controlsMoreOpen']
ipc('toggleControls');time.sleep(.4);assert not state()['visible']
ipc('openCalendar');time.sleep(.4);assert state()['visible'] and state()['kind']=='calendar'
ipc('toggleCalendar');time.sleep(.4)
print(json.dumps(frames))
'''
result=subprocess.check_output(runner+['python','-c',program],text=True);(a/'live-frames.json').write_text(result)
print('PASS: full dashboard dimensions throughout entrance, intermediate fade, submenus and calendar open/close')
