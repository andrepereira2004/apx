from pathlib import Path
import os,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=Path('/var/lib/apx/environments/faculdade/root')
if len(sys.argv)>1:
 service,case,directory=sys.argv[1:];directory=Path(directory)
 subprocess.run(['mount','--make-rprivate','/'],check=True)
 for source,target in [(directory/'pam',ROOT/'etc/pam.d'),(HERE/'pam-conversation',ROOT/'usr/bin/true'),(HERE/'pam-fixture-password.so',ROOT/'usr/lib/security/pam_unix.so'),(HERE/'pam-fixture-faillock.so',ROOT/'usr/lib/security/pam_faillock.so')]:
  subprocess.run(['mount','--bind',str(source),str(target)],check=True)
 os.execvp('chroot',['chroot',str(ROOT),'/usr/bin/true',case,service])
else:
 for service in ['hyprlock','sudo']:
  for case in ['password','reject']:
   with tempfile.TemporaryDirectory(dir=HERE) as d:
    directory=Path(d);shutil.copytree(ROOT/'etc/pam.d',directory/'pam')
    if service=='sudo':shutil.copy2('/var/lib/apx/environments/hub/root/etc/pam.d/sudo',directory/'pam/sudo')
    result=subprocess.run(['unshare','--mount','--fork','python',str(__file__),service,case,d],capture_output=True,text=True,timeout=8)
    print(service,result.stdout,result.stderr,flush=True)
    if result.returncode:raise SystemExit(result.returncode)
