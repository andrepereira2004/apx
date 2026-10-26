"""Isolated Brave profile, local animated video, HTML fullscreen and RAF timing."""
import base64,hashlib,http.client,json,os,socket,struct,subprocess,tempfile,time
from pathlib import Path
from urllib.parse import urlparse

class CDP:
 def __init__(self,url):
  u=urlparse(url);self.s=socket.create_connection((u.hostname,u.port),timeout=8);self.seq=0
  key=base64.b64encode(os.urandom(16)).decode()
  self.s.sendall(f'GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
  header=b''
  while not header.endswith(b'\r\n\r\n'):header+=self.s.recv(1)
  assert header.startswith(b'HTTP/1.1 101 '), header.split(b'\r\n')[0]
 def read(self,n):
  data=b''
  while len(data)<n:
   part=self.s.recv(n-len(data))
   if not part:raise EOFError()
   data+=part
  return data
 def call(self,method,params=None):
  self.seq+=1;data=json.dumps({'id':self.seq,'method':method,'params':params or {}}).encode();mask=os.urandom(4)
  head=bytes([0x81,0x80|len(data)]) if len(data)<126 else bytes([0x81,0xfe])+struct.pack('!H',len(data))
  self.s.sendall(head+mask+bytes(v^mask[i%4] for i,v in enumerate(data)))
  while True:
   a,b=self.read(2);n=b&127
   if n==126:n=struct.unpack('!H',self.read(2))[0]
   elif n==127:n=struct.unpack('!Q',self.read(8))[0]
   payload=self.read(n)
   if a&15==8:raise EOFError()
   if a&15!=1:continue
   obj=json.loads(payload)
   if obj.get('id')==self.seq:
    if 'error' in obj:raise RuntimeError(obj['error'])
    return obj.get('result',{})
 def evaluate(self,code,await_promise=False):
  r=self.call('Runtime.evaluate',{'expression':code,'returnByValue':True,'userGesture':True,'awaitPromise':await_promise})
  if 'exceptionDetails' in r:raise RuntimeError(r['exceptionDetails'].get('exception',{}).get('description',r['exceptionDetails'].get('text')))
  return r.get('result',{}).get('value')

def windows():return json.loads(subprocess.check_output(['hyprctl','-j','clients'],text=True))

with tempfile.TemporaryDirectory(prefix='apx-brave-fullscreen-') as directory:
 root=Path(directory);profile=root/'profile'
 html=root/'probe.html'
 html.write_text('''<!doctype html><title>APX fullscreen disposable probe</title><style>body{background:#222;color:white}video{width:640px;max-width:90vw}video:fullscreen{width:100%;height:100%;background:black}</style><video id=v autoplay muted playsinline></video><script>
let c=document.createElement('canvas');c.width=640;c.height=360;let x=c.getContext('2d');
v.srcObject=c.captureStream(60);let t=0;function draw(){x.fillStyle='hsl('+(t++%360)+',40%,30%)';x.fillRect(0,0,640,360);x.fillStyle='white';x.fillRect((t*3)%600,150,40,40);requestAnimationFrame(draw)}draw();v.play();
window.samples=[];window.events=[];let last=performance.now();function frame(now){samples.push([now,now-last,innerWidth,innerHeight]);last=now;requestAnimationFrame(frame)}requestAnimationFrame(frame);
document.addEventListener('fullscreenchange',()=>events.push({time:performance.now(),fullscreen:!!document.fullscreenElement,width:innerWidth,height:innerHeight}));
</script>''')
 if os.environ.get('APX_PROBE_VIDEO') == 'decoded':
  subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-f','lavfi','-i','testsrc2=size=1280x720:rate=60','-t','4','-c:v','libx264','-preset','ultrafast','-crf','24','-pix_fmt','yuv420p',str(root/'movie.mp4')],check=True,timeout=30)
  text=html.read_text().replace("v.srcObject=c.captureStream(60)","v.src='movie.mp4';v.loop=true");html.write_text(text)
 p=subprocess.Popen(['/usr/bin/brave','--ozone-platform=wayland','--user-data-dir='+str(profile),'--remote-debugging-port=0','--remote-debugging-address=127.0.0.1','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-component-update','--disable-sync','--disable-extensions','--class=apx-fullscreen-probe','--new-window',html.as_uri()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 cdp=None
 try:
  deadline=time.monotonic()+12
  while not (profile/'DevToolsActivePort').exists():
   if time.monotonic()>deadline or p.poll() is not None:raise RuntimeError('Isolated browser did not start')
   time.sleep(.05)
  port=int((profile/'DevToolsActivePort').read_text().splitlines()[0])
  h=http.client.HTTPConnection('127.0.0.1',port,timeout=4);h.request('GET','/json/list');targets=json.loads(h.getresponse().read());h.close()
  target=next(t for t in targets if t.get('type')=='page' and t.get('url','').startswith(html.as_uri()))
  cdp=CDP(target['webSocketDebuggerUrl']);time.sleep(1)
  own=next(w for w in windows() if w.get('title','').startswith('APX fullscreen disposable probe'))
  youtube = os.environ.get('APX_PROBE_YOUTUBE') == '1'
  if youtube:
   cdp.call('Page.navigate',{'url':'https://www.youtube.com/watch?v=aqz-KE-bpKQ'})
   until=time.monotonic()+10
   ready=False
   while time.monotonic()<until:
    time.sleep(.5)
    try:
     ready=cdp.evaluate("!!document.querySelector('video') && document.querySelector('video').readyState >= 2")
     if ready:break
     cdp.evaluate("(()=>{let b=[...document.querySelectorAll('button')].find(b=>/^(Reject all|Rejeitar tudo|Rejeitar todos)$/.test(b.innerText.trim()));if(b)b.click()})()")
    except RuntimeError:pass
   if not ready:
    diagnostic=cdp.evaluate("({host:location.hostname,ready:document.readyState,hasVideo:!!document.querySelector('video'),videoReady:document.querySelector('video')?.readyState,videoError:document.querySelector('video')?.error?.code,signInRequired:/Sign in to confirm|Inicie sess.o para confirmar/.test(document.body.innerText),consent:location.hostname.includes('consent')})")
    print(json.dumps({'youtube_ready':False,'diagnostic':diagnostic},indent=2))
    raise RuntimeError('YouTube test video not ready in disposable profile')
   cdp.evaluate("window.apxV=document.querySelector('video');apxV.muted=true;apxV.play()",True)
   cdp.evaluate("window.samples=[];window.events=[];window.apxLast=performance.now();function apxFrame(now){samples.push([now,now-apxLast,innerWidth,innerHeight]);apxLast=now;requestAnimationFrame(apxFrame)}requestAnimationFrame(apxFrame);document.addEventListener('fullscreenchange',()=>events.push({time:performance.now(),fullscreen:!!document.fullscreenElement,width:innerWidth,height:innerHeight}))")
   time.sleep(1)
  rows=[]
  experiment=os.environ.get('APX_PROBE_EXPERIMENT','')
  for cycle in range(8 if experiment else 4):
   candidate=bool(experiment and cycle%4>=2)
   if experiment=='noanim':
    code='hl.dispatch(hl.dsp.window.set_prop({prop="no_anim",value="'+('1' if candidate else '0')+'",window='+json.dumps('address:'+own['address'])+'}))'
    result=subprocess.check_output(['hyprctl','eval',code],text=True);assert result.strip()=='ok'
   elif experiment:
    css = '#cinematics {display:none!important}' if experiment=='ambient' else ('ytd-watch-flexy {contain:layout style!important}' if experiment=='contain' else '*,*::before,*::after {transition:none!important;animation:none!important}')
    cdp.evaluate("document.getElementById('apx-test-style')?.remove()")
    if candidate:cdp.evaluate("(()=>{let s=document.createElement('style');s.id='apx-test-style';s.textContent="+json.dumps(css)+";document.head.append(s)})()")
    time.sleep(.2)
   for enter in (True,False):
    cdp.evaluate('samples=[];events=[]');cdp.call('Performance.enable');before_metrics={m['name']:m['value'] for m in cdp.call('Performance.getMetrics')['metrics']}
    start=time.monotonic()
    cdp.evaluate("new Promise(resolve=>{document.addEventListener('fullscreenchange',()=>resolve(true),{once:true});document.querySelector('.ytp-fullscreen-button').click()})" if youtube and enter else ('v.requestFullscreen()' if enter else 'document.exitFullscreen()'),True)
    promise_ms=(time.monotonic()-start)*1000
    time.sleep(.75)
    result=cdp.evaluate('({intervals:samples.map(x=>x[1]),viewports:samples.filter((x,i,a)=>!i||x[2]!==a[i-1][2]||x[3]!==a[i-1][3]).map(x=>({time:x[0],width:x[2],height:x[3]})),events,fullscreen:!!document.fullscreenElement,frames:document.querySelector("video")?.getVideoPlaybackQuality().totalVideoFrames??null,dropped:document.querySelector("video")?.getVideoPlaybackQuality().droppedVideoFrames??null})')
    after_metrics={m['name']:m['value'] for m in cdp.call('Performance.getMetrics')['metrics']};result['work_ms']={k:round((after_metrics.get(k,0)-before_metrics.get(k,0))*1000,1) for k in ('ScriptDuration','LayoutDuration','RecalcStyleDuration','TaskDuration')};result['candidate']=candidate
    intervals=result.pop('intervals');result.update(cycle=cycle+1,enter=enter,promise_ms=round(promise_ms,1),max_raf_gap_ms=round(max(intervals,default=0),1),raf_gaps_over_25ms=sum(v>25 for v in intervals),samples=len(intervals))
    rows.append(result)
  print(json.dumps({'scope':'isolated browser: anonymous YouTube when selected, otherwise local video; RAF timing is not GPU presentation timing','video_source':'YouTube anonymous public Big Buck Bunny' if youtube else os.environ.get('APX_PROBE_VIDEO','canvas'),'xwayland':own.get('xwayland'),'results':rows},indent=2))
 finally:
  if cdp:
   try:cdp.call('Browser.close')
   except (EOFError,OSError):pass
   cdp.s.close()
  if p.poll() is None:
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=5)
