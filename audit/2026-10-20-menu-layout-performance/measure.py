"""Opt-in frame-swapped timing; opens/closes menus without invoking controls."""
import json,subprocess,time,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent
RUNNER=['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py')]
def ipc(action):
 return subprocess.check_output(RUNNER+['quickshell','-c','apx','ipc','call','host',action],text=True)
def close():
 status=json.loads(ipc('popupStatus'))
 if status['visible']:
  action={'controls':'toggleControls','calendar':'toggleCalendar','battery':'toggleBattery','environments':'openEnvironments','media':'openMedia'}.get(status['kind'])
  if action:ipc(action);time.sleep(.35)
results=[]
for attempt in range(30):
 try:
  json.loads(ipc('popupStatus'));break
 except (ValueError,subprocess.CalledProcessError):time.sleep(.2)
else:raise RuntimeError('Shell IPC did not settle after reload')
try:
 close()
 for action in ['toggleCalendar','toggleBattery','toggleControls']*3:
  ipc('startMenuFrameProbe');ipc(action);time.sleep(.42)
  samples=json.loads(ipc('stopMenuFrameProbe'))
  gaps=[b['time']-a['time'] for a,b in zip(samples,samples[1:])]
  results.append(dict(action=action,frames=len(samples),median_ms=statistics.median(gaps) if gaps else None,max_ms=max(gaps,default=None),gaps_over_20ms=sum(g>20 for g in gaps),samples=samples))
  close()
finally:
 ipc('stopMenuFrameProbe');close()
(OUT/'frames.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps([{k:v for k,v in x.items() if k!='samples'} for x in results],indent=2))
