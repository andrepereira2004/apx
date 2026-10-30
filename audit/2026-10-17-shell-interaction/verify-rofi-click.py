from pathlib import Path
import subprocess,json,time,os,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
RUNNER=['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py')]
def cmd(*args):return subprocess.check_output(RUNNER+list(args),text=True)
def ipc(name):return cmd('quickshell','-c','apx','ipc','call','host',name)
def state():return json.loads(ipc('popupStatus'))
def wait(predicate,timeout=5):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  s=state()
  if predicate(s):return s
  time.sleep(.025)
 raise AssertionError(s)
def settled(kind):return wait(lambda s:s['kind']==kind and s['island_progress']==1 and s['content_opacity']==1 and not s['page_transition'])
def close():
 s=state()
 if s['visible']:
  if s['island_closing'] and not s['pending_kind']:
   wait(lambda s:not s['visible']);return
  if s['pending_kind']:wait(lambda s:not s['pending_kind']);s=state()
  ipc({'calendar':'toggleCalendar','controls':'toggleControls','media':'openMedia','battery':'toggleBattery','environments':'openEnvironments'}[s['kind']]);wait(lambda s:not s['visible'])
assert not state()['visible'],'Owner menu open; do not interrupt'
assert not state()['launcher_running'],'Owner launcher open; do not interrupt'
active=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/active['name']/'home/apx'
pointer=home/'.cache/apx-interaction-pointer';assert not pointer.exists();shutil.copy2(OUT/'pointer-check',pointer);meta=home.stat();os.chmod(pointer,0o755);os.chown(pointer,meta.st_uid,meta.st_gid)
original=json.loads(cmd('hyprctl','-j','cursorpos'));results={}
def capture(name,geometry='0,0 1280x46'):
 p=home/'.cache'/('apx-interaction-'+name+'.png');assert not p.exists()
 try:
  cmd('grim','-g',geometry,'/home/apx/.cache/'+p.name);(OUT/(name+'.png')).write_bytes(p.read_bytes())
 finally:
  if p.exists():p.unlink()
try:
 # Open the real launcher, then send exactly one pointer click to the calendar.
 ipc('openApplications');wait(lambda s:s['launcher_running']);time.sleep(.6)
 layers=json.loads(cmd('hyprctl','-j','layers'));rofi=[]
 for monitor in layers.values():
  for group in monitor['levels'].values():rofi.extend(item for item in group if item['namespace']=='rofi')
 assert rofi and all(item['y']>=46 for item in rofi),rofi
 results['rofi_layers']=rofi
 results['all_layers']=layers
 target=state()['bar_targets']['calendar']
 cmd('/home/apx/.cache/'+pointer.name,str(round(target['x']+target['width']/2)),str(round(target['y']+target['height']/2)),'1280','720','click')
 results['cursor_after_click']=json.loads(cmd('hyprctl','-j','cursorpos'))
 results['after_click']=state()
 print('Click diagnostic',results['cursor_after_click'],{k:results['after_click'][k] for k in ['kind','visible','launcher_running']})
 s=wait(lambda s:s['visible'] and s['kind']=='calendar' and not s['launcher_running'])
 results['rofi_one_click']=s;settled('calendar');close()
finally:
 (OUT/'rofi-click-diagnostic.json').write_text(json.dumps(results,indent=2)+'\n')
 try:
  if state()['launcher_running']:ipc('toggleApplications')
  close()
 finally:
  try:cmd('/home/apx/.cache/'+pointer.name,str(original['x']),str(original['y']),'1280','720','move')
  finally:pointer.unlink()
