#!/usr/bin/env python3
"""Finish owner-authorized creator UI and deletion backup coverage; no packages."""
import ast
import datetime
import fcntl
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

REPO=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('foundation_deploy',REPO/'scripts/physical-pilot/deploy-desktop-foundation-20261004.py')
deploy=importlib.util.module_from_spec(spec);spec.loader.exec_module(deploy)


def labels(text):
    return text.replace('additions: "+ Brave · PDF · MPV"','additions: "+ PDF · MPV · impressão"').replace('description: "Tudo do Intermédio, Office, periféricos e programação."','description: "Tudo do Intermédio, Office e programação."').replace('additions: "+ LibreOffice · dev · impressão"','additions: "+ LibreOffice · programação"')


def main():
    assert Path('/etc/hostname').read_text().strip()=='apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
    assert not Path('/run/apx/system-power-v1.reserved').exists()
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for name in deploy.NAMES:
            assert json.loads((deploy.BASE/name/'registration.json').read_text())['state']=='stopped'
        plan={}
        source=deploy.SOURCE
        for base in [deploy.SEED]+[deploy.BASE/name/'home/apx/.config' for name in deploy.NAMES]:
            qml=base/'quickshell/apx/shell.qml';plan[qml]=labels(qml.read_text()).encode()
            for relative in ['local/bin/apx-settings','local/bin/apx-desktop-preferences-v1']:
                target=base/relative if base==deploy.SEED else base.parent/'.local'/Path(relative).relative_to('local')
                plan[target]=(source/relative).read_bytes()
        qml=deploy.BASE/'hub/home/apx/.config/quickshell/apx/shell.qml'
        before='return environmentModuleCatalog.slice(0, 14).map(function(item) { return item.key }).concat(["shortcuts"])'
        after='return environmentModuleCatalog.filter(function(item) { return item.key !== "office" && item.key !== "development" }).map(function(item) { return item.key })'
        text=qml.read_text();assert text.count(before)==1
        plan[qml]=labels(text.replace(before,after,1)).encode()
        runtime=Path('/usr/lib/apx/apx-lab-runtime.py');text=runtime.read_text()
        source_runtime=(REPO/'scripts/virtual-lab/apx-lab-runtime.py').read_text()
        begin=text.index('def purge_environment_backups(');end=text.index('\ndef snapshot(',begin)
        replacement=source_runtime[source_runtime.index('def purge_environment_backups('):source_runtime.index('\ndef snapshot(',source_runtime.index('def purge_environment_backups('))]
        text=text[:begin]+replacement+text[end:]
        begin=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',begin)+2
        assets=ast.literal_eval(text[begin:end].split('=',1)[1].strip())
        for relative in ['quickshell/apx/shell.qml','local/bin/apx-settings','local/bin/apx-desktop-preferences-v1']:
            assets[relative]=deploy.digest(plan[deploy.SEED/relative])
        text=text[:begin]+'ENVIRONMENT_SHELL_ASSETS = {\n'+''.join(f'    "{k}": "{v}",\n' for k,v in assets.items())+'}'+text[end:]
        compile(text,str(runtime),'exec');plan[runtime]=text.encode()
        backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-desktop-foundation-finish');backup.mkdir(mode=0o700)
        deploy.write_plan(plan,backup);print(backup)
        # Socket activation keeps printing available without running CUPS permanently.
        for name in deploy.NAMES:
            command=['systemd-nspawn','--quiet','--directory='+str(deploy.BASE/name/'root'),'--private-users=pick','--private-users-ownership=chown','--private-network','--register=no','/usr/bin/systemctl','enable','cups.socket']
            deploy.run(command)
            print(name+': CUPS socket enabled on demand')

if __name__=='__main__':main()
