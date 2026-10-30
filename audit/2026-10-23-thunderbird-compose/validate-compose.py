from pathlib import Path
import json,base64
REPO=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
exec((REPO/'audit/2026-10-23-thunderbird-clean/preview-client.py').read_text())
assert session['capabilities']['moz:profile'].endswith('/apx-thunderbird-clean-check')
css=(REPO/'config/thunderbird-graphite-v1/graphite.css').read_text()
content=(REPO/'config/thunderbird-graphite-v1/compose-content.css').read_text()
script='''let w=Services.wm.getMostRecentWindow("msgcompose"),e=w.document.getElementById("messageEditor"),before=e.contentDocument.body.outerHTML;
let s=Cc["@mozilla.org/content/style-sheet-service;1"].getService(Ci.nsIStyleSheetService);
for(let css of '''+json.dumps([css,content])+''')s.loadAndRegisterSheet(Services.io.newURI("data:text/css;charset=utf-8,"+encodeURIComponent(css)),s.USER_SHEET);
return {htmlUnchanged:before===e.contentDocument.body.outerHTML,subjectBg:w.getComputedStyle(w.document.getElementById("msgSubject")).backgroundColor,recipientBg:w.getComputedStyle(w.document.getElementById("toAddrContainer")).backgroundColor,editorBg:e.contentWindow.getComputedStyle(e.contentDocument.body).backgroundColor,editorUri:e.contentDocument.documentURI};'''
r=js(script);assert r['htmlUnchanged'];assert r['subjectBg']=='rgb(21, 23, 32)';assert r['editorBg']=='rgb(16, 17, 23)'
# Fill only an offline disposable composer; never invoke sending or save a draft.
js('''let w=Services.wm.getMostRecentWindow("msgcompose");w.addressRowAddRecipientsArray(w.document.getElementById("addressRowTo"),["Preview <preview@example.invalid>"]);w.document.getElementById("toAddrInput").value="";let subject=w.document.getElementById("msgSubject");subject.value="Reuniao de projeto";subject.dispatchEvent(new w.Event("input",{bubbles:true}));w.GetCurrentEditor().selectAll();w.GetCurrentEditor().insertText("Ola,\\n\\nPodemos combinar a proxima reuniao de projeto?\\n\\nObrigado!");return true;''')
h=cmd('WebDriver:GetWindowHandles',{});cmd('WebDriver:SwitchToWindow',{'handle':h[-1]})
(HERE/'after-small.png').write_bytes(base64.b64decode(cmd('WebDriver:TakeScreenshot',{'id':None,'full':False,'hash':False})['value']))
r['small']=js('''let w=Services.wm.getMostRecentWindow("msgcompose");return {width:w.innerWidth,height:w.innerHeight,body:w.document.getElementById("messageEditor").getBoundingClientRect().height,ccButtonVisible:w.document.getElementById("addr_ccShowAddressRowButton").getBoundingClientRect().width>0};''')
js('''let w=Services.wm.getMostRecentWindow("msgcompose");w.showAndFocusAddressRow("addressRowCc");return true;''')
r['ccFieldAvailable']=js('''let w=Services.wm.getMostRecentWindow("msgcompose");return w.document.getElementById("addressRowCc").getBoundingClientRect().height>0;''')
assert r['ccFieldAvailable']
(HERE/'computed-compose.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
js('Services.wm.getMostRecentWindow("msgcompose").fullScreen=true;return true;')
