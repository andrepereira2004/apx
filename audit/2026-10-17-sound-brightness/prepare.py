from pathlib import Path
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent;s=r/'config/environment-shell-v1'
rels=['quickshell/apx/ControlDashboard.qml','quickshell/apx/shell.qml']
for rel in rels:
 t=(s/rel).read_text()
 if rel.endswith('ControlDashboard.qml'):
  t=t.replace('readonly property bool brightnessPressed: brightness.pressed','readonly property bool brightnessPressed: false')
  start=t.index('    Rectangle {\n        width: dashboard.width; height: levels.')
  end=t.index('    Rectangle {\n        width: dashboard.width; height: sessionActions.',start)
  t=t[:start]+'''    Rectangle {
        width: dashboard.width; height: 84; radius: 18
        color: dashboard.controller.popupPanel
        border.width: 1; border.color: dashboard.controller.shellBorder
        ControlTile {
            x: 10; y: 10; width: parent.width - 20; height: 64; radius: 14
            iconName: "volume-2"; caption: "Som e brilho"; showCaption: true
            onActivated: dashboard.controller.openControlSection("brightness")
            Row {
                anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; spacing: 10
                LucideIcon { name: dashboard.controller.volumeMuted ? "volume-x" : "volume-2"; width: 16; height: 16; opacity: dashboard.controller.volumeMuted ? .4 : 1 }
                LucideIcon { name: "sun"; width: 16; height: 16 }
                LucideIcon { name: "chevron-right"; width: 16; height: 16 }
            }
        }
    }
'''+t[end:]
 if rel.endswith('shell.qml'):
  anchor='                        IconLabel { iconName: "sun"; text: "Brilho do ecrã";'
  idx=t.index(anchor,t.index('visible: root.renderedControls.controlsBrightnessOpen'))
  t=t[:idx]+'''                        ControlTile { width: implicitWidth; height: 28; color: "transparent"; showCaption: true; iconName: root.volumeMuted ? "volume-x" : "volume-2"; caption: "Som"; onActivated: root.openControlSection("audio") }
                        Text { text: root.volumeValue + "%"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                        ControlSlider {
                            id: combinedVolumeSlider
                            width: parent.width; height: 36; from: 0; to: 100; stepSize: 1; activeFocusOnTab: true
                            Accessible.name: "Volume"
                            onMoved: { root.previewVolume(value); if (!pressed) root.commitVolume(value) }
                            onPressedChanged: if (!pressed) root.commitVolume(value)
                            Binding { target: combinedVolumeSlider; property: "value"; value: root.volumeMuted ? 0 : root.volumeValue; when: !combinedVolumeSlider.pressed }
                        }
'''+t[idx:]
  anchor='                        ControlTile { width: parent.width; height: 42; showCaption: true; iconName: "keyboard"; caption: "Iluminação do teclado";'
  idx=t.index(anchor)
  t=t[:idx]+'''                        ControlTile { width: parent.width; height: 42; showCaption: true; iconName: root.microphoneMuted ? "mic-off" : "mic"; caption: "Microfone"; onActivated: root.openControlSection("microphone") }
'''+t[idx:]
 dest=a/'assets'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(t)
(a/'transform.py').write_text('from pathlib import Path\nRELATIVES='+repr(rels)+'\ndef transform(rel,s):\n return (Path(__file__).parent/"assets"/rel).read_text()\n')
(r/'scripts/physical-pilot/deploy-sound-brightness-20261017.py').write_text((r/'scripts/physical-pilot/deploy-controls-motion-20261017.py').read_text().replace('controls-motion','sound-brightness').replace('controls_motion','sound_brightness'))
(a/'validate-candidate.py').write_text((r/'audit/2026-10-17-controls-motion/validate-candidate.py').read_text().replace('controls-motion','sound-brightness').replace('motion-validation','sound-brightness-validation'))
