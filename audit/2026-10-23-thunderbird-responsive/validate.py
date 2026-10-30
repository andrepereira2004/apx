from pathlib import Path
import json,glob,socket,os,base64,time
HERE=Path(__file__).resolve().parent
exec((HERE/'preview-client.py').read_text())
pid=session['capabilities']['moz:processID']
def query(command):
 old=os.getcwd()
 try:
  os.chdir(glob.glob('/proc/4246/root/run/apx/session-1000/hypr/*')[0]);q=socket.socket(socket.AF_UNIX);q.connect('.socket.sock');q.send(command.encode());out=b''
  while c:=q.recv(65536):out+=c
  q.close()
  try:return json.loads(out)
  except:return out.decode()
 finally:os.chdir(old)
c=next(c for c in query('j/clients') if c['pid']==pid)
if not c['floating']:
 assert query('dispatch hl.dsp.window.float({action="toggle",window="address:'+c['address']+'"})').strip()=='ok'
js('let w=Services.wm.getMostRecentWindow("mail:3pane");w.resizeTo(740,780);return true;')
time.sleep(.6)
def geometry():
 return js('''let a=Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail").currentAbout3Pane,d=a.document;let rect=id=>{let r=d.getElementById(id).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};return {width:innerWidth,folder:rect("folderPane"),threads:rect("threadPane"),message:rect("messagePane"),splitter:a.getComputedStyle(d.getElementById("messagePaneSplitter")).display};''')
r=geometry();assert r['width']<1100,r;assert r['folder']['width']>=219;assert r['message']['y']>r['threads']['y']+100,r;assert r['message']['x']+r['message']['width']<=r['width']+1,r
(HERE/'half-window.json').write_text(json.dumps(r,indent=2)+'\n')
(HERE/'half-window.png').write_bytes(base64.b64decode(cmd('WebDriver:TakeScreenshot',{'id':None,'full':False,'hash':False})['value']))
print('Half',r)
# F8/collapse state keeps the message list usable and fills the available height.
js('let a=Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail").currentAbout3Pane;a.paneLayout.messagePaneSplitter.isCollapsed=true;return true;')
time.sleep(.1);collapsed=geometry();assert collapsed['threads']['height']>r['threads']['height']+100
js('let a=Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail").currentAbout3Pane;a.paneLayout.messagePaneSplitter.isCollapsed=false;Services.wm.getMostRecentWindow("mail:3pane").fullScreen=true;return true;')
time.sleep(.8);wide=geometry();assert wide['width']>1100;assert wide['message']['x']>wide['threads']['x']+100;assert wide['splitter']!='none'
(HERE/'wide-window.json').write_text(json.dumps(wide,indent=2)+'\n');print('Wide',wide)
(HERE/'wide-window.png').write_bytes(base64.b64decode(cmd('WebDriver:TakeScreenshot',{'id':None,'full':False,'hash':False})['value']))
