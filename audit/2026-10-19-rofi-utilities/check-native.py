import subprocess,time,json
from pathlib import Path
r=['python','audit/2026-10-16-lucide-bar/session-command.py']
def cmd(*args):return subprocess.check_output(r+list(args),text=True)
def key(k,mods=''):
 return cmd('hyprctl','eval','hl.dispatch(hl.dsp.send_shortcut({mods='+json.dumps(mods)+',key='+json.dumps(k)+'}))')
def text(t):
 for c in t:key('space' if c==' ' else c)
 time.sleep(.2)
def shot(name):
 temp='/home/apx/.cache/apx-folders-check.png';cmd('grim',temp)
 home=Path('/var/lib/apx/environments')/json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())['name']/'home/apx'
 p=home/'.cache/apx-folders-check.png';(Path('audit/2026-10-19-rofi-utilities')/(name+'.png')).write_bytes(p.read_bytes());p.unlink()
if __name__=='__main__':
 cmd('quickshell','-c','apx','ipc','call','host','openApplications');time.sleep(.5)
 text('xarchiver');key('1','ALT');time.sleep(.3);shot('folder-actions')
