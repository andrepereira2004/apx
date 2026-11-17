#!/usr/bin/env python3
"""Show the APX LocalSend peer toast and apply its typed address."""
from __future__ import annotations

import importlib.util
import ipaddress
import subprocess
import sys

CLIENT = "/run/apx/host-services-client-v3.py"
APP = "/opt/localsend/localsend_app"


def exchange(operation: str, payload: dict[str, object]) -> dict[str, object]:
    spec = importlib.util.spec_from_file_location("apx_host_services_client_v3", CLIENT)
    if spec is None or spec.loader is None:
        raise RuntimeError("O serviço de rede APX não está disponível")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.exchange(operation, payload)


def main() -> int:
    if len(sys.argv) == 1:
        exchange("localsend.peer.get", {})
        subprocess.run(["/usr/bin/notify-send", "-a", "LocalSend", "-i", "localsend",
                        "-c", "apx-localsend-peer", "-e", "-t", "0",
                        "Introduzir o IP do telemóvel."], check=True)
        return 0
    if len(sys.argv) == 3 and sys.argv[1] == "--apply":
        address = sys.argv[2].strip()
        if str(ipaddress.IPv4Address(address)) != address:
            raise ValueError("Endereço IPv4 inválido")
        exchange("localsend.peer.set", {"address": address})
        subprocess.Popen([APP], start_new_session=True)
        return 0
    raise ValueError("Argumentos LocalSend inválidos")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"LocalSend: {error}", file=sys.stderr)
        raise SystemExit(1)
