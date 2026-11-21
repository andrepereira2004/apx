#!/usr/bin/env python3
"""Recorded, 24-GiB-capped disposable clean-VM rehearsal on this pilot."""
import importlib.util
import json
import os
from pathlib import Path
import sys

REPO=Path(__file__).resolve().parents[2]
OUT=REPO/'audit/2026-11-21-portable-v3'
intent=json.loads((OUT/'intent.json').read_text())
spec=importlib.util.spec_from_file_location('portable_v3_lab_core',Path(__file__).with_name('full-vm-lab.py'))
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
lab.OUT=OUT if intent.get("replay",1)==1 else OUT/("replay"+str(intent["replay"]))
lab.GENERATION=intent['generation']
lab.ENVIRONMENT=Path('/var/lib/apx/environments')/intent['name']
lab.MAINTENANCE_ROOT=lab.ENVIRONMENT/'root'
lab.HOME=lab.ENVIRONMENT/'home/apx'
lab.VM=lab.HOME/'VMs/APX-Rebuild'
lab.LEASE=Path('/dev/codex-test-portable-v3-kvm')
lab.MACHINE='apx-codex-v3'
lab.UNIT='codex-test-portable-v3-lab.service'
lab.GUARD_ENTRYPOINT=Path(__file__).resolve()
original_call=lab.call

def call(*args,**kwargs):
    args=tuple(x.replace('apx-portable-rehearsal-budget.service','codex-test-portable-v3-budget.service') if isinstance(x,str) else x for x in args)
    return original_call(*args,**kwargs)
lab.call=call

def assert_test():
    if os.geteuid() or Path('/proc/sys/kernel/hostname').read_text().strip()!='apx-host':
        raise ValueError('recorded pilot root only')
    path=lab.ENVIRONMENT/'registration.json'
    if path.is_symlink() or path.stat().st_uid or path.stat().st_mode&0o022:
        raise ValueError('untrusted disposable registration')
    record=json.loads(path.read_text())
    if (record.get('name'),record.get('generation'),record.get('role'))!=(intent['name'],intent['generation'],'development'):
        raise ValueError('disposable test identity changed')
    return record
lab.assert_test=assert_test

if __name__=='__main__':
    assert_test()
    if sys.argv[1]=='prepare':
        if intent.get('replay',1)>1:
            # The outer, recorded test container and its KVM proxy stay owned.
            # Only a fresh sparse guest image is rebuilt.
            lab.LEASE=Path('/dev/codex-test-portable-v3-unused')
            lab.attach=lambda:None
        lab.prepare()
    elif sys.argv[1]=='start':lab.start('q35')
    elif sys.argv[1]=='guard':lab.guard()
    elif sys.argv[1]=='command':print(json.dumps(lab.guest(sys.argv[2:],timeout=600),indent=2))
    else:raise SystemExit('prepare | start | guard | command')
