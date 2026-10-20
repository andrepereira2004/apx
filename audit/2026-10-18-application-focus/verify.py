from pathlib import Path
import json,subprocess,time,base64,os
runner=['python','audit/2026-10-16-lucide-bar/session-command.py']
def cmd(*args):return subprocess.check_output(runner+list(args),text=True)
def clients():return json.loads(cmd('hyprctl','-j','clients'))
def active():return json.loads(cmd('hyprctl','-j','activewindow'))
def focus(workspace):return cmd('hyprctl','eval','hl.dispatch(hl.dsp.focus({workspace='+str(workspace)+'}))')
marker=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
home=Path('/var/lib/apx/environments')/marker['name']/'home/apx'
image=home/'.cache/apx-focus-image-check.png'
assert not image.exists()
image.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jD1kAAAAASUVORK5CYII='));meta=home.stat();os.chown(image,meta.st_uid,meta.st_gid)
before={w['address'] for w in clients()};original=active();workspace=json.loads(cmd('hyprctl','-j','activeworkspace'))['id'];test=None;result={}
try:
 cmd('hyprctl','eval','hl.exec_cmd("brave --new-window file:///home/apx/.cache/apx-focus-image-check.png")')
 end=time.monotonic()+10
 while time.monotonic()<end:
  added=[w for w in clients() if w['address'] not in before and 'brave' in w['class'].lower()]
  if len(added)==1:test=added[0];break
  time.sleep(.1)
 assert test,'No dedicated browser window'
 destination=test['workspace']['id'];away=9 if destination!=9 else 8
 focus(away);time.sleep(.25)
 assert json.loads(cmd('hyprctl','-j','activeworkspace'))['id']==away
 cmd('xdg-open','/home/apx/.cache/apx-focus-image-check.png')
 end=time.monotonic()+6
 while time.monotonic()<end:
  now=active()
  if now.get('address')==test['address']:break
  time.sleep(.1)
 assert now.get('address')==test['address'],now
 result={'image_open_focuses_exact_browser_window':True,'from_workspace':away,'to_workspace':destination}
 print(result)
finally:
 if test:
  cmd('hyprctl','eval','hl.dispatch(hl.dsp.window.close({window='+json.dumps('address:'+test['address'])+'}))')
 focus(workspace)
 if original.get('address'):cmd('hyprctl','eval','hl.dispatch(hl.dsp.focus({window='+json.dumps('address:'+original['address'])+'}))')
 image.unlink()
 Path('audit/2026-10-18-application-focus/results.json').write_text(json.dumps(result,indent=2)+'\n')
