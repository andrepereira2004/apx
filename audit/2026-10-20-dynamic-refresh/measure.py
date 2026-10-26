import json,subprocess,time
from pathlib import Path
out=Path(__file__).parent
cmd=['python',str(out.parents[1]/'audit/2026-10-16-lucide-bar/session-command.py'),'quickshell','-c','apx','ipc','call','host','popupStatus']
samples=[]
for i in range(35):
 r=subprocess.run(cmd,capture_output=True,text=True)
 try:
  status=json.loads(r.stdout)
  if status.get('dynamic_reads'):samples.append(status['dynamic_reads'])
 except ValueError:pass
 time.sleep(.12)
summary={}
for key in ['battery','volume','microphone','audio','network','hardware']:
 values={s[key]['sample']:s[key]['elapsed'] for s in samples if key in s}
 ordered=sorted(values)
 summary[key]={'samples':len(values),'max_query_ms':max(values.values()) if values else None,'max_sample_gap_ms':max((b-a for a,b in zip(ordered,ordered[1:])),default=None)}
(out/'timings.json').write_text(json.dumps({'summary':summary,'samples':samples},indent=2)+'\n');print(json.dumps(summary,indent=2))
assert all(v['samples']>=3 for v in summary.values()),'Missing successful periodic updates'
