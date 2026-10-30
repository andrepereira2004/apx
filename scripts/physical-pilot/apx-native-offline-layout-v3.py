#!/usr/bin/env python3
"""Validate exact maintenance GPT preconditions; no writes."""
import json
import stat
from pathlib import Path
import sys
sys.path.insert(0,'/usr/lib/apx')
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from apx_native_instances_v3 import validate_plan, canonical_layout

def validate(observed,plan,action,phase='start'):
    plan=validate_plan(plan)
    if action not in {'relocate','rollback'}:raise ValueError('unknown offline action')
    if phase not in {'start','result'}:raise ValueError('unknown offline validation phase')
    expected=plan['before'] if (action=='relocate') == (phase=='start') else plan['after']
    if canonical_layout(observed)!=canonical_layout(expected):
        raise ValueError('disk topology differs from the authorized '+('starting' if phase=='start' else 'result')+' layout')
    return True

def authorize(path,plan,action):
    plan=validate_plan(plan)
    info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or stat.S_IMODE(info.st_mode)!=0o400 or info.st_size>4096:
        raise ValueError('offline authorization is untrusted')
    value=json.loads(path.read_bytes())
    expected=dict(schema=3,profile='apx-native-offline-authorization-v3',
                  generation=plan['new']['generation'],plan_sha256=plan['plan_sha256'],
                  action=action,state='approved')
    if value!=expected:raise ValueError('offline authorization differs')
    return True

if __name__=='__main__':
    if sys.argv[1]=='--authorize':
        if len(sys.argv)!=5:raise SystemExit('invalid authorization arguments')
        authorize(Path(sys.argv[2]),json.loads(Path(sys.argv[3]).read_text()),sys.argv[4])
    else:
        if len(sys.argv) not in {4,5} or (len(sys.argv)==5 and sys.argv[4]!='--result'):
            raise SystemExit('invalid layout validation arguments')
        validate(json.loads(Path(sys.argv[1]).read_text())['partitiontable'],json.loads(Path(sys.argv[2]).read_text()),sys.argv[3],
                 'result' if len(sys.argv)==5 and sys.argv[4]=='--result' else 'start')
