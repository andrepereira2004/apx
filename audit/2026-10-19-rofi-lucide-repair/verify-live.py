import subprocess,json,time
from pathlib import Path
runner=['python','audit/2026-10-16-lucide-bar/session-command.py']
OUT=Path('audit/2026-10-19-rofi-lucide-repair')
def cmd(*args):return subprocess.check_output(runner+list(args),text=True)
def ipc(method):return cmd('quickshell','-c','apx','ipc','call','host',method)
def clients():return json.loads(cmd('hyprctl','-j','clients'))
def key(value,mods=''):return cmd('hyprctl','eval','hl.dispatch(hl.dsp.send_shortcut({mods='+json.dumps(mods)+',key='+json.dumps(value)+'}))')
def type_text(text):
 for c in text:key(c)
 time.sleep(.1)
def capture(name):
 target='/home/apx/.cache/apx-rofi-repair.png';cmd('grim',target)
 state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
 p=Path('/var/lib/apx/environments')/state['name']/'home/apx/.cache/apx-rofi-repair.png'
 (OUT/(name+'.png')).write_bytes(p.read_bytes());p.unlink()
status=json.loads(ipc('popupStatus'))
assert not status['visible'] and not status['launcher_running']
before=clients();addresses={w['address'] for w in before};active=json.loads(cmd('hyprctl','-j','activewindow'))
created=[]
try:
 ipc('openApplications');time.sleep(.4);type_text('brave');key('1','ALT');time.sleep(.25);capture('brave-inline-actions')
 key('Escape');time.sleep(.15)
 ipc('openApplications');time.sleep(.3);type_text('brave');key('Return')
 deadline=time.monotonic()+8
 while time.monotonic()<deadline:
  created=[w for w in clients() if w['address'] not in addresses and w['class']=='brave-browser']
  if created:break
  time.sleep(.1)
 assert created,'Primary activation did not create a Brave window'
 assert not json.loads(ipc('popupStatus'))['launcher_running']
 report={'primary_activation_creates_brave_window':True,'new_windows':[w['address'] for w in created],
         'existing_windows_preserved':addresses.issubset({w['address'] for w in clients()}),
         'launcher_closes_after_launch':True}
 (OUT/'live-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
finally:
 if json.loads(ipc('popupStatus'))['launcher_running']:key('Escape')
 for w in created:cmd('hyprctl','eval','hl.dispatch(hl.dsp.window.close({window='+json.dumps('address:'+w['address'])+'}))')
 if active.get('address') in {w['address'] for w in clients()}:
  cmd('hyprctl','eval','hl.dispatch(hl.dsp.focus({window='+json.dumps('address:'+active['address'])+'}))')
