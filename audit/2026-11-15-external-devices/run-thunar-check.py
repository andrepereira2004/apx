from pathlib import Path
import json,subprocess
repo=Path(__file__).resolve().parents[2]
p=json.loads((Path(__file__).parent/'session.json').read_text())
script='''import tempfile,pathlib,os
p=pathlib.Path(tempfile.mkdtemp(prefix="apx-device-test-"));(p/"gtk-3.0").mkdir();(p/"gtk-3.0/bookmarks").write_text("file:///home/apx/Documents Documentos\\nfile:///media/apx-usb/Ventoy PEN USB\\n")
os.environ.update(XDG_CONFIG_HOME=str(p),GTK_MODULES="/tmp/check-thunar-devices.so",NO_AT_BRIDGE="1",GTK_USE_PORTAL="0")
os.execvp("dbus-run-session",["dbus-run-session","--","/usr/bin/thunar","/home/apx/Downloads"])
'''
r=subprocess.run(p+['python3','-c',script],capture_output=True,text=True,timeout=25)
(Path(__file__).parent/'thunar-check.log').write_text(r.stdout+r.stderr)
print('return',r.returncode)
print('\n'.join(l for l in (r.stdout+r.stderr).splitlines() if any(x in l for x in ('PASS','FAIL','module'))))
assert r.returncode==0 and 'PASS stage 2' in r.stdout
