from pathlib import Path
import os,json,shutil,subprocess
repo=Path(__file__).resolve().parents[2];source=repo/'config/environment-shell-v1/quickshell/apx';text=(source/'shell.qml').read_text();a=text.rfind('                    Row {',0,text.index('id: energyModeRow'));b=text.index('                    Text {\n                        visible: root.hardwareMessage',a);row=text[a:b]
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/state['name']/'home/apx';stage=home/'.cache/apx-energy-centres';assert not stage.exists();stage.mkdir();meta=home.stat()
try:
 for name in ['LucideIcon.qml','ControlIcon.qml','BounceMouseArea.qml','MenuHover.qml']:shutil.copy2(source/name,stage/name)
 shutil.copytree(source/'icons',stage/'icons')
 (stage/'qmldir').write_text('singleton Appearance 1.0 Appearance.qml\n')
 (stage/'Appearance.qml').write_text('pragma Singleton\nimport QtQuick\nQtObject { property color iconColor: "white"; property string fontFamily: "sans-serif"; property bool tintButtons: false; property color hover: "#292d3a" }')
 qml='''import QtQuick
import QtTest
Item {
 id: root; width: 320; height: 120
 property var hardwareProfile: ({platform_profile:"low-power",platform_profiles:["low-power","balanced","performance"]})
 property bool hardwareBusy: false
 property color controlButtonSurface: "#1b1d26"
 property color controlButtonActive: "#353a4a"
 property color textMain: "white"
 property int menuSmallSize: 11
 property int profileActions: 0
 function setPlatformProfile(p) { profileActions++ }
 component SelectionIndicator: Rectangle { width:18; height:2; anchors.horizontalCenter:parent.horizontalCenter; anchors.bottom:parent.bottom }
 ROW
 TestCase {
  name: "EnergyCentres"; when: windowShown
  function test_transition() {
   mouseMove(root,319,115);wait(200)
   var cards=energyModeRow.children.filter(c=>c.modelData!==undefined)
   var before=cards[1].color.toString()
   var h=energyModeRow.height
   root.hardwareBusy=true;wait(20)
   compare(cards[0].opacity,1);compare(cards[1].opacity,1);compare(energyModeRow.height,h)
   root.hardwareProfile={platform_profile:"balanced",platform_profiles:["low-power","balanced","performance"]}
   wait(50)
   verify(cards[1].color.toString()!==before)
   verify(cards[1].color.toString()!==root.controlButtonActive.toString())
   wait(180);compare(cards[1].color.toString(),root.controlButtonActive.toString())
   compare(energyModeRow.height,h);root.hardwareBusy=false
  }
  function test_centres() {
   wait(100)
   var cards=energyModeRow.children.filter(c=>c.modelData!==undefined)
   compare(cards.length,3)
   for(var i=0;i<cards.length;i++) {
    var card=cards[i]
    var content=card.children.filter(c=>c.spacing===6)[0]
    verify(content!==undefined)
    var circle=content.children.filter(c=>c.width===32 && c.height===32)[0]
    verify(circle!==undefined)
    var p=circle.mapToItem(card,16,16)
    verify(Math.abs(p.x-(card.width/2-1))<0.00001)
    verify(p.y>=16 && p.y+16<card.height)
    var left=circle.mapToItem(card,0,0).x
    var right=card.width-left-circle.width
    verify(Math.abs((right-left)-2)<0.00001)
    var glyph=circle.children[0].mapToItem(card,8,8)
    verify(Math.abs(glyph.x-p.x)<0.51)
    verify(Math.abs(glyph.y-p.y)<0.51)
    var label=content.children[1]
    var labelPosition=label.mapToItem(card,0,0)
    verify(labelPosition.y+label.height<card.height)
    mousePress(card,card.width/2,card.height/2);wait(60);compare(card.scale,1)
    mouseRelease(card,card.width/2,card.height/2);wait(100);compare(card.scale,1)
    compare(root.profileActions,i+1)
    console.log(cards[i].modelData.profile,"button",card.width,card.height,"circle centre",p.x,p.y)
   }
  }
 }
}'''.replace('ROW',row)
 (stage/'tst_centres.qml').write_text(qml)
 for path in [stage]+list(stage.rglob('*')):os.chown(path,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(repo/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=15)
 log=result.stdout+result.stderr;Path(__file__).with_suffix('.log').write_text(log);print(log);assert result.returncode==0
finally:shutil.rmtree(stage)
