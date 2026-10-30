from pathlib import Path
import json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
a=source.index('            layer.effect: MultiEffect {',source.index('id: popupBackground\n'))
effect=source[a:source.index('\n            radius:',a)]
a=source.index('        Rectangle {\n            id: popupClipMask')
mask=source[a:source.index('        Rectangle {\n            id: popupBackground',a)]
marker=Path('/run/apx/active-graphical-environment-v1.json')
if not marker.exists():marker=Path('/run/apx/official-hub-graphical-v1.json')
home=Path('/var/lib/apx/environments')/json.loads(marker.read_text()).get('name','hub')/'home/apx'
stage=home/'.cache/apx-sharpness-test';assert not stage.exists();stage.mkdir()
qml='''import QtQuick
import QtQuick.Window
import QtQuick.Effects
import QtTest
Rectangle {
 id:root;width:700;height:260;color:"#101117"
 property var popup:({open:true})
 // MASK
 Rectangle {
  id:popupBackground;x:360;y:20;width:300;height:220;radius:20;color:"#101117"
  clip:true;layer.enabled:popup.open
  // EFFECT
  Text {x:20;y:30;text:"Central de Controlo";font.family:"JetBrains Mono";font.pixelSize:14;color:"white"}
  Text {x:20;y:65;text:"Ligações · Wi-Fi · Bluetooth";font.family:"JetBrains Mono";font.pixelSize:12;color:"#c8ccdc"}
  Text {x:20;y:100;text:"Brilho 50% · Bateria 28%";font.family:"JetBrains Mono";font.pixelSize:12;color:"#c8ccdc"}
  ControlIcon {x:20;y:145;width:18;height:18;source:"wifi.svg";tint:"white"}
  ControlIcon {x:60;y:145;width:18;height:18;source:"volume-2.svg";tint:"white"}
 }
 Rectangle {
  x:20;y:20;width:300;height:220;radius:20;color:"#101117"
  Text {x:20;y:30;text:"Central de Controlo";font.family:"JetBrains Mono";font.pixelSize:14;color:"white"}
  Text {x:20;y:65;text:"Ligações · Wi-Fi · Bluetooth";font.family:"JetBrains Mono";font.pixelSize:12;color:"#c8ccdc"}
  Text {x:20;y:100;text:"Brilho 50% · Bateria 28%";font.family:"JetBrains Mono";font.pixelSize:12;color:"#c8ccdc"}
  ControlIcon {x:20;y:145;width:18;height:18;source:"wifi.svg";tint:"white"}
  ControlIcon {x:60;y:145;width:18;height:18;source:"volume-2.svg";tint:"white"}
 }
 TestCase {
  name:"MenuSharpness";when:windowShown
  function test_capture() {
   wait(150)
   var frame=grabImage(root)
   frame.save(Qt.resolvedUrl("sharpness.png").toString().replace("file://",""))
   var dpr=frame.width/root.width, err=0, nativeEnergy=0, maskEnergy=0, count=0
   for(var y=Math.floor(50*dpr);y<Math.floor(153*dpr);y++) {
    for(var x=Math.floor(40*dpr);x<Math.floor(300*dpr);x++) {
     var a=frame.pixel(x,y).r,b=frame.pixel(x+Math.round(340*dpr),y).r
     var da=a-frame.pixel(x+1,y).r
     var db=b-frame.pixel(x+Math.round(340*dpr)+1,y).r
     err+=Math.abs(a-b);nativeEnergy+=da*da;maskEnergy+=db*db;count++
    }
   }
   console.log("SHARPNESS_METRICS",JSON.stringify({meanError:err/count,nativeEnergy:nativeEnergy,maskedEnergy:maskEnergy,ratio:maskEnergy/nativeEnergy}))
  }
 }
}
'''.replace(' // MASK',mask).replace('  // EFFECT',effect)

try:
 shutil.copy2(ROOT/'config/environment-shell-v1/quickshell/apx/ControlIcon.qml',stage/'ControlIcon.qml')
 for name in ['wifi.svg','volume-2.svg']:shutil.copy2(ROOT/'config/environment-shell-v1/quickshell/apx/icons/lucide'/name,stage/name)
 (stage/'tst_sharpness.qml').write_text(qml)
 (Path(__file__).parent/'tst_sharpness.qml').write_text(qml)
 meta=home.stat()
 for p in [stage]+list(stage.rglob('*')):os.chown(p,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=wayland','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=15)
 (Path(__file__).parent/'results.log').write_text(result.stdout+result.stderr)
 print(result.stdout+result.stderr)
 if (stage/'sharpness.png').exists():shutil.copy2(stage/'sharpness.png',Path(__file__).parent/'sharpness.png')
 assert result.returncode==0
finally:shutil.rmtree(stage)
