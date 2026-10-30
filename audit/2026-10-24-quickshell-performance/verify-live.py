from pathlib import Path
import subprocess,json,time
repo=Path('/root/apx-host-development-mode-v1/apx');out=Path('/root/apx-quickshell-optimization-20261024')
prefix=['python3',str(repo/'audit/2026-10-16-lucide-bar/session-command.py'),'quickshell','-c','apx','ipc','call','host']
def call(name):
 p=subprocess.run(prefix+[name],capture_output=True,text=True,check=True,timeout=10)
 return json.loads(p.stdout) if name=='popupStatus' else p.stdout
before=call('popupStatus');assert not before['visible'],'Leave user-opened menu untouched'
result={'closed_before':before}
try:
 call('openControls');time.sleep(1)
 a=call('popupStatus');time.sleep(1.2);b=call('popupStatus')
 assert a['visible'] and b['visible'] and a['kind']=='controls'
 for key in ['network','volume','microphone','audio']:
  assert b['dynamic_reads'][key]['sample']>a['dynamic_reads'][key]['sample'],key
 assert not b['animation_running'] and not b['transition_input_blocked']
 result.update(open_a=a,open_b=b)
finally:
 if call('popupStatus')['visible']:call('toggleControls')
time.sleep(0.5);result['closed_after']=call('popupStatus');assert not result['closed_after']['visible']
(out/'live-validation.json').write_text(json.dumps(result,indent=2))
print('Live controls open, refresh network/audio/volume/microphone, settle and close: OK')
