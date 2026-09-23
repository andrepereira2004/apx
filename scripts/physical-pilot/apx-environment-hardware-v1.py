#!/usr/bin/env python3
"""Bounded display, keyboard lighting and energy profile for active workloads."""
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import select
import socket
import struct
import sys
import threading
sys.path.insert(0,'/usr/lib/apx')
from apx_host_services_peer import HostServicesPeer, authorize_active_environment_peer, ACTIVE_ENVIRONMENT, _json
from apx_active_shell_peer import quickshell_ancestor
from apx_system_power_contract import PROFILE, parse_message

spec=importlib.util.spec_from_file_location('hardware_base',Path(__file__).with_name('apx-system-power-v1.py'))
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
SOCKET=Path('/run/apx/environment-hardware-v1.sock')
ALLOWED={'hardware.profile.status','hardware.platform.set','hardware.display.set','hardware.keyboard.cycle'}
LOCK=threading.Lock()
POWER_OPS={'system.poweroff.prepare','system.action.confirm','system.action.cancel'}
POWER_IDENTITY=None

def apply_power(operation,payload,peer,identity):
    global POWER_IDENTITY
    base.expire_pending()
    expected=set() if operation=='system.poweroff.prepare' else {'token'}
    if set(payload)!=expected: raise ValueError('power payload fields differ')
    shell=quickshell_ancestor(peer)
    shell_start=Path(f'/proc/{shell}/stat').read_text().rsplit(')',1)[1].split()[19]
    binding=(identity, shell, shell_start)
    if authorize_active_environment_peer(peer)!=identity: raise PermissionError('active identity changed')
    if operation!='system.poweroff.prepare' and POWER_IDENTITY!=binding:
        raise PermissionError('power confirmation Environment generation differs')
    result=base.apply(operation,payload,peer,shell)
    if operation=='system.poweroff.prepare' and result.get('prepared'): POWER_IDENTITY=binding
    if base.PENDING is None: POWER_IDENTITY=None
    print(json.dumps(dict(operation=operation,environment=identity.name,generation=identity.generation,result='handled',peer_uid=peer.uid)),flush=True)
    return result



def apply(operation,payload,peer):
    identity=authorize_active_environment_peer(peer)
    if identity.role!='graphical-base' or operation not in ALLOWED | POWER_OPS:
        raise PermissionError('operation is not an active Environment hardware control')
    if type(payload) is not dict:
        raise ValueError('hardware payload differs')
    if operation in POWER_OPS: return apply_power(operation,payload,peer,identity)
    keys={'hardware.profile.status':set(),'hardware.keyboard.cycle':set(),
          'hardware.platform.set':{'profile'},'hardware.display.set':{'percent'}}
    if set(payload)!=keys[operation]:raise ValueError('hardware payload fields differ')
    if operation=='hardware.profile.status':return base.hardware_profile_status()
    quickshell_ancestor(peer)
    with open('/run/apx/machine-transition-v1.lock','a') as transition:
        fcntl.flock(transition,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if authorize_active_environment_peer(peer)!=identity:raise PermissionError('active identity changed')
        if Path('/run/apx/system-power-v1.reserved').exists():raise RuntimeError('power transition pending')
        if operation=='hardware.platform.set':
            if type(payload['profile']) is not str:raise ValueError('platform profile differs')
            result=base.set_platform_profile(payload['profile'])
        elif operation=='hardware.display.set':result=base.set_display_brightness(payload['percent'])
        else:result=base.cycle_keyboard_brightness()
    print(json.dumps(dict(operation=operation, environment=identity.name, generation=identity.generation, result='applied', peer_uid=peer.uid)), flush=True)
    return result


def handle(connection):
    try:
        pid,uid,gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
        peer=HostServicesPeer(pid,uid,gid)
        request=parse_message(base.receive(connection))
        with LOCK:result=apply(request.get('operation'),request.get('payload'),peer)
        response=dict(schema=1,profile=PROFILE,ok=True,result=result,error=None)
    except Exception as e:
        response=dict(schema=1,profile=PROFILE,ok=False,result=None,error=dict(code='request_rejected',message=str(e)[:300]))
    try:connection.sendall((json.dumps(response,separators=(',',':'))+'\n').encode())
    except OSError:pass


def serve():
    endpoints=[(SOCKET,0)]
    # Existing-session alias avoids a compositor restart solely to add a bind.
    # The parent is Host-owned and not writable by the Environment user.
    identity=None
    try:
        if ACTIVE_ENVIRONMENT.exists():
            state=_json(ACTIVE_ENVIRONMENT);pid=state['pid']
            fields=Path(f'/proc/{pid}/uid_map').read_text().split()
            uid=int(fields[1])+1000
            identity=authorize_active_environment_peer(HostServicesPeer(pid,uid,uid))
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        identity=None
        print("Live hardware alias unavailable: " + str(error)[:200], flush=True)
    if identity is not None and identity.role=='graphical-base':
        parent=Path('/var/lib/apx/environments')/identity.name/'home/.apx-hardware-bridge'
        if parent.is_symlink():raise RuntimeError('hardware bridge directory differs')
        parent.mkdir(mode=0o755,exist_ok=True)
        if parent.stat().st_uid!=0 or parent.stat().st_mode&0o022:raise RuntimeError('hardware bridge ownership differs')
        os.chmod(parent,0o755)
        endpoints.append((parent/'hardware-v1.sock',(parent.parent/'apx').stat().st_uid))
    servers=[]
    try:
        for path,uid in endpoints:
            path.parent.mkdir(mode=0o755,parents=True,exist_ok=True)
            if path.exists():
                if not path.is_socket() or path.is_symlink():raise RuntimeError('hardware socket path differs')
                path.unlink()
            server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind(str(path))
            os.chown(path,uid,uid);os.chmod(path,0o660 if uid else 0o600);server.listen(8);servers.append(server)
        while True:
            ready,_,_=select.select(servers,(),(),1)
            with LOCK: base.expire_pending()
            for server in ready:
                connection,_=server.accept()
                with connection:
                    connection.settimeout(3);handle(connection)
    finally:
        for server in servers:server.close()

if __name__=='__main__':serve()
