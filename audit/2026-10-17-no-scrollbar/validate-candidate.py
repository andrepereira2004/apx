import importlib.util, json, os, shutil, subprocess, signal
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('motion',REPO/'scripts/physical-pilot/deploy-no-scrollbar-20261017.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/state['name']/'home/apx';stage=home/'.cache/apx-no-scrollbar-validation-20261017';assert not stage.exists();stage.mkdir();meta=home.stat()
try:
 shutil.copytree(home/'.config/quickshell/apx',stage/'apx')
 for rel in m.transform.RELATIVES:
  if not rel.startswith('quickshell/'):continue
  path=stage/'apx'/Path(rel).relative_to('quickshell/apx');path.parent.mkdir(parents=True,exist_ok=True)
  path.write_text(m.transform.transform(rel,path.read_text() if path.exists() else ""))
 (stage/'parse.qml').write_text('''import QtQuick
import Quickshell
ShellRoot {
 property var candidate: null
 Timer {
  interval: 100; running: true; repeat: true
  onTriggered: {
   if (!candidate) candidate = Qt.createComponent("apx/shell.qml")
   if (candidate.status === Component.Error) { console.error(candidate.errorString()); Qt.exit(1) }
   if (candidate.status === Component.Ready) { console.log("PARSE_PASS"); Qt.quit() }
  }
 }
}''')
 for path in [stage]+list(stage.rglob('*')):os.chown(path,meta.st_uid,meta.st_gid)
 runner=['python',str(REPO/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','quickshell','--path']
 for name in ['parse']:
  current_runner=[arg.replace('QT_QPA_PLATFORM=offscreen', 'QT_QPA_PLATFORM=wayland') if name=='parse' else arg for arg in runner]
  process=subprocess.Popen(current_runner+['/home/apx/.cache/'+stage.name+'/'+name+'.qml','--no-color'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
  try:stdout,stderr=process.communicate(timeout=12)
  except subprocess.TimeoutExpired:
   os.killpg(process.pid,signal.SIGTERM);stdout,stderr=process.communicate();raise RuntimeError(stdout+stderr)
  (m.AUDIT/(name+'-candidate.log')).write_text(stdout+stderr)
  print(name,process.returncode,(stdout+stderr)[-2300:]);assert process.returncode==0 and name.upper()+'_PASS' in stdout+stderr
finally:shutil.rmtree(stage)
