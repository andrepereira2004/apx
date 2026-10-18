from pathlib import Path
r=Path(__file__).resolve().parents[2]; a=Path(__file__).parent;s=r/'config/environment-shell-v1'
rels=['quickshell/apx/PersonalizationPanel.qml','quickshell/apx/ControlDashboard.qml','quickshell/apx/ControlTile.qml','quickshell/apx/shell.qml','quickshell/apx/Appearance.qml','local/bin/apx-appearance-v1','rofi/config.rasi','quickshell/apx/icons/lucide/paintbrush.svg']
for rel in rels:
 p=s/rel;t=p.read_text() if p.exists() else ''
 if rel.endswith('PersonalizationPanel.qml'):
  start=t.index('    function selectTarget(');end=t.index('    function applyColor()',start);t=t[:start]+t[end:]
  t=t.replace('style[key] = value','style[key] = value\n        style.icons = true; style.buttons = false; style.windows = false')
  t=t.replace('Cor e superfícies','Cor dos ícones')
  start=t.index('    Repeater {\n        model: [{ key: "icons"');end=t.index('    Action {\n        visible: panel.scope',start);t=t[:start]+t[end:]
 if rel.endswith('ControlTile.qml'):
  t=t.replace('implicitWidth: 48','implicitWidth: showCaption ? captionText.implicitWidth + 48 : 48')
  t=t.replace('    Text {\n        visible: tile.showCaption','    Text {\n        id: captionText\n        visible: tile.showCaption')
 if rel.endswith('ControlDashboard.qml'):
  t=t.replace('width: parent.width; height: 28; color: "transparent"','width: implicitWidth; height: 28; color: "transparent"')
 if rel.endswith('Appearance.qml'):
  t=t.replace('!!(state.effective_style && state.effective_style.buttons)','false').replace('!!(state.effective_style && state.effective_style.windows)','false')
 if rel.endswith('shell.qml'):
  t=t.replace('iconName: "settings"; label: "Personalização"','iconName: "paintbrush"; label: "Personalização"')
  start=t.index('                        MenuSlider {\n                            id: mouseSensitivitySlider');end=t.index('\n                    Text { visible: root.mouseSensitivityError',start)
  t=t[:start]+'''                        ControlSlider {
                            id: mouseSensitivitySlider
                            anchors.left: parent.left; anchors.leftMargin: 12; anchors.right: parent.right; anchors.rightMargin: 12
                            anchors.bottom: parent.bottom; anchors.bottomMargin: 3
                            height: 36; from: -100; to: 100; stepSize: 1
                            activeFocusOnTab: true
                            Accessible.name: "Sensibilidade do rato"
                            enabled: !mouseSensitivityProcess.running
                            onMoved: if (!pressed) root.setMouseSensitivity(value)
                            onPressedChanged: if (!pressed) root.setMouseSensitivity(value)
                            Binding { target: mouseSensitivitySlider; property: "value"; value: root.mouseSensitivity; when: !mouseSensitivitySlider.pressed }
                            background: Rectangle {
                                x: mouseSensitivitySlider.leftPadding; y: (mouseSensitivitySlider.height - height) / 2
                                width: mouseSensitivitySlider.availableWidth; height: 6; radius: 3; color: "#303644"
                                Rectangle { width: Math.max(6, parent.width * mouseSensitivitySlider.visualPosition); height: parent.height; radius: 3; color: "#c9d2e5" }
                            }
                        }
                    }'''+t[end:]
  t=t.replace('width: root.ghostGreetingVisible ? Math.min(ghostBarText.implicitWidth + 16, budget) : 0','property real reveal: root.ghostGreetingVisible ? 1 : 0\n                    width: Math.min(ghostBarText.implicitWidth + 16, budget) * reveal')
  t=t.replace('opacity: root.ghostGreetingVisible ? 1 : 0\n                    Behavior on width { NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }\n                    Behavior on opacity { NumberAnimation { duration: 180 } }','opacity: reveal\n                    Behavior on reveal { NumberAnimation { duration: 320; easing.type: Easing.InOutCubic } }')
  t=t.replace('x: 8; width: Math.max(0, parent.width - 16); height: parent.height; clip: true','x: 8; width: ghostBarText.implicitWidth; height: parent.height; clip: false')
 if rel.endswith('apx-appearance-v1'):
  t=t.replace("return {**value, 'color': color(value['color'])}","return {**DEFAULT_STYLE, 'color': color(value['color'])}")
  t=t.replace("window_surface = surface if style['windows'] else '#303445'","window_surface = '#0a1014'")
  t=t.replace("'; }']","'; }']") # preserve existing CSS structure
  t=t.replace("'.thunar menu, .thunar popover { background-color: ' + window_surface + '; }'","'.thunar menu, .thunar popover { background-color: rgba(' + rgb + ', 0.85); }'")
 if rel=='rofi/config.rasi':t=t.replace('#303445d9','#0a1014d9').replace('#303445e6','#0a1014e6')
 if rel.endswith('paintbrush.svg'):
  t='<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m14.06 9.94 6.92-6.92a1.5 1.5 0 0 1 2.12 2.12l-6.92 6.92"/><path d="M16 12 12 8l-8 8a4 4 0 0 0 0 6c2 0 4 0 6-2Z"/><path d="m9 11 4 4"/></svg>\n'
 dest=a/'assets'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(t)
(a/'transform.py').write_text('from pathlib import Path\nRELATIVES='+repr(rels)+'\ndef transform(rel,s):\n return (Path(__file__).parent/"assets"/rel).read_text()\n')
deploy=(r/'scripts/physical-pilot/deploy-controls-motion-20261017.py').read_text().replace('controls-motion','personalization-compact').replace('controls_motion','personalization_compact')
deploy=deploy.replace("base/'.config'/rel","base/('.local/'+rel[6:] if rel.startswith('local/') else '.config/'+rel)")
(r/'scripts/physical-pilot/deploy-personalization-compact-20261017.py').write_text(deploy)
v=(r/'audit/2026-10-17-controls-motion/validate-candidate.py').read_text().replace('controls-motion','personalization-compact').replace('motion-validation','personalization-validation')
(a/'validate-candidate.py').write_text(v)
