from pathlib import Path
import json,base64,glob,os,socket,time
HERE=Path(__file__).resolve().parent
exec((HERE/'preview-client.py').read_text())
css=(HERE.parents[1]/'config/thunderbird-graphite-v1/graphite.css').read_text()
js('''let s=Cc["@mozilla.org/content/style-sheet-service;1"].getService(Ci.nsIStyleSheetService);s.loadAndRegisterSheet(Services.io.newURI("data:text/css;charset=utf-8,"+encodeURIComponent('''+json.dumps(css)+''')),s.USER_SHEET);return true;''')
# Only the disposable offline process is controlled by this helper.
pid=session['capabilities']['moz:processID']
def query(command):
    old=os.getcwd()
    try:
        os.chdir(glob.glob('/proc/4246/root/run/apx/session-1000/hypr/*')[0]);sock=socket.socket(socket.AF_UNIX);sock.settimeout(3);sock.connect('.socket.sock');sock.send(command.encode());data=b''
        while c:=sock.recv(65536):data+=c
        sock.close()
        try:return json.loads(data)
        except json.JSONDecodeError:return data.decode()
    finally:os.chdir(old)
js('let w=Services.wm.getMostRecentWindow("mail:3pane"),t=w.document.getElementById("tabmail");w.fullScreen=false;Services.prefs.setIntPref("mail.pane_config.dynamic",0);if(t.tabInfo.length==1)t.openTab("addressBookTab");return true;')
time.sleep(.5)
preview=next(c for c in query('j/clients') if c['pid']==pid)
multi=js('''let w=Services.wm.getMostRecentWindow("mail:3pane"),t=w.document.getElementById("tabmail");return {tabs:t.tabInfo.length,display:w.getComputedStyle(w.document.getElementById("tabs-toolbar")).display};''')
assert multi['tabs']==2 and multi['display']!='none'
js('''let t=Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail");t.closeTab(1);let a=t.currentAbout3Pane;a.threadTree.selectedIndex=0;a.threadTree.dispatchEvent(new a.Event("select"));return true;''')
time.sleep(.5)
def capture(name):
    result=js('''let w=Services.wm.getMostRecentWindow("mail:3pane"),t=w.document.getElementById("tabmail"),a=t.currentAbout3Pane,d=a.document;let el=id=>d.getElementById(id),rect=id=>{let r=el(id).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};return {width:innerWidth,layout:d.body.className,tabs:t.tabInfo.length,tabsDisplay:w.getComputedStyle(w.document.getElementById("tabs-toolbar")).display,font:a.getComputedStyle(el("folderPane")).fontFamily,folder:rect("folderPane"),threads:rect("threadPane"),message:rect("messagePane"),rowActionsOpacity:a.getComputedStyle(d.querySelector(".card-layout:not(.current) .tree-button-more")).opacity,bodyFont:a.document.getElementById("messageBrowser").contentDocument.getElementById("messagepane")?.contentDocument?.body?.style.fontFamily,subject:d.querySelector(".card-layout .subject").textContent};''')
    assert result['tabsDisplay']=='none'
    result['multipleTabs']=multi
    (HERE/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    data=cmd('WebDriver:TakeScreenshot',{'id':None,'full':False,'hash':False})['value']
    (HERE/(name+'.png')).write_bytes(base64.b64decode(data))
    print(name,json.dumps(result))
capture('clean-small')
js('Services.wm.getMostRecentWindow("mail:3pane").fullScreen=true;return true;')
js('Services.prefs.setIntPref("mail.pane_config.dynamic",2);return true;')
time.sleep(1)
capture('clean-wide')
