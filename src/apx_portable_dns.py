"""Bounded per-veth DNS wire proxy to a fixed HTTPS resolver.

No query logging, arbitrary upstream URL, private-network forwarding or Host
resolver-file sharing. This is part of the experimental portable profile.
"""
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import json
import os
import re
import signal
import socket
import struct
import subprocess
import threading
import time
import urllib.request

UPSTREAM='https://1.1.1.1/dns-query'
MAX_QUERY=4096
MAX_RESPONSE=65535
INTERFACE=re.compile(r've-apx-[A-Za-z0-9_.-]{1,8}')
PRIVATE=tuple(ipaddress.IPv4Network(value) for value in ['10.0.0.0/8','172.16.0.0/12','192.168.0.0/16'])


def question(data):
    if not isinstance(data,bytes) or not 17<=len(data)<=MAX_QUERY:
        raise ValueError('invalid DNS query size')
    _,flags,questions,answers,authority,additional=struct.unpack('!6H',data[:12])
    if flags&0xf800 or questions!=1 or answers or authority or additional>1:
        raise ValueError('only ordinary single-question DNS queries are supported')
    position=12;labels=0
    while True:
        if position>=len(data):raise ValueError('truncated DNS name')
        size=data[position];position+=1
        if size==0:break
        if size>63 or position+size>len(data):raise ValueError('compressed or invalid DNS question name')
        position+=size;labels+=1
        if position-12>255 or labels>127:raise ValueError('oversized DNS name')
    if position+4>len(data):raise ValueError('missing DNS question type')
    kind,class_=struct.unpack('!2H',data[position:position+4])
    if class_!=1 or kind in {0,251,252,255}:raise ValueError('zone transfers and bulk queries are refused')
    return position+4


def response_header(query,code=2,truncated=False):
    end=question(query)
    flags=0x8080|(struct.unpack('!H',query[2:4])[0]&0x0100)|code
    if truncated:flags|=0x0200
    return query[:2]+struct.pack('!5H',flags,1,0,0,0)+query[12:end]


def resolve(query):
    question(query)
    request=urllib.request.Request(UPSTREAM,data=query,
        headers={'Content-Type':'application/dns-message','Accept':'application/dns-message'})
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request,timeout=10) as response:
        if response.url!=UPSTREAM or response.headers.get_content_type()!='application/dns-message':
            raise ValueError('DNS upstream identity or content type changed')
        data=response.read(MAX_RESPONSE+1)
    if not 12<=len(data)<=MAX_RESPONSE or not (data[2]&0x80):raise ValueError('invalid DNS upstream response')
    return query[:2]+data[2:]


def gateways(records):
    result={}
    for link in records:
        name=link.get('ifname','')
        if not INTERFACE.fullmatch(name) or link.get('linkinfo',{}).get('info_kind')!='veth':continue
        candidates=[a for a in link.get('addr_info',[]) if a.get('family')=='inet' and a.get('scope')=='global']
        if len(candidates)!=1:continue
        item=candidates[0];address=ipaddress.IPv4Address(item['local']);prefix=item['prefixlen']
        if type(prefix) is not int or prefix!=28 or not any(address in network for network in PRIVATE):continue
        network=ipaddress.IPv4Network(f'{address}/{prefix}',strict=False)
        if address in {network.network_address,network.broadcast_address}:continue
        result[name]=(str(address),network)
    return result


class Gateway:
    def __init__(self,name,address,network,workers,slots):
        self.network=network;self.address=address;self.workers=workers;self.slots=slots
        self.closed=threading.Event();self.sockets=[];self.rates={};self.rate_lock=threading.Lock()
        try:
            for kind in [socket.SOCK_DGRAM,socket.SOCK_STREAM]:
                server=socket.socket(socket.AF_INET,kind)
                self.sockets.append(server)
                server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                server.setsockopt(socket.SOL_SOCKET,socket.SO_BINDTODEVICE,name.encode()+b'\0')
                server.bind((address,53));server.settimeout(1)
                if kind==socket.SOCK_STREAM:server.listen(16)
                threading.Thread(target=self.listen,args=(server,kind),daemon=True).start()
        except BaseException:
            self.close();raise

    def admitted(self,peer):
        address=ipaddress.IPv4Address(peer[0])
        if address not in self.network or str(address)==self.address or address in {self.network.network_address,self.network.broadcast_address}:return False
        now=time.monotonic()
        with self.rate_lock:
            started,count=self.rates.get(str(address),(now,0))
            if now-started>=1:started,count=now,0
            self.rates[str(address)]=(started,count+1)
            return count<32

    def listen(self,server,kind):
        while not self.closed.is_set():
            client=None
            try:
                if kind==socket.SOCK_DGRAM:data,peer=server.recvfrom(MAX_QUERY+1)
                else:client,peer=server.accept();data=None
                if not self.admitted(peer) or not self.slots.acquire(blocking=False):
                    if client:client.close()
                    continue
                self.workers.submit(self.answer,server,client,data,peer)
            except socket.timeout:continue
            except OSError:return

    def answer(self,server,client,data,peer):
        try:
            if client:
                client.settimeout(3)
                header=client.recv(2)
                while len(header)<2:
                    part=client.recv(2-len(header))
                    if not part:return
                    header+=part
                length=struct.unpack('!H',header)[0]
                if not 17<=length<=MAX_QUERY:return
                data=b''
                while len(data)<length:
                    chunk=client.recv(length-len(data))
                    if not chunk:return
                    data+=chunk
            try:reply=resolve(data)
            except Exception:reply=response_header(data)
            if client:client.sendall(struct.pack('!H',len(reply))+reply)
            else:
                if len(reply)>1232:reply=response_header(data,code=0,truncated=True)
                server.sendto(reply,peer)
        except (OSError,ValueError):pass
        finally:
            if client:client.close()
            self.slots.release()

    def close(self):
        self.closed.set()
        for server in self.sockets:server.close()


def main():
    if os.geteuid():raise PermissionError('Host root required')
    stopping=threading.Event();active={}
    for sig in [signal.SIGTERM,signal.SIGINT]:signal.signal(sig,lambda *_:stopping.set())
    slots=threading.BoundedSemaphore(16)
    with ThreadPoolExecutor(max_workers=8) as workers:
        try:
            while not stopping.is_set():
                result=subprocess.run(['/usr/bin/ip','-j','-d','-4','address','show'],check=True,capture_output=True,text=True,timeout=5)
                desired=gateways(json.loads(result.stdout))
                for name,(key,server) in list(active.items()):
                    if desired.get(name)!=key:server.close();del active[name]
                for name,key in desired.items():
                    if name not in active:
                        try:active[name]=(key,Gateway(name,*key,workers,slots))
                        except OSError:pass
                stopping.wait(.5)
        finally:
            for _,server in active.values():server.close()


if __name__=='__main__':main()
