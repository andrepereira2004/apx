import json
from pathlib import Path
import subprocess
import time

RESULT = Path(__file__).with_name('2026-10-13-environment-return.json')
HUB = '/var/lib/apx/official-hub-v1/apx-official-hub-graphical-v1.py'
GENERAL = '/usr/lib/apx/apx-graphical-environment-v1.py'
RUNNER = '/usr/lib/apx/apx-environment-switch-runner-v1.py'
ACTIVE = Path('/run/apx/active-graphical-environment-v1.json')
HUB_ACTIVE = Path('/run/apx/official-hub-graphical-v1.json')
LOCK = Path('/run/apx/environment-handoff-v1.lock')
results = []

def run(args):
    result = subprocess.run(args, text=True, capture_output=True, timeout=35)
    if result.returncode: raise RuntimeError(f'{args[0]}: {result.stderr[-1500:]}')
    return result.stdout

def wait_state(path, name=None):
    until = time.monotonic() + 30
    while time.monotonic() < until:
        try:
            value = json.loads(path.read_text())
            if name is None or value.get('name') == name:
                return value
        except (OSError, ValueError): pass
        time.sleep(.2)
    raise RuntimeError(f'{path} did not become ready')

def launch(unit, args):
    run(['systemd-run',f'--unit={unit}','--collect',*args])

try:
    wait_state(HUB_ACTIVE)
    for index, (name, mode) in enumerate([('hytale','missing'),('minecraft','stale'),
                                          ('steam','missing'),('faculdade','missing'),
                                          ('hytale','supervised')]):
        print(f'Checking {name}: {mode}', flush=True)
        run([HUB,'--recover'])
        # Leave the previous Hub supervisor time to finish cleanup.
        time.sleep(1)
        if mode == 'supervised':
            launch(f'apx-return-validation-supervised-{index}', [RUNNER,'--environment',name])
        else:
            launch(f'apx-return-validation-workload-{index}', [GENERAL,'--environment',name,'--interactive'])
        active = wait_state(ACTIVE,name)
        if mode == 'stale':
            LOCK.write_text('abandoned validation supervisor\n')
            LOCK.chmod(0o600)
        if mode == 'missing' and LOCK.exists(): raise RuntimeError('unexpected handoff lock')
        record=json.loads((Path('/var/lib/apx/environments')/name/'registration.json').read_text())
        machine='apx-g'+record['generation'][:7]
        reply=run(['systemd-run','-M',machine,'--quiet','--pipe','--wait','--collect','--uid=apx','--',
                   '/run/apx/environment-switch-client-v1.py','return'])
        hub=wait_state(HUB_ACTIVE)
        time.sleep(2)
        if ACTIVE.exists(): raise RuntimeError('workload active state remained after return')
        if LOCK.exists(): raise RuntimeError('handoff lock remained after return')
        results.append({'environment':name,'mode':mode,'return_reply':reply.strip(),'hub':hub,'passed':True})
        RESULT.write_text(json.dumps(results,indent=2)+'\n')
        print(f'PASS {name}: {mode}; Hub active',flush=True)
except Exception as error:
    results.append({'error':str(error)});RESULT.write_text(json.dumps(results,indent=2)+'\n')
    print(f'FAILED: {error}',flush=True)
    raise
