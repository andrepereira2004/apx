#!/usr/bin/env python3
"""Stage portable native code/services for a future installation only."""
from pathlib import Path
import hashlib
import json
import shutil

REPO=Path(__file__).resolve().parents[2]
MODULES=('apx_portable_native.py','apx_portable_native_io.py','apx_portable_native_media.py',
         'apx_portable_native_worker.py','apx_portable_native_hub.py','apx_native_slot_wipe_v3.py')


def copy_runtime(root):
    library=root/'usr/lib/apx';library.mkdir(parents=True,exist_ok=True)
    for name in MODULES:shutil.copyfile(REPO/'src'/name,library/name);(library/name).chmod(0o644)
    shutil.copyfile(REPO/'scripts/portable/apx-portable-native.py',library/'apx-portable-native.py')
    (library/'apx-portable-native.py').chmod(0o755)


def recovery(root,write):
    copy_runtime(root)
    write(root,'etc/apx-portable-native-recovery-v4.json',json.dumps({
        'schema':4,'profile':'apx-portable-native-recovery-v4',
        'worker':'/usr/lib/apx/apx-portable-native.py',
        'files':{'usr/lib/apx/'+name:hashlib.sha256((root/'usr/lib/apx'/name).read_bytes()).hexdigest()
                 for name in MODULES+('apx-portable-native.py',)}})+'\n',0o600)
    write(root,'etc/systemd/system/apx-portable-native-offline.service','''[Unit]
Description=APX portable native explicit offline transaction
After=local-fs.target
Before=getty@tty1.service
ConditionPathExists=/var/lib/apx-native-v4/active.json

[Service]
Type=oneshot
ExecStart=/usr/bin/python /usr/lib/apx/apx-portable-native.py offline
TimeoutStartSec=infinity
TimeoutStopSec=120
UMask=0077
StandardOutput=journal+console
StandardError=journal+console

[Install]
WantedBy=multi-user.target
''')


def host(base):
    assets=Path('/usr/share/apx/portable-native-v4')
    shutil.copytree(REPO/'config/portable-native-v4',assets)
    files={}
    for name in MODULES+('apx-portable-native.py',):
        path=Path('/usr/lib/apx')/name;files[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    for path in assets.iterdir():
        if path.is_file():files[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    base.write(assets/'release.json',json.dumps(dict(schema=4,profile='apx-portable-native-release-v4',
        implementation='experimental-source-only',installation_validation=False,files=files),indent=2)+'\n',0o600)
    base.write(Path('/usr/bin/apx-native-windows'), '#!/bin/sh\nexec /usr/bin/python /usr/lib/apx/apx-portable-native.py "$@"\n', 0o755)
    base.write(Path('/etc/systemd/system/apx-portable-native-finalize.service'),'''[Unit]
Description=APX portable native return and exact-instance finalization
After=local-fs.target
Before=apx-portable-graphical.service apx-portable-environment-switch-v1.service
ConditionPathExists=/etc/apx-portable-native-identity-v4.json

[Service]
Type=oneshot
ExecStart=/usr/bin/python /usr/lib/apx/apx-portable-native.py finalize
TimeoutStartSec=600
UMask=0077

[Install]
WantedBy=multi-user.target
''')
    base.run('systemctl','enable','apx-portable-native-finalize.service')
