"""Build the current native modes in the active Environment and trace isolated launches."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'scripts/physical-pilot/apx-rofi-apps-mode-v1.c').read_text()
code='''import subprocess,shlex,os,json,time
from pathlib import Path
directory=Path('/home/apx/.cache/apx-rofi-startup-build')
directory.mkdir(mode=0o700,exist_ok=True)
flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gio-2.0','json-glib-1.0','cairo','gmodule-2.0'],text=True))
for name in ['apps','system']:
 subprocess.run(['cc','-shared','-fPIC','-Wall','-Wextra','-Werror','-O2','-DAPX_MODE_NAME="'+name+'"','-x','c','-','-o',str(directory/('apx-rofi-'+name+'-v1.so')),*flags],input=SOURCE,text=True,check=True)
link=directory/'apx-rofi-files-v1.so'
if not link.exists():link.symlink_to('/home/apx/.local/lib/rofi/apx-rofi-files-v1.so')
traces=[]
for mode in ['apps','system']:
 layers=json.loads(subprocess.check_output(['hyprctl','-j','layers'],text=True))
 assert not any(l.get('namespace')=='rofi' for m in layers.values() for g in m.get('levels',{}).values() for l in g)
 env=dict(os.environ,ROFI_PLUGIN_PATH=str(directory),APX_ROFI_TIMING='1',LD_PRELOAD='/home/apx/.local/libexec/apx-rofi-secondary-v1.so')
 p=subprocess.Popen(['rofi','-modi','apps,files,system','-show',mode],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
 time.sleep(.8)
 assert p.poll() is None
 p.terminate();_,errors=p.communicate(timeout=4)
 traces.append({'mode':mode,'trace':[x for x in errors.splitlines() if x.startswith('APX_ROFI_TIMING')]})
 time.sleep(.25)
print(json.dumps({'traces':traces},indent=2))
'''.replace('input=SOURCE,','input='+repr(source)+',')
r=subprocess.run(['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),'python','-'],input=code,capture_output=True,text=True,timeout=20)
print(r.stdout,r.stderr)
assert r.returncode==0
(ROOT/'audit/2026-10-25-desktop-integration/rofi-lazy-startup-trace.json').write_text(r.stdout)
