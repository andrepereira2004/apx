import socket,json,base64
from pathlib import Path
s=socket.create_connection(('127.0.0.1',2829),3)
def recv():
    n=b''
    while (c:=s.recv(1))!=b':': n+=c
    out=b''
    while len(out)<int(n):out+=s.recv(int(n)-len(out))
    return json.loads(out)
i=0
recv()
def cmd(name,data):
    global i
    i+=1;b=json.dumps([0,i,name,data]).encode();s.sendall(str(len(b)).encode()+b':'+b);r=recv()
    if r[2]:raise RuntimeError(r[2])
    return r[3]
cmd('WebDriver:NewSession',{})
cmd('Marionette:SetContext',{'value':'chrome'})
def js(script):return cmd('WebDriver:ExecuteScript',{'script':script,'args':[]})['value']
r=js('''let w=Services.wm.getMostRecentWindow("mail:3pane");let d=w.document.getElementById("tabmail").currentAbout3Pane.document;
return {outer:innerWidth,threePane:d.documentURI,rootColor:d.defaultView.getComputedStyle(d.documentElement).getPropertyValue("--layout-background-0"),folderFont:d.defaultView.getComputedStyle(d.getElementById("folderPane")).fontFamily,folderBg:d.defaultView.getComputedStyle(d.getElementById("folderPane")).backgroundColor,styleSheets:[...d.styleSheets].map(s=>s.href),folderWidth:d.getElementById("folderPane").getBoundingClientRect().width};''')
print(json.dumps(r,indent=2))
Path(__file__).with_name('computed-preview.json').write_text(json.dumps(r,indent=2)+'\n')
image=cmd('WebDriver:TakeScreenshot',{'id':None,'full':False,'hash':False})['value']
Path(__file__).with_name('preview.png').write_bytes(base64.b64decode(image))
