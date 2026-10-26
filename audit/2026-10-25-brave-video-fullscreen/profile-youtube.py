"""Profile page fullscreen work in a disposable Brave profile, without user data."""
import ast
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[2]
source=(Path(__file__).with_name('probe.py')).read_text()
tree=ast.parse(source)
cdp=next(ast.get_source_segment(source,n) for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CDP')
program='''import base64,http.client,json,os,socket,struct,subprocess,tempfile,time,collections
from pathlib import Path
from urllib.parse import urlparse
'''+cdp+'''
with tempfile.TemporaryDirectory(prefix='apx-youtube-cpu-') as d:
 profile=Path(d)/'profile';page=Path(d)/'test.html';page.write_text('<title>APX disposable YouTube CPU probe</title>')
 p=subprocess.Popen(['/usr/bin/brave','--ozone-platform=wayland','--user-data-dir='+str(profile),'--remote-debugging-port=0','--remote-debugging-address=127.0.0.1','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-component-update','--disable-sync','--disable-extensions','--class=apx-youtube-cpu-probe','--new-window',page.as_uri()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 c=None;rows=[];report={}
 try:
  deadline=time.monotonic()+12
  while not (profile/'DevToolsActivePort').exists():
   if time.monotonic()>deadline:raise RuntimeError('Browser startup timeout')
   time.sleep(.05)
  port=int((profile/'DevToolsActivePort').read_text().splitlines()[0]);h=http.client.HTTPConnection('127.0.0.1',port,timeout=4);h.request('GET','/json/list');targets=json.loads(h.getresponse().read());h.close()
  target=next(t for t in targets if t.get('type')=='page' and t.get('url')==page.as_uri());c=CDP(target['webSocketDebuggerUrl'])
  c.call('Page.enable');c.call('Page.navigate',{'url':'https://www.youtube.com/watch?v=aqz-KE-bpKQ'})
  deadline=time.monotonic()+22
  while True:
   try:
    ready=c.evaluate("!!document.querySelector('.ytp-fullscreen-button') && document.querySelector('video')?.readyState>=2")
    if ready:break
    c.evaluate("(()=>{let b=[...document.querySelectorAll('button')].find(b=>/^(Reject all|Rejeitar tudo|Rejeitar todos)$/.test(b.innerText.trim()));if(b)b.click()})()")
   except RuntimeError:pass
   if time.monotonic()>deadline:raise RuntimeError('YouTube player unavailable')
   time.sleep(.4)
  time.sleep(4)
  c.evaluate("document.querySelector('.ytp-settings-button').click()")
  time.sleep(.2)
  report['ambient_setting']=c.evaluate("(()=>{let rows=[...document.querySelectorAll('.ytp-menuitem')];let row=rows.find(e=>/Ambient mode|Modo ambiente|Modo de ambiente/i.test(e.innerText));if(!row)return {available:false,labels:rows.map(e=>e.querySelector('.ytp-menuitem-label')?.textContent||'')};let before=row.getAttribute('aria-checked');if(before==='true')row.click();return {available:true,before,after:row.getAttribute('aria-checked')}})()")
  c.evaluate("(()=>{let menu=document.querySelector('.ytp-settings-menu');if(menu&&getComputedStyle(menu).display!=='none')document.querySelector('.ytp-settings-button').click()})()")
  time.sleep(.4)
  c.evaluate("(()=>{const p=window.__apxFullscreenProbe={frames:[],longFrames:[]};let last=performance.now();function frame(now){p.frames.push(now-last);last=now;requestAnimationFrame(frame)}requestAnimationFrame(frame);if(PerformanceObserver.supportedEntryTypes.includes('long-animation-frame')){new PerformanceObserver(list=>p.longFrames.push(...list.getEntries().map(e=>({duration:e.duration,blockingDuration:e.blockingDuration,scripts:e.scripts.map(s=>({duration:s.duration,forcedStyleAndLayoutDuration:s.forcedStyleAndLayoutDuration,invoker:s.invoker,sourceFunctionName:s.sourceFunctionName,sourceFile:s.sourceURL.split('?')[0].split('/').pop()}))})))).observe({type:'long-animation-frame',buffered:false})}})()")
  c.call('Profiler.enable');c.call('Profiler.setSamplingInterval',{'interval':1000})
  for cycle in range(2):
   for enter in [True,False]:
    c.evaluate('window.__apxFullscreenProbe.frames=[];window.__apxFullscreenProbe.longFrames=[]')
    c.call('Profiler.start');time.sleep(.1);c.evaluate('window.__apxFullscreenProbe.frames=[];window.__apxFullscreenProbe.longFrames=[]');t=time.monotonic()
    try:
     expression="new Promise((resolve,reject)=>{let b=document.querySelector('.ytp-fullscreen-button');if(!b)return reject(new Error('Player control unavailable'));document.addEventListener('fullscreenchange',()=>resolve(true),{once:true});b.click();setTimeout(()=>reject(new Error('Fullscreen event timeout')),4000)})" if enter else 'document.exitFullscreen()'
     c.evaluate(expression,True);promise_ms=round((time.monotonic()-t)*1000,1);time.sleep(.65)
    finally:profile_data=c.call('Profiler.stop')['profile']
    measured=c.evaluate('({frames:__apxFullscreenProbe.frames,longFrames:__apxFullscreenProbe.longFrames,fullscreen:!!document.fullscreenElement,video:{ready:document.querySelector("video")?.readyState,paused:document.querySelector("video")?.paused}})')
    nodes={n['id']:n for n in profile_data['nodes']};totals=collections.Counter()
    for ident,delta in zip(profile_data.get('samples',[]),profile_data.get('timeDeltas',[])):
     f=nodes[ident]['callFrame'];key=(f['functionName'],urlparse(f['url']).path.rsplit('/',1)[-1],f['lineNumber']);totals[key]+=delta
    top=[{'function':k[0],'file':k[1],'line':k[2],'self_ms':round(v/1000,1)} for k,v in totals.most_common(16)]
    gaps=measured.pop('frames');rows.append(dict(cycle=cycle+1,enter=enter,promise_ms=promise_ms,max_raf_gap_ms=round(max(gaps,default=0),1),profile_top=top,**measured))
 except Exception as e:report['error']=str(e)
 finally:
  report['results']=rows
  if c:
   try:c.call('Browser.close')
   except (EOFError,OSError):pass
   c.s.close()
  if p.poll() is None:
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=5)
 print(json.dumps(report,indent=2))
'''
r=subprocess.run(['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),'python','-'],input=program,text=True,capture_output=True,timeout=60)
import json
report=json.loads(r.stdout) if r.stdout.strip() else {}
print({k:v for k,v in report.items() if k!='results'})
print([(r['enter'],r['max_raf_gap_ms']) for r in report.get('results',[])])
print(r.stderr)
(Path(__file__).with_name('youtube-ambient-off-cpu-profile.json')).write_text(r.stdout)
assert r.returncode==0
