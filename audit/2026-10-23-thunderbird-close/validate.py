from pathlib import Path
import json,time,base64
HERE=Path(__file__).resolve().parent
exec((HERE/'preview-client.py').read_text())
css=(HERE.parents[1]/'config/thunderbird-graphite-v1/graphite.css').read_text()
js('''let s=Cc["@mozilla.org/content/style-sheet-service;1"].getService(Ci.nsIStyleSheetService);s.loadAndRegisterSheet(Services.io.newURI("data:text/css;charset=utf-8,"+encodeURIComponent('''+json.dumps(css)+''')),s.USER_SHEET);return true;''')
def state():return js('''let t=Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail"),a=t.currentAbout3Pane;return {tabs:t.tabInfo.length,collapsed:a.paneLayout.messagePaneSplitter.isCollapsed,selected:a.threadTree.selectedIndex,count:a.gFolder.getTotalMessages(false)};''')
before=state();assert not before['collapsed'] and before['selected']==0
(HERE/'button.png').write_bytes(base64.b64decode(cmd('WebDriver:TakeScreenshot',{'id':None,'full':False,'hash':False})['value']))
js('''let a=Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail").currentAbout3Pane;let d=a.document.getElementById("messageBrowser").contentDocument;d.querySelector('[data-extensionid="apx-close-message@apx.local"]').click();return true;''')
time.sleep(.4);closed=state();assert closed['collapsed'] and closed['selected']==-1;assert closed['count']==before['count']
js('''let a=Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail").currentAbout3Pane;a.threadTree.selectedIndex=0;a.threadTree.dispatchEvent(new a.Event("select"));return true;''')
time.sleep(.4);reopened=state();assert not reopened['collapsed'] and reopened['selected']==0
js('''let t=Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail"),a=t.currentAbout3Pane;t.openTab("mailMessageTab",{messageURI:a.gDBView.getURIForViewIndex(0)});return true;''')
time.sleep(.5)
assert js('return Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail").tabInfo.length;')==before['tabs']+1
js('''let t=Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail");t.currentTabInfo.chromeBrowser.contentDocument.querySelector('[data-extensionid="apx-close-message@apx.local"]').click();return true;''')
time.sleep(.4);afterTab=state();assert afterTab['tabs']==before['tabs'];assert afterTab['count']==before['count']
r={'before':before,'closed':closed,'reopenedSameMessage':reopened,'messageTabClosed':afterTab}
(HERE/'validated.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
