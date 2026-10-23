from pathlib import Path
import subprocess,json,time,select,os,signal
ROOT=Path(__file__).resolve().parents[2]
runner=['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py')]
home=Path('/var/lib/apx/environments/minecraft/home/apx')
target=home/'.cache/apx-media-events-test-20261016.py'
assert not target.exists()
source=(ROOT/'audit/2026-10-16-island/mock-player.py').read_text()
source=source.replace('<method name="PlayPause"/>','<method name="PlayPause"/><method name="Play"/><method name="Pause"/>').replace("elif name=='PlayPause':base=position()/1000000;started=time.monotonic();playing=not playing","elif name in ('PlayPause','Play','Pause'):base=position()/1000000;started=time.monotonic();playing=not playing if name=='PlayPause' else name=='Play'")
source=source.replace('    invocation.return_value(None)', '''    connection.emit_signal(None,'/org/mpris/MediaPlayer2','org.freedesktop.DBus.Properties','PropertiesChanged',GLib.Variant('(sa{sv}as)',('org.mpris.MediaPlayer2.Player',{'PlaybackStatus':GLib.Variant('s','Playing' if playing else 'Paused')},['Position'])))
    invocation.return_value(None)''')
target.write_text(source);meta=target.parent.stat();os.chown(target,meta.st_uid,meta.st_gid)
watch=None;mock=None;results=[]
def read_until(predicate,deadline=2):
 end=time.monotonic()+deadline
 while time.monotonic()<end:
  if not select.select([watch.stdout],[],[],max(0,end-time.monotonic()))[0]:break
  report=json.loads(watch.stdout.readline())
  if predicate(report['players']):return report
 raise AssertionError('No matching media event')
def sample(players):return next((p for p in players if p['name']=='org.mpris.MediaPlayer2.apx_trial'),None)
try:
 watch=subprocess.Popen(runner+['/home/apx/.local/bin/apx-desktop-activity-v1','watch-media'],stdout=subprocess.PIPE,text=True,start_new_session=True)
 read_until(lambda players:True)
 start=time.monotonic()
 mock=subprocess.Popen(runner+['python','/home/apx/.cache/'+target.name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
 read_until(lambda players:sample(players) is not None)
 results.append(dict(event='player-added',seconds=round(time.monotonic()-start,3)))
 for operation,predicate in [(['media','org.mpris.MediaPlayer2.apx_trial','play-pause'],lambda p:p['status']=='Paused'),(['media','org.mpris.MediaPlayer2.apx_trial','play-pause'],lambda p:p['status']=='Playing')]:
  start=time.monotonic()
  subprocess.run(runner+['/home/apx/.local/bin/apx-desktop-activity-v1']+operation,check=True,stdout=subprocess.DEVNULL)
  read_until(lambda players:sample(players) is not None and predicate(sample(players)))
  results.append(dict(event='state-change',seconds=round(time.monotonic()-start,3)))
 harness=home/'.cache/apx-feedback-harness-20261016.qml'
 assert not harness.exists()
 harness.write_bytes((ROOT/'audit/2026-10-16-control-layout/feedback-harness.qml').read_bytes());os.chown(harness,meta.st_uid,meta.st_gid)
 try:
  check=subprocess.run(runner+['env','QT_QPA_PLATFORM=offscreen','quickshell','--path','/home/apx/.cache/'+harness.name,'--no-color'],capture_output=True,text=True,timeout=10)
  (ROOT/'audit/2026-10-16-control-layout/feedback-validation.log').write_text(check.stdout+check.stderr)
  assert check.returncode==0 and 'FEEDBACK_PASS' in check.stdout+check.stderr,(check.returncode,check.stdout,check.stderr)
 finally:harness.unlink()
 start=time.monotonic();os.killpg(mock.pid,signal.SIGTERM);mock.wait(timeout=3);mock=None
 read_until(lambda players:sample(players) is None)
 results.append(dict(event='player-removed',seconds=round(time.monotonic()-start,3)))
 assert max(row['seconds'] for row in results)<1,results
 (ROOT/'audit/2026-10-16-control-layout/media-events.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps(results,indent=2))
finally:
 for process in (mock,watch):
  if process is not None:
   os.killpg(process.pid,signal.SIGTERM);process.wait(timeout=3)
 target.unlink()
