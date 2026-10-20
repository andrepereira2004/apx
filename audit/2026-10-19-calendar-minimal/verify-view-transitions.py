import json,subprocess,time
from pathlib import Path
runner=['python','audit/2026-10-16-lucide-bar/session-command.py']
def cmd(*a):return subprocess.check_output(runner+list(a),text=True)
def ipc(n):return cmd('quickshell','-c','apx','ipc','call','host',n)
def state():return json.loads(ipc('popupStatus'))
def key(k):cmd('hyprctl','eval','hl.dispatch(hl.dsp.send_shortcut({mods="",key="'+k+'"}))')
if not state()['visible']:ipc('toggleCalendar')
time.sleep(.5);key('Home');time.sleep(.3);results=[]
for view in ['year','day','month']:
 for _ in range(55):
  s=state()
  if s['calendar_focus_kind']=='view' and s['calendar_focus_key']==view:break
  key('Tab')
 else:raise AssertionError('Unreachable '+view)
 key('Return');during=state();assert during['calendar_navigation_running'],during
 assert during['calendar_page_opacity']<1,during
 time.sleep(.3);after=state();assert after['calendar_view']==view;assert not after['calendar_navigation_running'];assert after['calendar_page_opacity']==1
 results.append({'view':view,'animated':True,'during_opacity':during['calendar_page_opacity'],'during_offset':during['calendar_page_offset']})
key('Escape');Path('audit/2026-10-19-calendar-minimal/view-transitions.json').write_text(json.dumps(results,indent=2)+'\n');print(results)
