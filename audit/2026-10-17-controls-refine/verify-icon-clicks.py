from pathlib import Path
import subprocess,json,time,shutil,os
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent
runner=['python',str(r/'audit/2026-10-16-lucide-bar/session-command.py')]
def cmd(*args):return subprocess.check_output(runner+list(args),text=True)
def ipc(name):return cmd('quickshell','-c','apx','ipc','call','host',name)
def status():return json.loads(ipc('popupStatus'))
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());h=Path('/var/lib/apx/environments')/state['name']/'home/apx'
p=h/'.cache/apx-refine-pointer';assert not p.exists();shutil.copy2(r/'audit/2026-10-17-shell-interaction/pointer-check',p);st=h.stat();os.chown(p,st.st_uid,st.st_gid);os.chmod(p,0o755)
original=json.loads(cmd('hyprctl','-j','cursorpos'));results={}
try:
 for section,offset in [('Audio',151),('Brightness',228)]:
  ipc('openControls');time.sleep(.5);s=status()
  cmd('/home/apx/.cache/'+p.name,str(round(s['visual_x']+30)),str(round(s['panel_y']+offset)),'1280','720','click')
  time.sleep(.6);s=status();assert s['displayed_controls']['controls'+section+'Open'],s
  results[section]=True
 ipc('toggleControls');time.sleep(.4)
 (a/'icon-click-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS: real pointer clicks on sound and brightness icons open the corresponding menus')
finally:
 cmd('/home/apx/.cache/'+p.name,str(original['x']),str(original['y']),'1280','720','move');p.unlink()
