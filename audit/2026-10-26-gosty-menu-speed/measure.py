from pathlib import Path
import subprocess,time,json,sys
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent
prefix=['python3',str(r/'audit/2026-10-16-lucide-bar/session-command.py'),'quickshell','-c','apx','ipc','call','host']
def call(name):
 p=subprocess.run(prefix+[name],capture_output=True,text=True,check=True,timeout=15)
 return json.loads(p.stdout) if name=='popupStatus' else p.stdout
call('openControls');time.sleep(.7)
s=call('popupStatus');assert s['visible'] and s['kind']=='controls',s
print('Greeting:',s['ghost_message'])
result=[]
for action in ['openConnectivityControls','openControls','openBrightnessControls','openControls']:
 start=time.monotonic();call(action);samples=[]
 while time.monotonic()-start<3:
  s=call('popupStatus');assert s['visible'],s
  elapsed=(time.monotonic()-start)*1000
  samples.append(dict(ms=round(elapsed),transition=s['page_transition'],progress=s['page_progress'],blocked=s['transition_input_blocked']))
  if not s['page_transition'] and elapsed>60:break
  time.sleep(.01)
 result.append(dict(action=action,settled_ms=round(elapsed),samples=samples))
(a/(sys.argv[1]+'.json')).write_text(json.dumps(result,indent=2))
print([(x['action'],x['settled_ms']) for x in result])
