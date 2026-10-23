from pathlib import Path
import subprocess,json,time,shutil,os
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent
runner=['python',str(r/'audit/2026-10-16-lucide-bar/session-command.py')]
def cmd(*args):return subprocess.check_output(runner+list(args),text=True)
def ipc(name):return cmd('quickshell','-c','apx','ipc','call','host',name)
def status():return json.loads(ipc('popupStatus'))
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());h=Path('/var/lib/apx/environments')/state['name']/'home/apx'
p=h/'.cache/apx-bar-stability-pointer';assert not p.exists();shutil.copy2(r/'audit/2026-10-17-shell-interaction/pointer-check',p);st=h.stat();os.chown(p,st.st_uid,st.st_gid);os.chmod(p,0o755)
original=json.loads(cmd('hyprctl','-j','cursorpos'));results={}
def click(rect):cmd('/home/apx/.cache/'+p.name,str(round(rect['x']+rect['width']/2)),str(round(rect['y']+rect['height']/2)),'1280','720','click')
def barshot(name):
 cmd('grim','-g','0,0 1280x46','/home/apx/.cache/apx-bar-stability.png');q=h/'.cache/apx-bar-stability.png';(a/name).write_bytes(q.read_bytes());q.unlink()
def close():
 s=status()
 if s['visible']:ipc({'controls':'toggleControls','media':'openMedia','calendar':'toggleCalendar','battery':'toggleBattery','environments':'toggleEnvironments'}[s['kind']]);time.sleep(.5)
try:
 close();baseline=status();barshot('bar-default.png')
 ipc('openControls');time.sleep(.6);s=status();results['greeting']=s
 assert 1<s['ghost_width']<160,s;barshot('bar-greeting.png')
 click(s['bar_targets']['controls']);time.sleep(.7);s=status();assert not s['visible'],s
 results['controls_same_icon_closes']=True
 for name,action in [('calendar','toggleCalendar'),('battery','toggleBattery')]:
  ipc(action);time.sleep(.6);s=status();assert s['visible'] and s['kind']==name,s
  click(s['bar_targets'][name]);time.sleep(.7);s=status();assert not s['visible'],s
  results[name+'_same_icon_closes']=True
 # Media menu selection changes only its independent capsule, never right-side buttons.
 before=status()
 if before['media_width']>1:
  ipc('openMedia');frames=[]
  for i in range(12):frames.append(status());time.sleep(.025)
  for s in frames:
   for name in ['apps','files','battery','controls']:
    assert abs(s['bar_targets'][name]['x']-before['bar_targets'][name]['x'])<.5,(name,before,s)
  s=status();click(s['bar_targets']['media']);time.sleep(.7);assert not status()['visible']
  results['media_same_icon_closes']=True;results['media_keeps_right_buttons_fixed']=True;results['media_frames']=frames
 for expected in [not status()["workspaces_expanded"], status()["workspaces_expanded"]]:
  ipc('toggleWorkspaces');time.sleep(.3);s=status();assert s['workspaces_expanded']==expected,s
  if not expected:assert s['workspace_width']==30,s
  results['workspaces_'+str(expected)]=s['workspace_width'];barshot('workspaces-'+str(expected)+'.png')
 results['configerrors']=cmd('hyprctl','configerrors').strip();assert not results['configerrors']
 (a/'live-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS: compact greeting, same-icon closing, stable right-side buttons, workspace labels toggle to icon only')
finally:
 close();cmd('/home/apx/.cache/'+p.name,str(original['x']),str(original['y']),'1280','720','move');p.unlink()
