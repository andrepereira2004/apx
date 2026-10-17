#!/usr/bin/env python3
"""Open Host development links in the active graphical Environment's browser."""
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit


def main():
    if len(sys.argv) != 2:
        raise ValueError('Indique um endereço HTTP ou HTTPS.')
    url = sys.argv[1]
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or any(c in url for c in '\r\n\0'):
        raise ValueError('Apenas endereços HTTP e HTTPS são suportados.')
    state = json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
    pid = int(state['pid'])
    if pid <= 1 or Path(f'/proc/{pid}/comm').read_text().strip() != 'Hyprland':
        raise ValueError('Não existe uma sessão gráfica ativa.')
    # Use only selected session values, never import unrelated process secrets.
    environment = {}
    for entry in Path(f'/proc/{pid}/environ').read_bytes().split(b'\0'):
        key, sep, value = entry.partition(b'=')
        if sep and key in (b'XDG_RUNTIME_DIR', b'DBUS_SESSION_BUS_ADDRESS', b'WAYLAND_DISPLAY', b'HYPRLAND_INSTANCE_SIGNATURE'):
            environment[key.decode()] = value.decode()
    if 'XDG_RUNTIME_DIR' not in environment:
        raise ValueError('A sessão gráfica não tem runtime disponível.')
    if 'WAYLAND_DISPLAY' not in environment:
        sockets = [p for p in (Path(f'/proc/{pid}/root') / environment['XDG_RUNTIME_DIR'].lstrip('/')).glob('wayland-*') if p.is_socket()]
        if len(sockets) != 1:
            raise ValueError('Não foi possível identificar o ecrã Wayland ativo.')
        environment['WAYLAND_DISPLAY'] = sockets[0].name
    command = ['/usr/bin/nsenter', '-t', str(pid), '-m', '-U', '-p', '-n', '--',
               '/usr/bin/setpriv', '--reuid=1000', '--regid=1000', '--init-groups',
               '/usr/bin/env', '-i', 'HOME=/home/apx', 'USER=apx', 'LOGNAME=apx',
               'PATH=/home/apx/.local/bin:/usr/local/bin:/usr/bin', 'XDG_CURRENT_DESKTOP=Hyprland']
    command += [f'{key}={value}' for key, value in environment.items()]
    command += ['/usr/bin/xdg-open', url]
    return subprocess.run(command, cwd='/', check=False).returncode


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as error:
        print(f'Não foi possível abrir o navegador: {error}', file=sys.stderr)
        sys.exit(1)
