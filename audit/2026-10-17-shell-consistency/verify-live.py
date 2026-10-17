from pathlib import Path
import json,subprocess,time
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
RUNNER=['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py')]
def cmd(*args):return subprocess.check_output(RUNNER+list(args),text=True)
def ipc(name):return cmd('quickshell','-c','apx','ipc','call','host',name)
def state():return json.loads(ipc('popupStatus'))
def wait(predicate):
 deadline=time.monotonic()+4
 while time.monotonic()<deadline:
  s=state()
  if predicate(s):return s
  time.sleep(.02)
 raise AssertionError(s)
def settled():return wait(lambda s:s['island_progress']==1 and s['content_opacity']==1 and not s['page_transition'])
def close():
 s=state()
 if s['visible']:
  ipc({'calendar':'toggleCalendar','controls':'toggleControls','media':'openMedia','battery':'toggleBattery','environments':'openEnvironments'}[s['kind']]);wait(lambda s:not s['visible'])
results={};assert not state()['visible'],'Owner menu open; do not interrupt'
active=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/active['name']/'home/apx'
def capture(name,s):
 p=home/'.cache'/('apx-consistency-'+name+'.png');assert not p.exists()
 try:
  cmd('grim','-g',f"{round(s['visual_x'])},{round(s['panel_y'])} {round(s['visual_width'])}x{min(round(s['visual_height']),655)}",'/home/apx/.cache/'+p.name)
  (OUT/(name+'.png')).write_bytes(p.read_bytes())
 finally:
  if p.exists():p.unlink()
def verify(name,s):
 assert s['panel_y']==65,(name,s)
 assert s['content_font']=='JetBrains Mono' and s['body_size']==12 and s['title_size']==14,(name,s)
 assert all(f.startswith('JetBrains Mono:') for f in s['visible_fonts']),(name,s['visible_fonts'])
 results[name]=s
try:
 ipc('openControls');s=settled();verify('controls',s);assert s['content_y']==0,s;capture('controls',s)
 old_height=s['visual_height']
 program = """import subprocess,json,time
base=['quickshell','-c','apx','ipc','call','host']
subprocess.run(base+['openMoreControls'],check=True,stdout=subprocess.DEVNULL)
frames=[]
for i in range(32):
 frames.append(json.loads(subprocess.check_output(base+['popupStatus'],text=True)))
 time.sleep(.01)
print(json.dumps(frames))
"""
 samples=json.loads(cmd('python','-c',program))
 results['submenu_samples']=samples
 assert any(not s['displayed_controls']['controlsMoreOpen'] and s['content_opacity']<1 for s in samples),'No outgoing state sampled'
 assert any(s['displayed_controls']['controlsMoreOpen'] and s['content_opacity']<1 for s in samples),'No incoming state sampled'
 s=settled();verify('more',s);capture('more',s)
 ipc('openWifiControls');s=settled();verify('wifi',s);capture('wifi',s)
 ipc('openBluetoothControls');s=settled();verify('bluetooth',s)
 ipc('openVolumeControls');s=settled();verify('audio',s)
 ipc('openMicrophoneControls');s=settled();verify('microphone',s)
 ipc('openShortcuts');s=settled();verify('shortcuts',s)
 close();ipc('openCalendar');s=settled();verify('calendar',s);close()
 ipc('openMedia');s=settled();verify('media',s);capture('media',s);close()
 ipc('toggleBattery');s=settled();verify('battery',s);close()
 ipc('openEnvironments');s=settled();verify('environments',s);close()
 ipc('hotkeyTouchpadToggled');wait(lambda s:s['osd_visible']);time.sleep(.4)
 p=home/'.cache/apx-consistency-bar.png';assert not p.exists()
 cmd('grim','-g','0,0 1280x46','/home/apx/.cache/'+p.name);(OUT/'bar.png').write_bytes(p.read_bytes());p.unlink()
 results['configerrors']=cmd('hyprctl','configerrors').strip();assert not results['configerrors']
 (OUT/'live-results.json').write_text(json.dumps(results,indent=2)+'\n')
 print('CONSISTENCY_PASS: 11 menus aligned at y=65, shared actual text font, staged submenu exit/swap/reveal, grouped bar')
finally:
 close()
