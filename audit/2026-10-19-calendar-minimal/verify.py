import subprocess,json,time
from pathlib import Path
runner=['python','audit/2026-10-16-lucide-bar/session-command.py']
def cmd(*a):return subprocess.check_output(runner+list(a),text=True)
def ipc(n):return cmd('quickshell','-c','apx','ipc','call','host',n)
def state():return json.loads(ipc('popupStatus'))
def key(k):cmd('hyprctl','eval','hl.dispatch(hl.dsp.send_shortcut({mods="",key="'+k+'"}))')
a=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/a['name']/'home/apx';out=Path('audit/2026-10-19-calendar-minimal')
def capture(name):
 s=state();p=home/'.cache/apx-calendar-minimal.png';x=round(s['visual_x']);cmd('grim','-g',f'{x},50 {min(round(s['visual_width']),1280-x)}x650','/home/apx/.cache/apx-calendar-minimal.png');(out/(name+'.png')).write_bytes(p.read_bytes());p.unlink()
if not state()['visible']:ipc('toggleCalendar')
time.sleep(.6);key('Home');time.sleep(.3);original=state()['calendar_date'];capture('month')
key('Next');samples=[state()];time.sleep(.3);samples.append(state())
# Hyprland uses Next for PageDown.
assert samples[-1]['calendar_date'] != original,samples[-1]['calendar_date']
assert not samples[-1]['calendar_navigation_running'];assert samples[-1]['calendar_page_opacity']==1
capture('next-month');key('Prior');time.sleep(.3);assert state()['calendar_date'][:7]==original[:7]
# Navigate to year selector without changing a day/event.
for _ in range(50):
 s=state()
 if s['calendar_focus_kind']=='view' and s['calendar_focus_key']=='year':break
 key('Tab')
else:raise AssertionError('Year selector unreachable')
key('Return');time.sleep(.15);assert state()['calendar_view']=='year';y=state()['calendar_date'];key('Next');time.sleep(.3);assert int(state()['calendar_date'][:4])==int(y[:4])+1;capture('year');key('Home');time.sleep(.2)
for _ in range(55):
 if state()['calendar_focus_kind']=='new':break
 key('Tab')
else:raise AssertionError('New event unreachable')
key('Return');time.sleep(.3);assert state()['calendar_editor'];capture('event-editor')
for _ in range(4):key('Tab')
key('Return');time.sleep(.2);capture('event-details')
key('Escape');time.sleep(.2)
s=state()
if s['visible']:key('Escape')
(out/'validation.json').write_text(json.dumps({'month_and_year_navigation':True,'editor_opened':True,'samples':[{k:s[k] for k in ['calendar_date','calendar_navigation_running','calendar_page_opacity','calendar_page_offset']} for s in samples]},indent=2)+'\n')
print('Month/year navigation and editor verified; no event saved')
