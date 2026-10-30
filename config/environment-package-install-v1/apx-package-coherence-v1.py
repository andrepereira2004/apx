#!/usr/bin/python3
"""Refuse partial repository upgrades before they can break an Environment."""
from pathlib import Path
import os
import subprocess
import sys

HOST_GPU_PACKAGES = frozenset(('nvidia-utils', 'lib32-nvidia-utils', 'opencl-nvidia'))


def check_transaction(targets, pending):
    """Every pending repository upgrade must participate in this transaction."""
    return sorted(set(pending) - set(targets) - HOST_GPU_PACKAGES)


def main():
    if os.geteuid() != 0 or Path('/run/systemd/container').read_text().strip() != 'systemd-nspawn':
        raise RuntimeError('Esta verificação pertence apenas ao gestor de pacotes de um Environment.')
    targets = set(sys.stdin.read().splitlines())
    if not targets:
        raise RuntimeError('Não foi possível identificar a transação de pacotes.')
    env = {**os.environ, 'LC_ALL': 'C'}
    result = subprocess.run(['/usr/bin/pacman', '-Quq'], capture_output=True, text=True, env=env)
    if result.returncode not in (0, 1) or result.stderr.strip():
        raise RuntimeError('Não foi possível verificar as versões dos pacotes; instalação interrompida.')
    missing = check_transaction(targets, result.stdout.splitlines())
    if missing:
        raise RuntimeError(
            'Instalação interrompida para evitar dependências incompatíveis. '
            f'Faltam {len(missing)} atualizações nesta transação (ex.: ' + ', '.join(missing[:6]) + '). '
            'Atualiza este Environment pelo botão Atualizar antes de repetir a instalação, '
            'ou usa pacman/yay -Syu em vez de -S. Mantém os pacotes NVIDIA na versão do Host.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as error:
        print('APX: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
