from pathlib import Path
import json, subprocess, time, os
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
runner=['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py')]
def command(*args):return subprocess.check_output(runner+list(args),text=True)
def ipc(name):return command('quickshell','-c','apx','ipc','call','host',name)
def status():return json.loads(ipc('popupStatus'))
def wait(predicate, timeout=3):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  s=status()
  if predicate(s):return s
  time.sleep(.03)
 raise AssertionError(s)
results={}
initial=status();assert not initial['visible'],'Owner menu is open; do not interrupt it'
active=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/active['name']/'home/apx'
original=json.loads(command('hyprctl','-j','activewindow')).get('address','')
try:
 ipc('openControls');wait(lambda s:s['island_progress']==1)
 ipc('openMoreControls')
 samples=[status() for _ in range(6)]
 results['submenu_samples']=samples
 assert any(0<s['content_opacity']<1 for s in samples),samples
 wait(lambda s:s['content_opacity']==1)
 ipc('openCalendar')
 samples=[status() for _ in range(7)];results['between_menu_samples']=samples
 assert any(340<s['visual_width']<500 for s in samples),samples
 wait(lambda s:s['content_opacity']==1 and abs(s['visual_width']-500)<1)
 ipc('openControls');wait(lambda s:s['island_progress']==1 and abs(s['visual_width']-340)<1)
 # Capture only the menu rectangle, not the owner's application contents.
 s=status();image=home/'.cache/apx-motion-menu-20261017.png';assert not image.exists()
 x=round(s['visual_x']);height=round(s['visual_height'])
 command('grim','-g',f'{x},65 340x{height}', '/home/apx/.cache/'+image.name)
 (OUT/'controls-after.png').write_bytes(image.read_bytes());image.unlink()
 ipc('toggleControls');wait(lambda s:not s['visible'])
 ipc('hotkeyTouchpadToggled');s=wait(lambda s:s['osd_visible'])
 assert s['island_transient'] or s['fullscreen'],s;results['transient']=s
 wait(lambda s:not s['osd_visible'])
 # Use an empty, disposable folder and only close windows created by this check.
 empty=home/'.cache/apx-motion-empty-20261017';assert not empty.exists();empty.mkdir();st=home.stat();os.chown(empty,st.st_uid,st.st_gid)
 before={w['address'] for w in json.loads(command('hyprctl','-j','clients'))}
 launch=subprocess.Popen(runner+['thunar','--window','/home/apx/.cache/'+empty.name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
 wait(lambda s:s['files_active'])
 after=json.loads(command('hyprctl','-j','clients'));created=[w['address'] for w in after if w['address'] not in before and w['class'].lower() in ('thunar','org.xfce.thunar')]
 assert len(created)==1,created;results['folder_selected']=True
 ipc('hotkeyTouchpadToggled');s=wait(lambda s:s['island_transient']);results['bar_transient']=s
 wait(lambda s:not s['osd_visible'])
 if original:
  command('hyprctl','dispatch','hl.dsp.focus({ window = '+json.dumps('address:'+original)+' })')
  wait(lambda s:not s['files_active']);results['folder_deselected']=True
 command('hyprctl','dispatch','hl.dsp.focus({ window = '+json.dumps('address:'+created[0])+' })');wait(lambda s:s['files_active'])
 # Exercise the same IPC endpoint as Super+P while our disposable window owns focus.
 ipc('openFiles');wait(lambda s:s['files_active']);results['super_p_endpoint']=True
 time.sleep(.2)
 current=json.loads(command('hyprctl','-j','clients'))
 for w in current:
  if w['address'] not in before and w['class'].lower() in ('thunar','org.xfce.thunar'):
   command('hyprctl','dispatch','hl.dsp.window.close({ window = '+json.dumps('address:'+w['address'])+' })')
 empty.rmdir()
 if original:command('hyprctl','dispatch','hl.dsp.focus({ window = '+json.dumps('address:'+original)+' })')
 results['configerrors']=command('hyprctl','configerrors').strip();assert not results['configerrors']
 (OUT/'live-results.json').write_text(json.dumps(results,indent=2)+'\n')
 print('LIVE_PASS: submenu fade, between-menu geometry, transient island, folder focus and Super+P endpoint; clean config')
finally:
 if status()['visible']:ipc('toggleControls')
