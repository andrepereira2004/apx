#!/usr/bin/env python3
"""Real installed Howdy PAM module, synthetic face/password, private mount namespace.
Never reads a password, model contents or camera; never changes a live PAM stack.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
ROOT=Path('/var/lib/apx/environments/faculdade/root')

def child(case, directory):
    subprocess.run(['mount','--make-rprivate','/'],check=True)
    pairs=[(directory/'pam',ROOT/'etc/pam.d'),(directory/'config.ini',ROOT/'etc/howdy/config.ini'),
           (directory/'compare.py',ROOT/'usr/lib/howdy/compare.py'),
           (HERE/'pam-conversation',ROOT/'usr/bin/true'),
           (HERE/'pam-fixture-password.so',ROOT/'usr/lib/security/pam_unix.so'),
           (HERE/'pam-fixture-faillock.so',ROOT/'usr/lib/security/pam_faillock.so')]
    for source,target in pairs:
        subprocess.run(['mount','--bind',str(source),str(target)],check=True)
    os.execvp('chroot',['chroot',str(ROOT),'/usr/bin/true',case])

if len(sys.argv)>1:
    child(sys.argv[1],Path(sys.argv[2]))
else:
    for case, delay, status in [('face',.05,0),('password',2,11),('timeout',.02,11),('camera-error',.02,14),('reject',2,11),('disabled',.02,11)]:
        with tempfile.TemporaryDirectory(prefix='fixture-',dir=HERE) as temp:
            directory=Path(temp); (directory/'pam').mkdir()
            (directory/'pam/apx-parallel-test').write_bytes((HERE.parents[1]/'config/howdy-v1/pam/hyprlock-workload').read_bytes())
            (directory/'config.ini').write_text('[core]\nworkaround = native\nabort_if_ssh = false\nabort_if_lid_closed = false\ndisabled = false\nno_confirmation = true\ndetection_notice = false\n')
            if case=='disabled':
                (directory/'config.ini').write_text((directory/'config.ini').read_text().replace('disabled = false','disabled = true'))
            (directory/'compare.py').write_text(f'import time\ntime.sleep({delay})\nraise SystemExit({status})\n')
            subprocess.run(['unshare','--mount','--fork','python',str(__file__),case,temp],check=True,timeout=6)
