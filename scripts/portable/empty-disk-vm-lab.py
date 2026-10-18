#!/usr/bin/env python3
"""Disposable blank-disk test harness. Never opens physical disks in QEMU."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import socket
import stat
import struct
import subprocess
import sys
import time
import zlib

REPO=Path(__file__).resolve().parents[2]
OUT=REPO/'audit/2026-10-18-empty-disk'
LAB=Path('/tmp/apx-empty-disk-lab-20261018')
ROOT=Path('/var/lib/apx/test-labs/empty-disk-20261018/root')
UNIT='apx-empty-disk-lab.service'
MACHINE='apx-empty-disk-lab'
LEASE=Path('/dev/apx-empty-disk-lab')
GEN='0de1256b-dc39-4b67-82cc-30363819c36a'


def call(*args,check=True):
    return subprocess.run(args,check=check,text=True,capture_output=True)


def inside(*args,check=True):
    return call('systemd-run','-M',MACHINE,'--quiet','--wait','--pipe','--collect',*args,check=check)


def ownership():
    if os.geteuid() or Path('/proc/sys/kernel/hostname').read_text().strip()!='apx-host':
        raise ValueError('authorized pilot root only')
    reg=json.loads(Path('/var/lib/apx/environments/teste/registration.json').read_text())
    if reg['generation']!=GEN: raise ValueError('manual Teste identity changed')


def setup():
    ownership()
    if LAB.exists() or ROOT.exists() or LEASE.exists(): raise ValueError('lab already exists')
    if shutil.disk_usage('/').free < 98*1024**3: raise ValueError('physical reserve')
    LAB.mkdir(mode=0o755);os.chown(LAB,1000,1000)
    (LAB/'public').mkdir(mode=0o755);(LAB/'public').chmod(0o755)
    ROOT.parent.mkdir(parents=True)
    call('btrfs','subvolume','snapshot','/var/lib/apx/environments/teste/root',str(ROOT))
    LEASE.mkdir(mode=0o700)
    node=Path('/dev/kvm').stat()
    os.mknod(LEASE/'kvm',stat.S_IFCHR|0o600,node.st_rdev)
    call('systemd-run','--quiet','--collect','--unit='+UNIT,
         '--property=Delegate=yes','--property=KillMode=mixed','--property=TimeoutStopSec=20s',
         '--property=MemoryMax=20G','--property=MemoryHigh=18G','--property=DevicePolicy=closed','--property=DeviceAllow=/dev/kvm rw',
         'systemd-nspawn','--quiet','--keep-unit','--boot','--settings=no','--register=yes',
         '--machine='+MACHINE,'--directory='+str(ROOT),'--private-users=pick','--private-users-ownership=chown',
         '--private-network','--network-veth','--link-journal=no','--console=pipe',
         '--bind='+str(LAB)+':/lab:idmap','--bind='+str(LEASE/'kvm')+':/dev/kvm')
    for _ in range(200):
        result=call('machinectl','show',MACHINE,'--property=Leader','--value',check=False)
        if result.returncode==0 and result.stdout.strip().isdecimal():
            mapping=Path('/proc/'+result.stdout.strip()+'/uid_map').read_text().split()
            if mapping[0]!='0' or mapping[2]!='65536': raise ValueError('unexpected mapping')
            uid=int(mapping[1])+1000;os.chown(LEASE/'kvm',uid,uid);os.chmod(LEASE/'kvm',0o660)
            break
        time.sleep(.1)
    else: raise RuntimeError('container absent')
    for _ in range(100):
        if inside('/usr/bin/true',check=False).returncode==0: break
        time.sleep(.2)
    # Only new source/test-fixture files, not homes or credentials.
    call(sys.executable,str(REPO/'scripts/portable/build-bundle.py'),'--profile','graphical',str(LAB/'public/apx.tar.gz'))
    for name in ('full-vm-agent.py','full-vm-smoke.py','empty-disk-vm-install.py'):
        shutil.copy2(REPO/'scripts/portable'/name,LAB/'public'/name)
    bootstrap='''#!/bin/bash
set -e
curl -fsS http://10.0.2.2:18080/apx.tar.gz | tar xz -C /root
curl -fsS http://10.0.2.2:18080/full-vm-agent.py -o /root/full-vm-agent.py
curl -fsS http://10.0.2.2:18080/full-vm-smoke.py -o /root/full-vm-smoke.py
touch /etc/apx-disposable-full-vm
nohup python /root/full-vm-agent.py >/tmp/agent.log 2>&1 &
'''
    (LAB/'public/bootstrap.sh').write_text(bootstrap)
    for artifact in (LAB/'public').iterdir(): artifact.chmod(0o644)
    inside('systemctl','start','systemd-networkd','systemd-resolved')
    # No owner data in this server tree; private maintenance network only.
    call('systemd-run','-M',MACHINE,'--quiet','--collect','--unit=apx-empty-public',
         '--property=User=apx','/usr/bin/python','-m','http.server','18080','--bind','127.0.0.1',
         '--directory','/lab/public')
    (OUT/'lab.json').write_text(json.dumps({'unit':UNIT,'machine':MACHINE,'ram_files':str(LAB),
                                          'builder_root':str(ROOT),'retained_manual_vm_untouched':True},indent=2)+'\n')
    call('systemd-run','--quiet','--collect','--unit=apx-empty-disk-budget',
         '--property=MemoryMax=128M','/usr/bin/python',str(Path(__file__).resolve()),'guard')


def start(mode):
    ownership()
    iso=LAB/'arch.iso'
    live=mode.endswith('live')
    bios=mode.startswith('bios-')
    if live:
        source=iso if iso.exists() else Path('/tmp/apx-archlinux-2026.10.01.iso')
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        if digest!='684ded26c63240ff4a41e8c25ee84ea6da233f557364821f13d12c2b0a9059a5':
            raise ValueError('official ISO checksum mismatch')
        if source!=iso: source.rename(iso)
        iso.chmod(0o444)
        with (LAB/'disk.raw').open('xb') as stream: stream.truncate(180*1024**3)
        os.chown(LAB/'disk.raw',1000,1000)
        if not bios:
            shutil.copy2(ROOT/'usr/share/edk2/x64/OVMF_VARS.4m.fd',LAB/'vars.fd');os.chown(LAB/'vars.fd',1000,1000)
    for name in ('qmp.sock','agent.sock','console.sock'): (LAB/name).unlink(missing_ok=True)
    command=['/usr/bin/qemu-system-x86_64','-name','APX Empty Disk Rehearsal','-machine',('pc' if bios else 'q35')+',accel=kvm',
             '-cpu','host','-m','6144','-smp','4','-nodefaults','-display','none']
    if not bios:
        command+=['-drive','if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.4m.fd',
                  '-drive','if=pflash,format=raw,file=/lab/vars.fd']
    command+=[
             '-drive','if=none,id=disk,format=raw,discard=unmap,detect-zeroes=unmap,file=/lab/disk.raw',
             '-device','virtio-blk-pci,drive=disk','-device','virtio-vga','-device','qemu-xhci',
             '-device','usb-kbd','-device','usb-tablet','-netdev','user,id=n0','-device','virtio-net-pci,netdev=n0',
             '-device','virtio-serial-pci','-chardev','socket,id=lab,path=/lab/agent.sock,server=on,wait=off',
             '-device','virtserialport,chardev=lab,name=apx.lab',
             '-qmp','unix:/lab/qmp.sock,server=on,wait=off','-serial','file:/lab/serial-'+mode+'.log']
    if live: command+=['-drive','if=none,id=cd,media=cdrom,readonly=on,file=/lab/arch.iso',
                              '-device','ide-cd,drive=cd','-boot','order=d']
    else: command+=['-boot','order=c']
    (OUT/('qemu-'+mode+'.json')).write_text(json.dumps(command,indent=2)+'\n')
    call('systemd-run','-M',MACHINE,'--quiet','--collect','--unit=apx-empty-vm',
         '--property=User=apx','--property=MemoryMax=18G','--property=MemoryHigh=16G','--property=KillMode=mixed',*command)


def qmp(execute,arguments=None):
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as sock:
        sock.settimeout(10);sock.connect(str(LAB/'qmp.sock'))
        stream=sock.makefile('rwb',buffering=0);stream.readline()
        for request in [{'execute':'qmp_capabilities'},{'execute':execute,**({'arguments':arguments} if arguments else {})}]:
            stream.write((json.dumps(request)+'\n').encode())
            while True:
                result=json.loads(stream.readline())
                if 'return' in result or 'error' in result: break
        if 'error' in result: raise RuntimeError(result)
        return result


def type_text(text):
    names={' ':'spc','\n':'ret','/':'slash','-':'minus','.':'dot',':':'shift-semicolon',
           '|':'shift-backslash','>':'shift-dot','_':'shift-minus','=':'equal','&':'shift-7'}
    # QEMU's human monitor key notation, commands only; never owner credentials.
    for char in text:
        key=names.get(char, 'shift-'+char.lower() if char.isupper() else char)
        qmp('human-monitor-command',{'command-line':'sendkey '+key+' 1'})
        time.sleep(.025)


def screenshot():
    qmp('screendump',{'filename':'/lab/screen.ppm'})
    parts=(LAB/'screen.ppm').read_bytes().split(b'\n',3)
    if parts[0]!=b'P6' or parts[2]!=b'255': raise ValueError('unexpected QMP screenshot')
    width,height=map(int,parts[1].split());raw=parts[3]
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    pixels=b''.join(b'\0'+raw[y*width*3:(y+1)*width*3] for y in range(height))
    (LAB/'screen.png').write_bytes(b'\x89PNG\r\n\x1a\n'+
        chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+
        chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b''))


def guest(args,timeout=600):
    spec=importlib.util.spec_from_file_location('old_lab',REPO/'scripts/portable/full-vm-lab.py')
    lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
    lab.GENERATION=GEN;lab.VM=LAB
    return lab.guest(args,timeout)


def cleanup():
    ownership()
    call('systemctl','stop','apx-empty-disk-budget.service',check=False)
    call('systemctl','stop',UNIT,check=False)
    if call('machinectl','show',MACHINE,check=False).returncode==0: raise ValueError('container remains')
    if ROOT.exists(): call('btrfs','subvolume','delete',str(ROOT))
    if LEASE.exists(): (LEASE/'kvm').unlink();LEASE.rmdir()
    if LAB.exists():
        for log in LAB.glob('serial-*.log'): shutil.copy2(log,OUT/log.name)
        shutil.rmtree(LAB)
    if ROOT.parent.exists(): ROOT.parent.rmdir()


def guard():
    ownership()
    while call('systemctl','is-active','--quiet',UNIT,check=False).returncode==0:
        available=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines()
                           if line.startswith('MemAvailable:')))*1024
        values={'host_free':shutil.disk_usage('/').free,'tmp_free':shutil.disk_usage(LAB).free,
                'memory_available':available}
        if values['host_free']<97*1024**3 or values['tmp_free']<512*1024**2 or available<2*1024**3:
            (OUT/'resource-guard-stop.json').write_text(json.dumps(values,indent=2)+'\n')
            call('systemctl','stop',UNIT,check=False);return
        time.sleep(2)


if __name__=='__main__':
    action=sys.argv[1]
    if action=='setup': setup()
    elif action=='start': start(sys.argv[2])
    elif action=='type': type_text(sys.argv[2])
    elif action=='command': print(json.dumps(guest(sys.argv[2:]),indent=2))
    elif action=='screenshot': screenshot()
    elif action=='cleanup': cleanup()
    elif action=='guard': guard()
    else: raise SystemExit('setup | start live/installed | type | command | screenshot | cleanup')
