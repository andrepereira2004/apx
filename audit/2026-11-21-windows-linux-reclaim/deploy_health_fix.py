"""Install reviewed health gate and exact evidence of the completed read-only scrub."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,os,re,shutil,subprocess,tempfile,time,sys
sys.path.insert(0,"/usr/lib/apx")
repo=Path(__file__).resolve().parents[2]
def run(*args):return subprocess.check_output(args,env={'PATH':'/usr/bin','LC_ALL':'C'})
def sha(data):return hashlib.sha256(data).hexdigest()
def atomic(path,data,mode):
 fd,tmp=tempfile.mkstemp(prefix='.apx-health-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:os.fchmod(f.fileno(),mode);f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:Path(tmp).unlink(missing_ok=True)
assert Path('/etc/hostname').read_text().strip()=='apx-host'
assert Path('/sys/class/block/nvme0n1/device/serial').read_text().strip()=='S4DYNX0R253702'
scrub=run('btrfs','scrub','status','-R','/')
assert b'Status:           finished' in scrub
errors=re.findall(rb'\b[a-z_]*errors:\s+(\d+)',scrub);assert len(errors)>=7 and all(int(v)==0 for v in errors)
log=(repo/'audit/2026-11-21-windows-linux-reclaim/scrub-readonly.log').read_text()
assert 'no errors found' in log and 'Sat Nov 21 15:17:57 2026' in log
stats=json.loads(run('btrfs','--format','json','device','stats','/'))
fields=['write_io_errs','read_io_errs','flush_io_errs','corruption_errs','generation_errs']
assert len(stats['device-stats'])==1
values={key:stats['device-stats'][0][key] for key in fields}
assert values==dict(write_io_errs=0,read_io_errs=0,flush_io_errs=0,corruption_errs=79,generation_errs=0)
proof=dict(profile='apx-clean-readonly-scrub-v3',filesystem_uuid=run('findmnt','-no','UUID','/').decode().strip(),
 clean_readonly_scrub=True,verified_at=time.time(),historical_counters={'/dev/mapper/cryptroot':values},scrub_status_sha256=sha(scrub))
manifest=Path('/usr/share/apx/native-v3-enabled.json');release=json.loads(manifest.read_bytes())
for name,expected in release['files'].items():assert sha(Path(name).read_bytes())==expected,name
changed={Path('/usr/lib/apx/apx_native_linux_reclaim_v3.py'):(repo/'src/apx_native_linux_reclaim_v3.py').read_bytes(),
 Path('/usr/lib/apx/apx-reclaim-windows-linux-v3.py'):(repo/'scripts/physical-pilot/apx-reclaim-windows-linux-v3.py').read_bytes()}
for path,data in changed.items():release['files'][str(path)]=sha(data)
changed[manifest]=json.dumps(release,sort_keys=True).encode()
proof_path=Path('/var/lib/apx/native-environments/linux-reclaim-health-v3.json')
assert not proof_path.exists()
changed[proof_path]=json.dumps(proof,sort_keys=True).encode()
backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-reclaim-health-fix');backup.mkdir(mode=0o700)
for path in changed:
 if path.exists():
  out=backup/str(path).lstrip('/');out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,out)
for path,data in changed.items():atomic(path,data,path.stat().st_mode&0o777 if path.exists() else 0o400)
# Exercise the installed preflight with the exact current device counters.
spec=importlib.util.spec_from_file_location('health_installed','/usr/lib/apx/apx_native_linux_reclaim_v3.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.validate_storage_health(stats,proof,proof['filesystem_uuid'],time.time())
assert sha(run('btrfs','scrub','status','-R','/'))==proof['scrub_status_sha256']
print(json.dumps({'backup':str(backup),'health_preflight':'passed','counters_preserved':values,'disk_changes':False,'scrub_errors':0}))
