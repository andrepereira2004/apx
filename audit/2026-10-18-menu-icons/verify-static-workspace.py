import subprocess,json,time
from pathlib import Path
runner=['python','audit/2026-10-16-lucide-bar/session-command.py']
def cmd(*a):return subprocess.check_output(runner+list(a),text=True)
state=json.loads(cmd('quickshell','-c','apx','ipc','call','host','popupStatus'))
assert not state['visible'] and not state['launcher_running']
active=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
home=Path('/var/lib/apx/environments')/active['name']/'home/apx'
original=json.loads(cmd('hyprctl','-j','activeworkspace'))['id']
away=9 if original!=9 else 8
samples=[]
def capture(name):
 p=home/'.cache'/('apx-static-workspace-'+name+'.png')
 assert not p.exists()
 try:
  cmd('grim','-g','205,7 41x32','/home/apx/.cache/'+p.name)
  data=p.read_bytes();(Path('audit/2026-10-18-menu-icons')/('static-'+name+'.png')).write_bytes(data)
  samples.append(data)
 finally:p.unlink(missing_ok=True)
try:
 capture('before')
 cmd('hyprctl','eval','hl.dispatch(hl.dsp.focus({workspace='+str(away)+'}))')
 time.sleep(.25);capture('during')
 time.sleep(1.1);capture('after')
 assert samples[0] == samples[1]
 assert samples[1] == samples[2]
 print('Workspace icon pixels identical before, during and after workspace change')
finally:cmd('hyprctl','eval','hl.dispatch(hl.dsp.focus({workspace='+str(original)+'}))')
