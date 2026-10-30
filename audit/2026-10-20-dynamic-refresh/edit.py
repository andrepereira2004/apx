from pathlib import Path
repo=Path(__file__).resolve().parents[2];base=repo/'config/environment-shell-v1';p=base/'quickshell/apx/shell.qml';s=p.read_text()
s=s.replace('id: pointerRefreshTimer; interval: 2000','id: pointerRefreshTimer; interval: 500')
s=s.replace('''        interval: 750
        running: true''','''        interval: 500
        running: true''',1)
s=s.replace('''        interval: 10000
        running: true''','''        interval: 500
        running: true''',1)
s=s.replace('interval: root.modelStoreBusy ? 500 : 5000;', 'interval: 500;')
s=s.replace('''        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: if (!audioStateProcess.running)''','''        interval: 500
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: if (!audioStateProcess.running)''')
# Request fresh information on opening, in addition to continuous reconciliation.
s=s.replace('''        popup.open = true
        popupAnimationPending = true''','''        popup.open = true
        root.refreshDynamicStatus()
        popupAnimationPending = true''',1)
pos=s.index('    function updateClock() {');s=s[:pos]+'''    property var dynamicReadMetrics: ({})
    function recordDynamicRead(kind, started) {
        var now = Date.now()
        var reads = Object.assign({}, dynamicReadMetrics)
        reads[kind] = {sample: now, elapsed: now - started}
        dynamicReadMetrics = reads
    }
    function refreshDynamicStatus() {
        if (!hostStatusProcess.running) hostStatusProcess.running = true
        if (!volumeProcess.running) volumeProcess.running = true
        if (!microphoneProcess.running) microphoneProcess.running = true
        if (!batteryProcess.running) batteryProcess.running = true
        if (!hardwareProfileProcess.running) hardwareProfileProcess.running = true
        if (!audioStateProcess.running) audioStateProcess.running = true
        if (!radioStatusProcess.running) radioStatusProcess.running = true
    }

'''+s[pos:]
# Bounded read-only diagnostic timings: sample when the query actually finishes.
for process,kind in [('hostStatusProcess','network'),('volumeProcess','volume'),('microphoneProcess','microphone'),('batteryProcess','battery'),('audioStateProcess','audio'),('hardwareProfileProcess','hardware')]:
 marker='        id: '+process+'\n';a=s.index(marker);b=s.index('\n    }',a);part=s[a:b]
 part=part.replace(marker,marker+'        property double readStarted: 0\n',1)
 if process=='hardwareProfileProcess':
  part=part.replace('onStarted: { response = "";', 'onStarted: { readStarted = Date.now(); response = "";',1)
  part=part.replace('onExited: (exitCode, exitStatus) => {', 'onExited: (exitCode, exitStatus) => {\n            if (exitCode === 0) root.recordDynamicRead("hardware", readStarted)',1)
 else:
  part=part.replace('        property double readStarted: 0\n','        property double readStarted: 0\n        onStarted: readStarted = Date.now()\n        onExited: (code, status) => { if (code === 0) root.recordDynamicRead("'+kind+'", readStarted) }\n',1)
 s=s[:a]+part+s[b:]
s=s.replace('displayed_controls: root.renderedControls,', 'dynamic_reads: root.dynamicReadMetrics, displayed_controls: root.renderedControls,',1)
p.write_text(s)
p=base/'quickshell/apx/DesktopActivity.qml';s=p.read_text().replace('interval: 10000; running: true;', 'interval: 500; running: true;').replace('interval: 2000; running: !activity.watchProcess.running;', 'interval: 500; running: !activity.watchProcess.running;');p.write_text(s)
p=base/'local/bin/apx-desktop-activity-v1';s=p.read_text().replace('GLib.timeout_add_seconds(2,lambda:(schedule(),True)[1])','GLib.timeout_add(500,lambda:(schedule(),True)[1])');p.write_text(s)
p=base/'quickshell/apx/Appearance.qml';s=p.read_text().replace('interval: 5000; running: true;', 'interval: 500; running: true;');p.write_text(s)
p=repo/'scripts/physical-pilot/deploy-controls-followup-20261020.py';s=p.read_text().replace('RELATIVES = [',"RELATIVES = ['quickshell/apx/DesktopActivity.qml', 'quickshell/apx/Appearance.qml', 'local/bin/apx-desktop-activity-v1', ",1);p.write_text(s)
