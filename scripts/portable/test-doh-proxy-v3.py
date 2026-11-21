#!/usr/bin/python
"""TEST ONLY: DNS-over-HTTPS for this disposable lab's UDP-restricted uplink."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import socket
import urllib.request

if __name__=='__main__':
    if Path('/run/systemd/container').read_text().strip()!='systemd-nspawn' or Path('/root/apx-disposable-doh-fixture').read_text().strip()!='codex-test-portable-v3':
        raise SystemExit('recorded disposable lab only')
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as server, ThreadPoolExecutor(max_workers=8) as workers:
        server.bind(('127.0.0.53',53))
        def answer(query,peer):
            try:
                request=urllib.request.Request('https://1.1.1.1/dns-query',data=query,headers={'Content-Type':'application/dns-message','Accept':'application/dns-message'})
                with urllib.request.urlopen(request,timeout=15) as response:data=response.read(65536)
                if len(data)>=12:server.sendto(query[:2]+data[2:],peer)
            except Exception:
                if len(query)>=12:server.sendto(query[:2]+b'\x81\x82'+query[4:6]+b'\0'*6+query[12:],peer)
        while True:
            query,peer=server.recvfrom(4096)
            workers.submit(answer,query,peer)
