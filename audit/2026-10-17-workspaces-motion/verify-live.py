from pathlib import Path
import subprocess,json
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent
program='''import subprocess,time,json
base=['quickshell','-c','apx','ipc','call','host']
def ipc(name):return subprocess.check_output(base+[name],text=True)
def state():return json.loads(ipc('popupStatus'))
def frames(duration):
 out=[];start=time.monotonic()
 while time.monotonic()-start<duration:
  s=state();out.append({'ms':round((time.monotonic()-start)*1000),'width':s['workspace_width'],'controls_x':s['bar_targets']['controls']['x']});time.sleep(.012)
 return out
initial=state();results={}
if not initial['workspaces_expanded']:ipc('toggleWorkspaces');time.sleep(.35)
full=state()['workspace_width'];assert full>30
ipc('toggleWorkspaces');results['collapse']=frames(.4)
assert state()['workspace_width']==30
ipc('toggleWorkspaces');results['expand']=frames(.4)
assert abs(state()['workspace_width']-full)<.1
for name in ['collapse','expand']:
 widths=[s['width'] for s in results[name]]
 assert any(30<w<full for w in widths),(name,widths)
 assert all(abs(s['controls_x']-initial['bar_targets']['controls']['x'])<.1 for s in results[name])
 pairs=zip(widths,widths[1:])
 assert all(b<=a+.1 if name=='collapse' else b>=a-.1 for a,b in pairs),(name,widths)
ipc('toggleWorkspaces');time.sleep(.09);before=state()['workspace_width'];ipc('toggleWorkspaces');results['reverse']=frames(.4)
assert abs(state()['workspace_width']-full)<.1
assert any(30<s['width']<full for s in results['reverse'])
if not initial['workspaces_expanded']:ipc('toggleWorkspaces');time.sleep(.35)
print(json.dumps(results))
'''
runner=['python',str(r/'audit/2026-10-16-lucide-bar/session-command.py')]
result=subprocess.check_output(runner+['python','-c',program],text=True);(a/'live-frames.json').write_text(result)
print('PASS: intermediate frames on open/close, monotonic widths, reversal without reset, stationary control button')
