from pathlib import Path
import json,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
s=(ROOT/'config/environment-shell-v1/quickshell/apx/ControlDashboard.qml').read_text()
a=s.index('    component DashboardCard:')
component=s[a:s.index('    readonly property bool brightnessPressed:',a)]
marker=Path('/run/apx/active-graphical-environment-v1.json')
if not marker.exists():marker=Path('/run/apx/official-hub-graphical-v1.json')
home=Path('/var/lib/apx/environments')/json.loads(marker.read_text()).get('name','hub')/'home/apx'
stage=home/'.cache/apx-dashboard-outline';assert not stage.exists();stage.mkdir()
scale=sys.argv[1]
qml='''import QtQuick
import QtQuick.Window
import QtTest
Rectangle {
 id:dashboard;width:220;height:220;color:"#ff0000"
 property var controller:({popupPanel:"#101117",shellBorder:"#808080"})
 property real displayScale:Window.window.devicePixelRatio
 readonly property real outlineWidth:Math.max(1,Math.round(displayScale))/displayScale
 // COMPONENT
 DashboardCard {id:card;x:20;y:20;width:180;height:180;radius:20}
 TestCase {
  name:'DashboardOutline';when:windowShown
  function test_same_stroke_on_all_sides_at_monitor_scale() {
   wait(80);var frame=grabImage(dashboard),dpr=frame.width/dashboard.width
   fuzzyCompare(dpr,EXPECTED_SCALE,0.01)
   fuzzyCompare(dashboard.outlineWidth*dpr,Math.round(dpr),0.01)
   var left=0,right=0,top=0,bottom=0
   for(var i=0;i<Math.ceil(6*dpr);i++) {
    var l=frame.pixel(Math.round(20*dpr)+i,Math.floor(110*dpr)).g
    var r=frame.pixel(Math.round(200*dpr)-1-i,Math.floor(110*dpr)).g
    var t=frame.pixel(Math.floor(110*dpr),Math.round(20*dpr)+i).g
    var b=frame.pixel(Math.floor(110*dpr),Math.round(200*dpr)-1-i).g
    left+=Math.max(0,(l-17/255)/(128/255-17/255))
    right+=Math.max(0,(r-17/255)/(128/255-17/255))
    top+=Math.max(0,(t-17/255)/(128/255-17/255))
    bottom+=Math.max(0,(b-17/255)/(128/255-17/255))
   }
   fuzzyCompare(left,right,0.08);fuzzyCompare(left,top,0.08);fuzzyCompare(top,bottom,0.08)
   verify(left>0.8)
   frame.save(Qt.resolvedUrl('outline.png').toString().replace('file://',''))
   console.log('OUTLINE_METRICS',JSON.stringify({dpr:dpr,left:left,right:right,top:top,bottom:bottom}))
  }
 }
}
'''.replace(' // COMPONENT',component).replace('EXPECTED_SCALE',scale)
try:
 (stage/'tst_outline.qml').write_text(qml)
 (Path(__file__).parent/'tst_outline.qml').write_text(qml)
 meta=home.stat()
 for p in [stage]+list(stage.rglob('*')):os.chown(p,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=wayland','QT_SCALE_FACTOR='+str(float(scale)/1.5),'/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=15)
 (Path(__file__).parent/('results-'+scale+'.log')).write_text(result.stdout+result.stderr)
 if (stage/'outline.png').exists():shutil.copy2(stage/'outline.png',Path(__file__).parent/('outline-'+scale+'.png'))
 print(result.stdout+result.stderr);assert result.returncode==0
finally:shutil.rmtree(stage)
