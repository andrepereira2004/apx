from pathlib import Path
import json,subprocess
p=json.loads((Path(__file__).parent/'session.json').read_text())
code='''import tempfile,pathlib,zipfile,tarfile,io,os
p=pathlib.Path(tempfile.mkdtemp(prefix="apx-archive-action-"))
with zipfile.ZipFile(p/"sample-zip.zip","w",zipfile.ZIP_DEFLATED) as z:z.writestr("zip-marker.txt","APX ZIP extraction test\\n")
with tarfile.open(p/"sample-tar.tar","w") as t:
 data=b"APX TAR extraction test\\n";i=tarfile.TarInfo("tar-marker.txt");i.size=len(data);t.addfile(i,io.BytesIO(data))
os.environ.update(APX_ARCHIVE_FIXTURE=str(p),GTK_MODULES="/tmp/check-archive-action.so",NO_AT_BRIDGE="1",GTK_USE_PORTAL="0",USER="apx",LOGNAME="apx",PATH="/home/apx/.local/bin:/usr/local/bin:/usr/bin")
os.execvp("dbus-run-session",["dbus-run-session","--","/usr/bin/thunar",str(p)])
'''
r=subprocess.run(p+['python3','-c',code],capture_output=True,text=True,timeout=25)
(Path(__file__).parent/'archive-check.log').write_text(r.stdout+r.stderr)
print('return',r.returncode);print('\n'.join(l for l in (r.stdout+r.stderr).splitlines() if any(x in l for x in ('PASS','FAIL','module'))))
assert r.returncode==0 and 'PASS: native Thunar' in r.stdout
