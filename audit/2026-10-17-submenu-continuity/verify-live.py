from pathlib import Path
import subprocess
runner=['python','audit/2026-10-16-lucide-bar/session-command.py']
program="""import subprocess,json,time
b=['quickshell','-c','apx','ipc','call','host']
def ipc(n):return subprocess.check_output(b+[n],text=True)
def state():return json.loads(ipc('popupStatus'))
def sample():
 out=[]
 for i in range(27):
  out.append(state());time.sleep(.012)
 return out
original=state()
results={}
try:
 ipc('openControls')
 deadline=time.monotonic()+3
 while time.monotonic()<deadline:
  s=state()
  if s['kind']=='controls' and s['island_progress']==1 and not s['page_transition'] and not s['pending_kind']:break
  time.sleep(.03)
 else:raise RuntimeError('Menu changed during validation')
 time.sleep(.12)
 ipc('openConnectivityControls');results['enter']=sample()
 mid=[s for s in results['enter'] if 0<s['page_progress']<1]
 assert mid, 'No intermediate frames; menu may have changed during sampling'
 assert all(s['outgoing_page_visible'] for s in mid if s['page_blend'] < 1),mid
 assert any(s['page_progress'] < 1 and s['popup_opacity'] == 1 and not s['outgoing_page_visible'] for s in mid),mid
 assert all(abs(s['popup_opacity']+s['outgoing_page_opacity']-1)<.04 for s in mid)
 assert results['enter'][-1]['displayed_controls']['controlsConnectivityOpen']
 assert all(not s['material_animating'] for s in results['enter'])
 assert all(abs(s['target_height']-s['settled_height'])<.1 for s in results['enter'] if s['page_progress']<1)
 ipc('openControls');results['back']=sample()
 mid=[s for s in results['back'] if 0<s['page_progress']<1]
 assert mid
 assert all(s['outgoing_page_visible'] for s in mid if s['page_blend'] < 1)
 assert not results['back'][-1]['displayed_controls']['controlsConnectivityOpen']
 assert all(not s['material_animating'] for s in results['back'])
 assert all(abs(s['target_height']-s['settled_height'])<.1 for s in results['back'] if s['page_progress']<1)
 ipc('openConnectivityControls');time.sleep(.065);ipc('openBrightnessControls');time.sleep(.9)
 results['rapid']=state()
 assert results['rapid']['displayed_controls']['controlsBrightnessOpen']
 assert not results['rapid']['page_transition']
 assert not results['rapid']['outgoing_page_visible']
 print(json.dumps(results))
finally:
 print(json.dumps(results))
 if original['visible'] and original['kind']=='controls':
  c=original['displayed_controls']
  route='openMoreControls' if c['controlsMoreOpen'] else ('openConnectivityControls' if c['controlsConnectivityOpen'] else ('openBrightnessControls' if c['controlsBrightnessOpen'] else 'openControls'))
  ipc(route)
 elif original['visible'] and original['kind']=='calendar':ipc('openCalendar')
 elif not original['visible']:ipc('toggleControls')
"""
p=subprocess.run(runner+['python','-c',program],capture_output=True,text=True)
Path('audit/2026-10-17-submenu-continuity/live-frames.json').write_text(p.stdout+p.stderr)
print(p.stderr if p.returncode else 'PASS: full opacity before movement ends, complementary fades, enter/back and rapid navigation')
assert p.returncode==0
