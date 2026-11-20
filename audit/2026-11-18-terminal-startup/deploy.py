from pathlib import Path
import datetime,hashlib,json,os,re,shutil,stat,fcntl
repo=Path(__file__).resolve().parents[2]
source=repo/'config/environment-shell-v1'
live=Path('/var/lib/apx/environments/minecraft/home/apx')
info=(live/'.local/bin/apx-sysinfo').read_text()
a=info.index('    if [[ -t 1 && ${APX_ANIMATE:')
b=info.index('    else\n',a)
c=info.index('    fi\n',b)
info=info[:a]+info[b+len('    else\n'):c]+info[c+len('    fi\n'):]
info=info.replace('    info_delay=0\n','').replace('    [[ -t 1 && ${APX_ANIMATE:-0} != 0 ]] && info_delay=0.025\n','').replace('        [[ $info_delay != 0 ]] && sleep "$info_delay"\n','')
assets={'local/bin/apx-sysinfo':info.encode(),'local/bin/apx-atualizar-info':(live/'.local/bin/apx-atualizar-info').read_bytes(),'apx/bashrc':(live/'.config/apx/bashrc').read_bytes()}
rule='''\n-- Terminals open immediately, including the Host console (SUPER+H).
hl.window_rule({
    name = "apx-terminals-no-animation",
    match = { class = "^(kitty|apx-host-console-v1)$" },
    no_anim = true,
})
'''
planned={}
seed=Path('/usr/share/apx/config-seeds/environment-shell-v1')
homes=[p/'home/apx' for p in Path('/var/lib/apx/environments').iterdir() if (p/'registration.json').is_file()]
for rel,data in assets.items():
 planned[source/rel]=data;planned[seed/rel]=data
 for home in homes:
  planned[home/('.'+rel if rel.startswith('local/') else '.config/'+rel)]=data
rel='hypr/hyprland.lua'
for path in [source/rel,seed/rel]+[h/'.config'/rel for h in homes]:
 text=path.read_text()
 if 'apx-terminals-no-animation' not in text: text+=rule
 planned[path]=text.encode()
digest=lambda data:hashlib.sha256(data).hexdigest()
for runtime,origin in [(repo/'scripts/virtual-lab/apx-lab-runtime.py',source),(Path('/usr/lib/apx/apx-lab-runtime.py'),seed)]:
 text=runtime.read_text()
 for rel in [*assets,'hypr/hyprland.lua']:
  value=digest(planned[origin/rel])
  pattern=r'("'+re.escape(rel)+r'": ")[a-f0-9]{64}(",)'
  text,count=re.subn(pattern,lambda m:m[1]+value+m[2],text)
  if not count:
   assert rel=='local/bin/apx-atualizar-info'
   text=text.replace('    "local/bin/apx-sysinfo":',f'    "{rel}": "{value}",\n    "local/bin/apx-sysinfo":',1)
 planned[runtime]=text.encode()
recovery=repo/'scripts/physical-pilot/recover-development-quota-v1.sh'
text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+digest(planned[repo/'scripts/virtual-lab/apx-lab-runtime.py']),recovery.read_text());assert count==1
planned[recovery]=text.encode()
with open('/run/apx/machine-transition-v1.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-terminal-startup');backup.mkdir(mode=0o700)
 entries=[]
 for target,data in planned.items():
  if target.exists() and target.read_bytes()==data:continue
  assert not target.is_symlink()
  meta=target.stat() if target.exists() else target.parent.stat()
  mode=stat.S_IMODE(meta.st_mode) if target.exists() else 0o755
  if target.exists():
   saved=backup/target.relative_to('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  entries.append({'path':str(target),'existed':target.exists(),'after':digest(data)})
  temp=target.with_name(target.name+'.startup-new');temp.write_bytes(data);os.chmod(temp,mode);os.chown(temp,meta.st_uid,meta.st_gid);os.replace(temp,target)
  assert digest(target.read_bytes())==digest(data)
 (backup/'inventory.json').write_text(json.dumps(entries,indent=2)+'\n')
 print(backup);print('Verified',len(entries),'files; homes:',len(homes))
