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
session = cmd('WebDriver:NewSession',{})
assert session['capabilities']['moz:profile'].endswith('/apx-thunderbird-responsive-check')
cmd('Marionette:SetContext',{'value':'chrome'})
def js(script):return cmd('WebDriver:ExecuteScript',{'script':script,'args':[]})['value']
