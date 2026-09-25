#!/usr/bin/env python3
"""Hub UI/CLI for the APX coordinated-update service."""

from __future__ import annotations

import argparse
import json
import socket
import sys
import os
import subprocess
import time

# A bounded live repair may bind a replacement endpoint without restarting Hub.
# Fresh sessions use the normal launcher-provided socket.
SOCKET = ("/run/apx/coordinated-update-live-v1.sock"
          if os.path.exists("/run/apx/coordinated-update-live-v1.sock")
          else "/run/apx/coordinated-update-v1.sock")


def exchange(operation: str, payload: dict[str, object]) -> dict[str, object]:
    request = (json.dumps({"operation": operation, "payload": payload}, sort_keys=True,
                          separators=(",", ":")) + "\n").encode()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(15); connection.connect(SOCKET); connection.sendall(request)
        data = bytearray()
        while b"\n" not in data and len(data) <= 65536:
            chunk = connection.recv(4096)
            if not chunk: break
            data.extend(chunk)
    response = json.loads(data)
    if not response.get("ok"): raise RuntimeError(str(response.get("error")))
    return response["result"]


def ui() -> int:
    previous = exchange("status", {})
    if previous.get("state") in {"complete", "failed"}:
        print("\nResultado da última operação:", previous.get("message", previous["state"]))
        if previous.get("reboot_required"):
            print("O Host precisa de reiniciar. O APX nunca reinicia sem a sua decisão.")
    plan = exchange("preview", {})
    print("\nAPX — PRÉ-VISUALIZAÇÃO DA ATUALIZAÇÃO\n")
    print("Incluídos:", ", ".join(item["name"] for item in plan["targets"]))
    print("Excluídos:", ", ".join(plan["excluded_environments"]) or "nenhum")
    if plan["blockers"]:
        print("\nOperação bloqueada:", ", ".join(plan["blockers"])); input("\nEnter para fechar..."); return 2
    print("\nSerá criada uma cópia de segurança independente antes de alterar cada sistema.")
    print("Se alguma parte falhar, tudo para e as cópias ficam guardadas para recuperação controlada.")
    if input("\nEscreva CONFIRMAR para iniciar: ").strip() != "CONFIRMAR":
        print("Cancelado sem alterações."); return 1
    result = exchange("apply", {"plan_digest": plan["plan_digest"], "confirmation": "CONFIRMAR"})
    print("\n", result["message"]); input("\nEnter para fechar..."); return 0


def environments_ui() -> int:
    current = exchange("environments.status", {})
    if current.get("state") not in ("queued", "running", "awaiting-hub"):
        plan = exchange("environments.preview", {})
        print("\nAtualizar todos os Environments: " + ", ".join(item["name"] for item in plan["targets"]), flush=True)
        if plan["blockers"]:
            print("Não é possível atualizar: " + ", ".join(plan["blockers"])); return 2
        print("Serão atualizados o sistema, as aplicações AUR e os Flatpaks de cada Environment.")
        print("Os outros Environments são atualizados primeiro; o Hub fica para o fim.")
        print("Cada Environment terá uma cópia de segurança. O Host não é atualizado.")
        if input("\nEscreve CONFIRMAR para começar: ").strip() != "CONFIRMAR": return 1
        current = exchange("environments.apply", {"plan_digest": plan["plan_digest"], "confirmation": "CONFIRMAR"})
    operation_id = current["operation"]
    last = None
    while current["state"] in ("queued", "running"):
        progress = (current["state"], current.get("current"), tuple(current.get("completed", [])))
        if progress != last:
            print("A atualizar: " + (current.get("current") or "a preparar"), flush=True)
            if current.get("completed"): print("Concluídos: " + ", ".join(current["completed"]), flush=True)
            last = progress
        time.sleep(2)
        current = exchange("environments.status", {})
        if current.get("operation") != operation_id: raise RuntimeError("Update operation changed")
    if current["state"] != "awaiting-hub":
        print(current.get("error") or current.get("message", "A atualização parou.")); return 2
    print("\nA atualizar o Hub…", flush=True)
    result = subprocess.run(["/home/apx/.local/bin/apx-environment-update-v1"])
    if result.returncode:
        print("O Hub não terminou a atualização. Abre Atualizar para retomar."); return result.returncode
    final = exchange("environments.finish", {"operation": operation_id})
    print(final["message"], flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("mode", choices=("preview", "status", "include", "exclude", "ui", "environments-ui")); parser.add_argument("environment", nargs="?")
    args = parser.parse_args()
    if args.mode == "environments-ui":
        try: return environments_ui()
        finally:
            try: input("\nEnter para fechar…")
            except (EOFError, KeyboardInterrupt): pass
    if args.mode == "ui": return ui()
    if args.mode == "preview": print(json.dumps(exchange("preview", {}), ensure_ascii=False, indent=2)); return 0
    if args.mode == "status": print(json.dumps(exchange("status", {}), ensure_ascii=False, indent=2)); return 0
    if not args.environment: parser.error("Environment required")
    policy = "follow-host" if args.mode == "include" else "excluded"
    print(json.dumps(exchange("policy.set", {"environment": args.environment, "policy": policy}), indent=2)); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"APX update unavailable: {error}", file=sys.stderr); raise SystemExit(3)
