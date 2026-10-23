#!/usr/bin/python3
"""Restore only Faculdade's signed OpenAI sync metadata; no Arch package refresh."""
from pathlib import Path
import datetime
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

REPO=Path(__file__).resolve().parents[2]
ROOT=Path('/var/lib/apx/environments/faculdade/root')

def main():
    assert Path('/etc/hostname').read_text().strip()=='apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
    registration=json.loads((ROOT.parent/'registration.json').read_text())
    assert registration['generation']=='e9b08983-4740-4b85-8580-862c4a1d4c54'
    config=(ROOT/'etc/pacman.d/openai-chatgpt.conf').read_text()
    assert 'SigLevel = Required DatabaseRequired TrustedOnly' in config
    assert 'Server = https://persistent.oaistatic.com/codex-app-prod/linux/arch/$arch' in config
    names=['openai-chatgpt.db','openai-chatgpt.db.sig']
    with tempfile.TemporaryDirectory(dir=REPO/'audit/2026-10-20-chatgpt-install') as temporary:
        directory=Path(temporary)
        for name in names:
            subprocess.run(['curl','--proto','=https','--tlsv1.2','-fsSL','--max-time','30','https://persistent.oaistatic.com/codex-app-prod/linux/arch/x86_64/'+name,'-o',str(directory/name)],check=True)
        subprocess.run(['gpgv','--keyring',str(ROOT/'etc/pacman.d/gnupg/pubring.gpg'),str(directory/names[1]),str(directory/names[0])],check=True)
        parent=ROOT/'var/lib/pacman/sync';meta=parent.stat()
        assert not parent.is_symlink()
        lock=ROOT/'var/lib/pacman/db.lck';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-chatgpt-repository');backup.mkdir()
        records=[]
        try:
            for name in names:
                target=parent/name;assert not target.is_symlink()
                if target.exists():shutil.copy2(target,backup/name)
                records.append({'path':str(target),'existed':target.exists(),'sha256':hashlib.sha256((directory/name).read_bytes()).hexdigest()})
                stage=target.with_name(name+'.apx-tmp');assert not stage.exists()
                stage.write_bytes((directory/name).read_bytes());os.chown(stage,meta.st_uid,meta.st_gid);os.chmod(stage,0o644);os.replace(stage,target)
            (backup/'inventory.json').write_text(json.dumps(records,indent=2)+'\n')
        finally:os.close(fd);lock.unlink()
        print(backup)

if __name__=='__main__':
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);main()
