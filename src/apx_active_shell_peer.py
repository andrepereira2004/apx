"""QuickShell ancestry within an already authorized active service."""
from pathlib import Path
import os

def quickshell_ancestor(peer, proc=Path('/proc')):
    # authorize() first proves the peer belongs to the trusted active unit.
    # Every ancestor must stay in that exact service cgroup boundary.
    lines = (proc / str(peer.pid) / 'cgroup').read_text().splitlines()
    groups = [line.split(':', 2)[2] for line in lines if line.startswith('0::')]
    if len(groups) != 1:
        raise PermissionError('Host console cgroup identity unavailable')
    parts = groups[0].split('/')
    if len(parts) < 3 or parts[1] != 'system.slice' or not parts[2].endswith('.service'):
        raise PermissionError('Host console service boundary differs')
    unit = '/system.slice/' + parts[2]
    current = peer.pid
    for _ in range(8):
        fields = dict(line.split(':', 1) for line in (proc / str(current) / 'status').read_text().splitlines() if ':' in line)
        parent = int(fields['PPid'].strip())
        if parent <= 1:
            break
        cgroups = (proc / str(parent) / 'cgroup').read_text().splitlines()
        if not any(line == '0::' + unit or line.startswith('0::' + unit + '/') for line in cgroups):
            break
        if (proc / str(parent) / 'comm').read_text().strip() == 'quickshell' and os.readlink(proc / str(parent) / 'exe') == '/usr/bin/quickshell':
            return parent
        current = parent
    raise PermissionError('Host-console caller is not an active QuickShell descendant')

