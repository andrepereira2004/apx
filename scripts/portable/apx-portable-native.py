#!/usr/bin/env python3
"""Future portable-native v4 Host/Recovery worker and explicit source registration."""
import argparse
import os
import shutil
import tempfile
from pathlib import Path
import sys
sys.path.insert(0,'/usr/lib/apx')
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from apx_portable_native_io import STATE,atomic,trusted,locked
from apx_portable_native_worker import host_action,offline,finalize,MANAGEMENT_LOCK,state


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['register-source','prepare','activate','rollback','retry','delete','boot','offline','finalize','status','unlock'])
    parser.add_argument('--target');parser.add_argument('--generation');parser.add_argument('--lock-token')
    parser.add_argument('--iso',type=Path);parser.add_argument('--sha256');parser.add_argument('--image-index',type=int)
    parser.add_argument('--drivers',type=Path);parser.add_argument('--drivers-sha256')
    args=parser.parse_args()
    try:return perform(args,parser)
    finally:
        if args.lock_token and MANAGEMENT_LOCK.exists() and MANAGEMENT_LOCK.read_text().strip()==args.lock_token:
            MANAGEMENT_LOCK.unlink()


def perform(args,parser):
    if os.geteuid():raise PermissionError('Host root required')
    if args.action=='unlock':return
    with locked():
        if args.action=='register-source':
            if not args.iso or not args.sha256 or not args.image_index:parser.error('register-source requires --iso --sha256 --image-index')
            if (STATE/'pending.json').exists():raise ValueError('cannot replace media during a native transaction')
            from apx_portable_native_media import register_source
            value=register_source(args.iso,args.sha256,args.image_index,args.drivers,args.drivers_sha256)
            # Import into a private root-owned store; later preparation never
            # depends on a download/home directory remaining unchanged.
            from apx_portable_native_io import file_hash,regular
            needed=sum(Path(value[key]).stat().st_size for key in ['iso','driver_archive'] if key in value)
            if shutil.disk_usage('/').free-needed<112*1024**3:raise ValueError('source import would cross the Linux recovery reserve/headroom')
            store=STATE/'sources';store.mkdir(mode=0o700,parents=True,exist_ok=True)
            for key,sha_key,suffix in [('iso','sha256','.iso'),('driver_archive','driver_sha256','.tar')]:
                if key not in value:continue
                destination=store/(value[sha_key]+suffix)
                if not destination.exists():
                    fd,temp=tempfile.mkstemp(prefix='.import-',dir=store)
                    try:
                        with os.fdopen(fd,'wb') as out,regular(value[key]).open('rb') as source:
                            shutil.copyfileobj(source,out);out.flush();os.fsync(out.fileno())
                        if file_hash(temp)!=value[sha_key]:raise ValueError('source changed during import')
                        os.replace(temp,destination)
                    finally:
                        if os.path.exists(temp):os.unlink(temp)
                if file_hash(regular(destination))!=value[sha_key]:raise ValueError('stored ISO/driver archive differs')
                value[key]=str(destination)
            atomic(STATE/'source.json',value);print('Official ISO registered; no Windows installation or boot queued.');return
        if args.action=='status':
            import json
            from apx_portable_native_hub import records,control
            print(json.dumps({'pending':control(),'instances':records()},indent=2));return
        if args.action=='offline':return offline()
        if args.action=='finalize':
            try:return finalize()
            except Exception as error:
                if (STATE/'pending.json').exists():
                    job=trusted(STATE/'pending.json')
                    state(job,'recovery-required','A validação do Windows parou. Consulta a recuperação no Host.',
                          error=str(error)[-2000:],manual_recovery=True)
                raise
        if not args.target or not args.generation:parser.error('instance action requires --target and --generation')
        from apx_portable_native import NAME,guid
        if not NAME.fullmatch(args.target) or args.target=='hub':raise ValueError('invalid native instance name')
        guid(args.generation)
        # Host root may run recovery operations from the console. Socket callers
        # enter only through the authenticated Hub adapter with its exact token.
        if args.lock_token:
            if MANAGEMENT_LOCK.read_text().strip()!=args.lock_token:raise ValueError('management lock owner changed')
        elif MANAGEMENT_LOCK.exists():raise ValueError('another Environment operation is active')
        try:host_action(args.action,args.target,args.generation)
        except Exception as error:
            if (STATE/'pending.json').exists():
                job=trusted(STATE/'pending.json')
                if job['generation']==args.generation:
                    old=job['stage']
                    phase='prepare-failed' if args.action=='prepare' else ('offline-failed' if job['action']=='delete' else old)
                    state(job,phase,'A operação Windows parou. Consulta a recuperação no Hub.',
                          error=str(error)[-2000:],offline_stage=job.get('offline_stage',old))
            raise


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('APX portable Windows: '+str(error),file=sys.stderr);raise SystemExit(2)
