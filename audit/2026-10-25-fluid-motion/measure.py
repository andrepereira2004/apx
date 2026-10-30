from pathlib import Path
import subprocess,json,time,statistics,sys
ROOT=Path(__file__).resolve().parents[2]
base=['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py')]
def ipc(m):return subprocess.check_output(base+['qs','-c','apx','ipc','call','host',m],text=True)
def close():
 subprocess.run(base+['hyprctl','eval','hl.dispatch(hl.dsp.send_shortcut({mods="",key="Escape"}))'],capture_output=True);time.sleep(.35)
results=[]
try:
 for method in ['openControls','openCalendar','openControls','openCalendar','openControls','openCalendar']:
  close();ipc('startMenuFrameProbe');ipc(method);time.sleep(.7)
  samples=json.loads(ipc('stopMenuFrameProbe'));gaps=[b['time']-a['time'] for a,b in zip(samples,samples[1:])]
  assert len(samples)>5,(method,samples)
  results.append({'method':method,'samples':samples,'median_ms':statistics.median(gaps),'max_ms':max(gaps),'gaps_over_17ms':sum(x>17 for x in gaps)})
finally:ipc('stopMenuFrameProbe');close()
Path(__file__).with_name(sys.argv[1]+'.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps([{k:v for k,v in r.items() if k!='samples'} for r in results]))
