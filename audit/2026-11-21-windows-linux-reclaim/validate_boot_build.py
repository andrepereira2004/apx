#!/usr/bin/env python3
"""Build-only validation in a private mount namespace; no GPT or boot writes."""
import importlib.util,json,pathlib,shutil,stat,subprocess,sys,tempfile
repo=pathlib.Path(__file__).resolve().parents[2]
root=pathlib.Path(tempfile.mkdtemp(prefix='apx-reclaim-build-',dir='/var/lib/apx/tmp'))
root.chmod(0o700)
subprocess.run(['mount','--make-rprivate','/'],check=True)
shutil.copytree('/etc',root/'etc',symlinks=True,ignore=lambda d,names:[n for n in names if stat.S_ISSOCK(pathlib.Path(d,n).lstat().st_mode)])
subprocess.run(['mount','--bind',str(root/'etc'),'/etc'],check=True)
sys.path.insert(0,str(repo/'src'))
p=repo/'scripts/physical-pilot/apx-reclaim-windows-linux-v3.py'
s=importlib.util.spec_from_file_location('boot_validation',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
plan=json.loads(pathlib.Path('/root/apx-linux-reclaim-faculdade-20261121T144101Z/reclaim-plan.json').read_bytes())
work=root/'work';work.mkdir()
try:
 m.prepare_boot(plan,work)
 print(json.dumps({'signed_boot_images':[p.name for p in m.IMAGES],'build_work':str(work),'disk_changes':False,'boot_changes':False}))
finally:
 # Remove private copies of Host keys/configuration after the build.
 subprocess.run(['umount','/etc'],check=True)
 shutil.rmtree(root/'etc')
