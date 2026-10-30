"""Measure only disposable-folder windows; never quit the shared Thunar process."""
import json,subprocess,tempfile,time,statistics
from pathlib import Path

def clients():
    return json.loads(subprocess.check_output(['hyprctl','-j','clients'],text=True))

def active():
    return json.loads(subprocess.check_output(['hyprctl','-j','activewindow'],text=True)).get('address')

original=active(); rows=[]
with tempfile.TemporaryDirectory(prefix='apx-thunar-latency-') as directory:
    title=Path(directory).name
    for i in range(5):
        start=time.monotonic(); proc=subprocess.Popen(['thunar','--window',directory],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        own=None
        while time.monotonic()-start<8:
            own=next((c for c in clients() if title in c.get('title','') and c.get('class','').lower() in ('thunar','org.xfce.thunar')),None)
            if own:break
            time.sleep(.02)
        if not own:raise RuntimeError('Disposable window not found; no user window will be closed')
        mapped=time.monotonic()-start
        time.sleep(.5) # allow configured entrance to finish before close sample
        t=time.monotonic()
        subprocess.run(['hyprctl','eval','for _,w in ipairs(hl.get_windows()) do if w.title == '+json.dumps(own['title'])+' then hl.dispatch(hl.dsp.window.close({window=w})) end end'],check=True,stdout=subprocess.DEVNULL)
        while any(c.get('address')==own['address'] for c in clients()):
            if time.monotonic()-t>5:raise RuntimeError('Window close timeout')
            time.sleep(.02)
        rows.append({'iteration':i+1,'mapped_ms':round(mapped*1000,1),'removed_from_client_list_ms':round((time.monotonic()-t)*1000,1)})
        time.sleep(.4)
    assert not any(title in c.get('title','') for c in clients())
# Restore only when compositor has already returned to the original window.
# Never force focus over an intervening owner action.
print(json.dumps({'scope':'direct thunar --window empty directory; first sample not guaranteed cold; mapped != interactive or animation-complete; polling includes subprocess overhead','samples':rows,'median_mapped_ms':statistics.median(r['mapped_ms'] for r in rows),'temporary_windows_remaining':0},indent=2))
