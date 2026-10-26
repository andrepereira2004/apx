from pathlib import Path
import json,os,shutil,subprocess
repo=Path(__file__).resolve().parents[2];state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/state['name']/'home/apx';stage=home/'.cache/apx-media-hover-test';assert not stage.exists();stage.mkdir();meta=home.stat()
try:
 source=repo/'config/environment-shell-v1/quickshell/apx'
 for name in ['MediaIsland.qml','BounceMouseArea.qml','MenuHover.qml']:shutil.copy2(source/name,stage/name)
 (stage/'qmldir').write_text('singleton Appearance 1.0 Appearance.qml\nsingleton DesktopActivity 1.0 DesktopActivity.qml\n')
 (stage/'Appearance.qml').write_text('pragma Singleton\nimport QtQuick\nQtObject { property color capsuleSurface: "#10121a"; property color iconColor: "white"; property string fontFamily: "sans-serif"; property bool tintButtons: false; property color hover: "#292d3a" }')
 (stage/'DesktopActivity.qml').write_text('pragma Singleton\nimport QtQuick\nQtObject { property var state: ({players:[{title:"Sample",status:"Playing",length:0}]}); function hasMedia(p) { return true } function position(p) { return 0 } }')
 for name in ['LucideIcon','ControlIcon']:(stage/(name+'.qml')).write_text('import QtQuick\nItem { property string name: ""; property url source; property color tint }')
 (stage/'tst_hover.qml').write_text('''import QtQuick
import QtTest
Item {
 id: root; width: 400; height: 150
 MediaIsland { id: media; x:20; y:20; width: selected ? 36 : 220; Behavior on width { NumberAnimation { duration: 300; easing.type: Easing.OutCubic } } hoverOverride: false }
 TestCase {
  name: "MediaHover"; when: windowShown
  function test_overlay_to_bar_handoff() {
   mouseMove(root,350,120)
   media.hoverOverride=true;media.selected=true;wait(400)
   var border=media.children[0].border.color.toString()
   media.beginHoverHandoff(true)
   compare(border,Appearance.iconColor.toString())
   media.selected=false;media.hoverOverride=false
   border="#69728a"
   compare(media.color.toString(),"#f2292d3a")
   compare(media.children[0].border.color.toString(),border)
   wait(32)
   compare(media.color.toString(),"#f2292d3a")
   media.hoverOverride=null
   compare(media.children[0].border.color.toString(),border)
   compare(media.visuallyHovered,true)
   compare(media.color.toString(),"#f2292d3a")
   wait(180);compare(media.visuallyHovered,true)
   mouseMove(media,10,16);wait(32)
   compare(media.visuallyHovered,true)
   compare(media.color.toString(),"#f2292d3a")
   wait(350);compare(media.width,220)
   compare(media.children[0].border.color.toString(),border)
   compare(media.visuallyHovered,true)
   var progress=media.children.filter(c=>c.objectName==="mediaPreviewProgress")[0]
   compare(progress.x,18);compare(media.width-progress.x-progress.width,18)
   mouseMove(root,350,120);wait(150)
   compare(media.visuallyHovered,false)
   compare(media.color.toString(),Appearance.capsuleSurface.toString())
   media.beginHoverHandoff(true)
   media.endHoverHandoff()
   media.hoverOverride=false;media.hoverOverride=null
   compare(media.visuallyHovered,false)
   media.hoverOverride=false
  }
  function test_selection_surface() {
   media.hoverOverride=false;media.selected=false;wait(400)
   var outline=media.children[0]
   var base=outline.border.color.toString()
   media.selected=true
   compare(outline.border.color.toString(),Appearance.iconColor.toString())
   compare(media.color.toString(),"#f2292d3a")
   var fill=media.color.toString(),border=outline.border.color.toString()
   for (var frame=0;frame<22;frame++) {
    wait(16)
    compare(media.selected,true)
    compare(media.color.toString(),fill)
    compare(outline.border.color.toString(),border)
    compare(outline.border.width,1)
    if(frame===4) verify(media.width>36 && media.width<220)
   }
   compare(media.width,36)
   media.hoverOverride=true;wait(140)
   compare(media.color.toString(),fill);compare(outline.border.color.toString(),border)
   media.hoverOverride=false;wait(140)
   compare(media.color.toString(),fill);compare(outline.border.color.toString(),border)
   media.selected=false;wait(400)
   mousePress(media,100,16);wait(60);compare(media.scale,1)
   mouseRelease(media,100,16);wait(100);compare(media.scale,1)
  }
  function test_restoration() {
   wait(400);compare(media.color.toString(),Appearance.capsuleSurface.toString())
   var outline=media.children[0];compare(outline.anchors.margins,1)
   media.hoverOverride=true;wait(150);compare(outline.border.color.toString(),"#69728a");compare(outline.border.width,1);verify(media.color.toString()!==Appearance.capsuleSurface.toString())
   media.hoverOverride=false;wait(150);compare(outline.border.color.toString(),"#304f566c");compare(media.color.toString(),Appearance.capsuleSurface.toString())
   media.selected=true;wait(150);verify(media.color.toString()!==Appearance.capsuleSurface.toString())
   media.selected=false;wait(150);compare(media.color.toString(),Appearance.capsuleSurface.toString())
   mouseMove(media,100,15);wait(150);compare(media.color.toString(),Appearance.capsuleSurface.toString())
   media.hoverOverride=null;mouseMove(media,101,15);wait(150);verify(media.color.toString()!==Appearance.capsuleSurface.toString())
   mouseMove(media,270,65);wait(150);compare(media.color.toString(),Appearance.capsuleSurface.toString())
  }
 }
}''')
 for path in [stage]+list(stage.iterdir()):os.chown(path,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(repo/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=15)
 log=result.stdout+result.stderr;(Path(__file__).parent/'validation.log').write_text(log);print(log);assert result.returncode==0
finally:shutil.rmtree(stage)
