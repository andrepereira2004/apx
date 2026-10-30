from pathlib import Path
import re
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent;s=r/'config/environment-shell-v1'
rels=['quickshell/apx/ControlSlider.qml','quickshell/apx/Appearance.qml','quickshell/apx/PersonalizationPanel.qml','quickshell/apx/shell.qml']
for rel in rels:
 t=(s/rel).read_text()
 if rel.endswith('ControlSlider.qml'):
  t=t[:t.index('    handle: Rectangle {')]+'    handle: Item { width: 0; height: 0 }\n}\n'
  t=t.replace('height: 4; radius: 2','height: 6; radius: 3').replace('radius: 2; color: Appearance.iconColor','radius: 3; color: Appearance.iconColor')
 if rel.endswith('shell.qml'):
  t=re.sub(r'                                handle: Rectangle \{\n.*?\n                                \}', '                                handle: Item { width: 0; height: 0 }',t,flags=re.S)
 if rel.endswith('PersonalizationPanel.qml'):
  t=t.replace('            property int pendingOpacity: 0\n','')
  t=t.replace('activeFocusOnTab: true; enabled: !Appearance.busy','activeFocusOnTab: true')
  t=t.replace('when: !opacitySlider.pressed && !opacitySave.running','when: !opacitySlider.pressed')
  t=t.replace('onMoved: if (!pressed) { opacityRow.pendingOpacity = Math.round(value); opacitySave.restart() }','onMoved: Appearance.setOpacity(opacityRow.modelData.key, value)')
  t=t.replace('onPressedChanged: if (!pressed) { opacityRow.pendingOpacity = Math.round(value); opacitySave.restart() }','onPressedChanged: if (!pressed) Appearance.setOpacity(opacityRow.modelData.key, value)')
  t=t.replace('            Timer { id: opacitySave; interval: 180; onTriggered: Appearance.setOpacity(opacityRow.modelData.key, opacityRow.pendingOpacity) }\n','')
 if rel.endswith('Appearance.qml'):
  t=t.replace('    function opacityPercent(key) {','    property var pendingOpacity: ({})\n    property var opacityInFlight: ({})\n    function opacityPercent(key) {\n        if (pendingOpacity[key] !== undefined) return pendingOpacity[key]')
  start=t.index('    function setOpacity(');end=t.index('    readonly property color iconColor:',start)
  t=t[:start]+'''    function setOpacity(key, value) {
        var pending = Object.assign({}, pendingOpacity)
        pending[key] = Math.max(0, Math.min(100, Math.round(value)))
        pendingOpacity = pending
        opacitySave.restart()
    }
    function flushOpacity() {
        if (busy || !Object.keys(pendingOpacity).length) return
        opacityInFlight = Object.assign({}, pendingOpacity)
        change("opacity", JSON.stringify(opacityInFlight))
    }
    function finishOpacity() {
        var pending = Object.assign({}, pendingOpacity)
        Object.keys(opacityInFlight).forEach(function(key) {
            if (pending[key] === opacityInFlight[key]) delete pending[key]
        })
        pendingOpacity = pending
        opacityInFlight = ({})
        if (Object.keys(pending).length) opacitySave.restart()
    }
    property Timer opacitySave: Timer {
        interval: 180
        onTriggered: appearance.flushOpacity()
    }
'''+t[end:]
  t=t.replace('onExited: (code, status) => { if (code === 0) appearance.refresh() }','onExited: (code, status) => { appearance.finishOpacity(); if (code === 0) appearance.refresh() }')
  t=t.replace('onExited: (code, status) => { if (code === 0) appearance.error = "" }','onExited: (code, status) => { if (code === 0) appearance.error = ""; if (Object.keys(appearance.pendingOpacity).length) appearance.opacitySave.restart() }')
 dest=a/'assets'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(t)
(a/'transform.py').write_text('from pathlib import Path\nRELATIVES='+repr(rels)+'\ndef transform(rel,s):\n return (Path(__file__).parent/"assets"/rel).read_text()\n')
(r/'scripts/physical-pilot/deploy-slider-bars-20261017.py').write_text((r/'scripts/physical-pilot/deploy-controls-motion-20261017.py').read_text().replace('controls-motion','slider-bars').replace('controls_motion','slider_bars'))
(a/'validate-candidate.py').write_text((r/'audit/2026-10-17-controls-motion/validate-candidate.py').read_text().replace('controls-motion','slider-bars').replace('motion-validation','slider-bars-validation'))
