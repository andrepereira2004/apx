import json,os,re,shutil,subprocess,time
from pathlib import Path
repo=Path.cwd();out=repo/'audit/2026-10-20-environments-minimal'
a=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/a['name']/'home/apx';stage=home/'.cache/apx-env-menu-test';stage.mkdir(exist_ok=False)
runner=['python',str(repo/'audit/2026-10-16-lucide-bar/session-command.py')]
try:
 shutil.copytree(home/'.config/quickshell/apx',stage/'apx')
 s=(repo/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
 s=re.sub(r'readonly property bool isHub: identityReady\s*\? environmentIdentity.role === "hub"\s*: sessionHubProof','readonly property bool isHub: true',s)
 s=s.replace('/home/apx/.config/apx-environment-icons.ini','/home/apx/.cache/apx-env-menu-test/icons.ini')
 s=s.replace('environmentCatalogProcess.running = true', 'environmentCatalogProcess.running = false')
 s=s.replace('function refreshEnvironmentMenu() {','function refreshEnvironmentMenu() { return;')
 s=s.replace('        environmentMetadataProcess.running = true','        console.error("UNEXPECTED_METADATA_WRITE")')
 s=s.rsplit('}',1)[0]+'''
    property int testStep: 0
    Timer {
        interval: 1800; running: true; repeat: true
        onTriggered: {
            root.testStep++
            if (root.testStep === 1) {
                root.environmentCatalog = [{name:"demo-study", display_name:"Estudo", description:"Hidden description", generation:"test-1", state:"stopped"}, {name:"demo-work", display_name:"Trabalho", generation:"test-2", state:"stopped"}]
                root.toggleFocusedPopup("environments")
            } else if (root.testStep === 3) {
                root.environmentManagementBusy = false
                root.selectedEnvironmentName = "demo-study"
                root.selectedEnvironmentGeneration = "test-1"
                root.beginEnvironmentEdit()
                if (!root.environmentEditOpen) throw Error("edit did not open")
                root.environmentEditFocusIndex = 3
                root.handleEnvironmentEditKey({key:Qt.Key_Right, accepted:false})
                if (root.environmentEditIcon !== "monitor") throw Error("icon keyboard")
                root.storeEnvironmentIcon("demo-study:test-1", root.environmentEditIcon)
                if (root.environmentIcon(root.environmentCatalog[0]) !== "monitor") throw Error("icon save")
                if (root.environmentIcon({name:"demo-study",generation:"new"}) !== "box") throw Error("generation reuse")
                root.environmentEditFocusIndex = 4
            } else if (root.testStep === 5) {
                console.log("UI_PASS"); Qt.quit()
            }
        }
    }
}
'''
 (stage/'apx/shell.qml').write_text(s)
 for p in [stage]+list(stage.rglob('*')):os.chown(p,home.stat().st_uid,home.stat().st_gid)
 process=subprocess.Popen(runner+['quickshell','--path','/home/apx/.cache/apx-env-menu-test/apx/shell.qml','--no-color'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 time.sleep(3.8)
 for name,delay in [('list',0),('edit',4.8)]:
  time.sleep(delay);subprocess.run(runner+['grim','/home/apx/.cache/apx-env-menu-test/'+name+'.png'],check=True)
  shutil.copyfile(stage/(name+'.png'),out/(name+'.png'))
 log=process.communicate(timeout=12)[0];(out/'ui-candidate.log').write_text(log)
 assert 'UI_PASS' in log and 'UNEXPECTED_METADATA_WRITE' not in log,log[-2500:]
 assert 'monitor' in (stage/'icons.ini').read_text()
 print(log[-1600:]);print('UI and persisted icon PASS')
finally:
 if 'process' in locals() and process.poll() is None:process.terminate();process.wait(timeout=5)
 shutil.rmtree(stage)
