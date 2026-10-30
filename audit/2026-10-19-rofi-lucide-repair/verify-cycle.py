"""Verify cycling existing Brave windows without opening/closing any owner window."""
import json,subprocess,time
from pathlib import Path
runner=['python','audit/2026-10-16-lucide-bar/session-command.py']
def cmd(*args):return subprocess.check_output(runner+list(args),text=True)
def clients():return json.loads(cmd('hyprctl','-j','clients'))
def active():return json.loads(cmd('hyprctl','-j','activewindow'))
original=active();before=clients();addresses={w['address'] for w in before}
windows=sorted(w['address'] for w in before if w['class']=='brave-browser')
assert len(windows)>1
visits=[]
try:
 for i in range(len(windows)+1):
  prior=active().get('address')
  cmd('/home/apx/.local/bin/apx-window-apps-v1','cycle','brave-browser')
  time.sleep(.12)
  current=active();visits.append({'address':current['address'],'workspace':current['workspace']['id']})
  if prior in windows:assert current['address']==windows[(windows.index(prior)+1)%len(windows)]
 assert len({v['address'] for v in visits[:len(windows)]})==len(windows)
 assert visits[0]['address']==visits[-1]['address']
 assert {w['address'] for w in clients()}==addresses
 report={'visits':visits,'wraps':True,'window_set_unchanged':True}
 Path('audit/2026-10-19-rofi-lucide-repair/cycle-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
finally:
 if original.get('address') in {w['address'] for w in clients()}:
  cmd('hyprctl','eval','hl.dispatch(hl.dsp.focus({window='+json.dumps('address:'+original['address'])+'}))')
