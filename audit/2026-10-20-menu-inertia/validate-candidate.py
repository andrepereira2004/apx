import importlib.util, json, os, shutil, subprocess, signal
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('motion',REPO/'scripts/physical-pilot/deploy-menu-inertia-20261020.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/state['name']/'home/apx';stage=home/'.cache/apx-menu-inertia-validation-20261020';assert not stage.exists();stage.mkdir();meta=home.stat()
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
 (stage/'inertia.qml').write_text('import QtQuick\nimport Quickshell\nShellRoot {\n property var popup: ({open:true})\n property var controlPageAnimation: ({running:false})\n Item { width:300; height:300\n Flickable {\n  id: view; width:300; height:300; contentWidth:300; contentHeight:2000; contentY:400\n  boundsBehavior: Flickable.StopAtBounds\n  flickDeceleration:3200; maximumFlickVelocity:1200\n  property real wheelVelocity:0\n  property double wheelStamp:0\n  property bool nativeWheelMomentum:false\n                function scrollWheel(delta, stamp, phase) {\n                    if (phase === Qt.ScrollBegin) {\n                        nativeWheelMomentum = false\n                        wheelVelocity = 0\n                        wheelStamp = 0\n                    }\n                    if (phase === Qt.ScrollMomentum) nativeWheelMomentum = true\n                    wheelRelease.stop()\n                    cancelFlick()\n                    if (delta) {\n                        var elapsed = wheelStamp ? Math.max(8, Math.min(60, stamp - wheelStamp)) : 16\n                        wheelVelocity = Math.max(-1200, Math.min(1200, delta * 2.5 / elapsed * 1000 * .35))\n                        wheelStamp = stamp\n                        contentY = Math.max(0, Math.min(Math.max(0, contentHeight - height), contentY - delta * 2.5))\n                    }\n                    if (!nativeWheelMomentum && wheelStamp) wheelRelease.restart()\n                }\n                function releaseWheel() {\n                    if (enabled && popup.open && !controlPageAnimation.running && Math.abs(wheelVelocity) >= 35)\n                        flick(0, wheelVelocity)\n                    wheelVelocity = 0\n                    wheelStamp = 0\n                    nativeWheelMomentum = false\n                }\n\n  Timer {id:wheelRelease;interval:70;onTriggered:view.releaseWheel()}\n }\n }\n property real startY:0\n property real startVelocity:0\n Timer {interval:100;running:true;onTriggered: {\n   view.scrollWheel(-10,1000,Qt.ScrollBegin)\n   view.scrollWheel(-12,1016,Qt.ScrollUpdate)\n   rootTest.startY=view.contentY\n   view.releaseWheel()\n   rootTest.startVelocity=1200\n }}\n Timer {interval:180;running:true;onTriggered: {\n   if (view.contentY<=rootTest.startY || Math.abs(view.verticalVelocity)>=rootTest.startVelocity) {\n      console.error("No decelerating continuation",view.contentY,rootTest.startY,view.verticalVelocity,rootTest.startVelocity);Qt.exit(1)\n   }\n }}\n Timer {interval:900;running:true;onTriggered: {\n   if (view.flicking || view.contentY>view.contentHeight-view.height) {console.error("Inertia did not settle");Qt.exit(1)}\n   console.log("INERTIA_PASS");Qt.quit()\n }}\n id:rootTest\n}')
 for path in [stage]+list(stage.rglob('*')):os.chown(path,meta.st_uid,meta.st_gid)
 runner=['python',str(REPO/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','quickshell','--path']
 for name in ['parse','inertia']:
  current_runner=[arg.replace('QT_QPA_PLATFORM=offscreen', 'QT_QPA_PLATFORM=wayland') if name=='parse' else arg for arg in runner]
  process=subprocess.Popen(current_runner+['/home/apx/.cache/'+stage.name+'/'+name+'.qml','--no-color'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
  try:stdout,stderr=process.communicate(timeout=12)
  except subprocess.TimeoutExpired:
   os.killpg(process.pid,signal.SIGTERM);stdout,stderr=process.communicate();raise RuntimeError(stdout+stderr)
  (m.AUDIT/(name+'-candidate.log')).write_text(stdout+stderr)
  print(name,process.returncode,(stdout+stderr)[-2300:]);assert process.returncode==0 and name.upper()+'_PASS' in stdout+stderr
finally:shutil.rmtree(stage)
