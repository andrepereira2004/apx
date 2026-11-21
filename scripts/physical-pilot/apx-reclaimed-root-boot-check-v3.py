#!/usr/bin/env python3
"""One-request post-reboot evidence collector for the owner-authorized pilot test."""
from pathlib import Path
import hashlib,json,os,subprocess,tempfile,time
ROOT=Path('/var/lib/apx/native-environments')
request=json.loads((ROOT/'reboot-validation-request-v3.json').read_bytes())
boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
if boot_id==request['before_boot_id']:
 print('Waiting for a different boot ID.');raise SystemExit(0)
def run(*args):return subprocess.check_output(args,stderr=subprocess.STDOUT,env={'PATH':'/usr/bin','LC_ALL':'C'},timeout=45).decode()
checks={};errors=[]
def check(name,fn):
 try:checks[name]=fn()
 except Exception as e:checks[name]=False;errors.append(name+': '+str(e)[:400])
def root_members():
 output=run('btrfs','filesystem','show','--raw','/')
 assert 'Total devices 2' in output
 assert '/dev/mapper/cryptroot' in output and '/dev/mapper/cryptreclaimed' in output
 return output
def unlock():
 assert run('cryptsetup','luksUUID','/dev/nvme0n1p5').strip()==request['luks_uuid']
 assert 'device=/dev/mapper/cryptreclaimed' in Path('/proc/cmdline').read_text()
 assert 'rd.luks.name='+request['luks_uuid']+'=cryptreclaimed' in Path('/proc/cmdline').read_text()
 return True
def windows():
 table=json.loads(run('sfdisk','--json','/dev/nvme0n1'))['partitiontable']
 part=next(p for p in table['partitions'] if p['node']=='/dev/nvme0n1p3')
 assert part==request['windows_partition']
 assert run('blkid','-p','-s','TYPE','-o','value','/dev/nvme0n1p3').strip()=='ntfs'
 return True
def signatures():
 for name,expected in request['boot_images'].items():
  path=Path(name);assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
  run('sbverify','--cert','/etc/kernel/secure-boot-certificate.pem',name)
 return True
def device_health():
 actual=json.loads(run('btrfs','--format','json','device','stats','/'))
 assert actual==request['device_stats']
 return actual
check('both_root_members',root_members);check('encrypted_boot_configuration',unlock)
check('windows_personal_preserved',windows);check('installed_signatures',signatures)
check('device_error_counters_unchanged',device_health)
check('native_release',lambda:json.loads(run('python3','/root/apx-host-development-mode-v1/apx/scripts/physical-pilot/check-native-release-v3.py')))
report=dict(profile='apx-reclaimed-root-boot-validation-v3',before_boot_id=request['before_boot_id'],
 boot_id=boot_id,checked_at=time.time(),status='passed' if not errors else 'failed',checks=checks,errors=errors,
 capacity=run('df','-h','/'),failed_units=run('systemctl','--failed','--no-pager'),
 graphical_state=Path('/run/apx/official-hub-graphical-v1.json').read_text() if Path('/run/apx/official-hub-graphical-v1.json').exists() else None)
fd,tmp=tempfile.mkstemp(prefix='.boot-validation-',dir=ROOT)
with os.fdopen(fd,'w') as f:
 os.fchmod(f.fileno(),0o600);json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
os.replace(tmp,ROOT/'reboot-validation-result-v3.json')
print(json.dumps({'status':report['status'],'boot_id':boot_id,'errors':errors}))
raise SystemExit(1 if errors else 0)
