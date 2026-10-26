from pathlib import Path
import subprocess,time,shutil,json,os
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
home=Path('/var/lib/apx/environments')/state['name']/'home/apx'
stage=home/'.cache/apx-rofi-motion-validation';stage.mkdir(exist_ok=True)
shutil.copy2(OUT/'secondary-candidate.so',stage/'apx-rofi-secondary-v1.so')
for path in [stage]+list(stage.iterdir()):os.chown(path,home.stat().st_uid,home.stat().st_gid)
base=['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py')]
def cmd(*args):return subprocess.check_output(base+list(args),text=True)
def key(k):cmd('hyprctl','eval',f'hl.dispatch(hl.dsp.send_shortcut({{mods="",key="{k}"}}))')
assert not subprocess.run(base+['pgrep','-x','rofi'],capture_output=True).stdout,'Owner Rofi is open'
p=subprocess.Popen(base+['env','APX_ROFI_MOTION_TRACE=1','LD_PRELOAD=/home/apx/.cache/apx-rofi-motion-validation/apx-rofi-secondary-v1.so','ROFI_PLUGIN_PATH=/home/apx/.local/lib/rofi','rofi','-modi','apps,files,system','-show','apps'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
 time.sleep(.8)
 for _ in range(3):key('Tab');time.sleep(.3)
 # Rapid reversals must finish on the last requested page.
 for _ in range(4):key('Tab');time.sleep(.035)
 time.sleep(.3);key('Escape')
 stdout,stderr=p.communicate(timeout=4)
 (OUT/'live.log').write_text(stdout+stderr)
 print('exit',p.returncode,stderr[-1800:])
 assert p.returncode in (0,1) and stderr.count('APX_MOTION start')>=3 and 'APX_MOTION complete' in stderr
finally:
 if p.poll() is None:p.terminate();p.wait(timeout=4)
 shutil.rmtree(stage)
