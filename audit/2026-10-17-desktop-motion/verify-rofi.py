from pathlib import Path
import json, subprocess, time, os, signal
ROOT=Path(__file__).resolve().parents[2]
runner=['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py')]
def run(*args):return subprocess.check_output(runner+list(args),text=True)
def layers():
 result=[]
 for monitor in json.loads(run('hyprctl','-j','layers')).values():
  for group in monitor['levels'].values():result += [x for x in group if x['namespace']=='rofi']
 return result
assert not layers(),'Owner launcher is already open'
s=json.loads(run('quickshell','-c','apx','ipc','call','host','popupStatus'));assert not s['visible']
process=subprocess.Popen(runner+['rofi','-dmenu','-p','Teste de movimento APX','-no-custom'],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,start_new_session=True)
try:
 process.stdin.write('Teste de movimento\n');process.stdin.close()
 samples=[];end=time.monotonic()+1.0
 while time.monotonic()<end:
  samples.extend(layers());time.sleep(.015)
 assert samples, 'Rofi did not map'
 assert any(x['alpha']==1 for x in samples),samples
 (Path(__file__).parent/'rofi-motion.json').write_text(json.dumps(samples,indent=2)+'\n')
 print('ROFI_PASS: configured layer maps and reaches full opacity; animation path/frame pacing not measured; no application launched')
finally:
 os.killpg(process.pid,signal.SIGTERM);process.wait(timeout=3)
