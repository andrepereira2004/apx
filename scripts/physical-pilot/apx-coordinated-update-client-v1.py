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


def explain_blockers(blockers):
    for blocker in blockers:
        if blocker == "host-reserve-unavailable":
            print("Espaço insuficiente: o APX exige pelo menos 96 GiB livres para preservar a reserva e as cópias de segurança.")
        elif blocker.startswith(("environment-state:", "environment-running:")):
            print("Fecha o Environment antes de atualizar: " + blocker.split(":", 1)[1])
        else:
            print("Bloqueio: " + blocker)


def authorize_update():
    print("\nAutorizar atualização: Enter para reconhecimento facial ou introduz a tua palavra-passe.", flush=True)
    result = subprocess.run(["/usr/bin/sudo", "-k", "-p",
                             "Enter para usar a cara / palavra-passe: ", "/usr/bin/true"])
    if result.returncode:
        print("Autorização recusada ou cancelada. Nenhuma atualização foi iniciada.", flush=True)
        return False
    return True


def full_ui():
    print("\nAPX — Atualizar tudo: Arch Linux, kernel, drivers e aplicações.", flush=True)
    environment_plan = exchange("environments.preview", {})
    host_plan = exchange("preview", {})
    print("Environments: " + ", ".join(t["name"] for t in environment_plan["targets"]))
    if host_plan["excluded_environments"]:
        print("A atualização completa requer incluir estes Environments na política: " + ", ".join(host_plan["excluded_environments"]))
        return 2
    blockers = list(dict.fromkeys(environment_plan["blockers"] + host_plan["blockers"]))
    if blockers:
        explain_blockers(blockers)
        return 2
    print("Cada sistema terá uma cópia de segurança. A etapa final fecha o Hub para atualizar o Host e alinhar os drivers.")
    print("O reinício fica à tua decisão. Aplicações com atualizador próprio são atualizadas nesse programa.")
    if not authorize_update():
        return 1
    code = environments_ui()
    if code:
        return code
    # Revalidate after application updates; never reuse a stale approval digest.
    plan = exchange("preview", {})
    if plan["blockers"] or plan["excluded_environments"]:
        explain_blockers(plan["blockers"])
        print("A etapa do Host ficou pendente: o plano mudou. Abre Atualizar para verificar.")
        return 2
    result = exchange("apply", {"plan_digest": plan["plan_digest"], "confirmation": "CONFIRMAR"})
    print(result["message"], flush=True)
    print("A atualização completa ainda está em curso no Host. O resultado ficará disponível ao voltar ao Hub.", flush=True)
    return 0


def environments_ui() -> int:
    current = exchange("environments.status", {})
    if current.get("state") not in ("queued", "running", "awaiting-hub"):
        plan = exchange("environments.preview", {})
        print("\nAtualizar todos os Environments: " + ", ".join(item["name"] for item in plan["targets"]), flush=True)
        if plan["blockers"]:
            explain_blockers(plan["blockers"]); return 2
        print("Serão atualizados o sistema, as aplicações AUR e os Flatpaks de cada Environment.")
        print("Os outros Environments são atualizados primeiro; o Hub fica para o fim.")
        print("Cada Environment terá uma cópia de segurança. Depois segue a etapa do Host.")
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
    result = subprocess.run(["/home/apx/.local/bin/apx-environment-update-v1", "--unattended"])
    if result.returncode:
        print("O Hub não terminou a atualização. Abre Atualizar para retomar."); return result.returncode
    final = exchange("environments.finish", {"operation": operation_id})
    print(final["message"], flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("mode", choices=("preview", "status", "include", "exclude", "ui", "environments-ui")); parser.add_argument("environment", nargs="?")
    args = parser.parse_args()
    if args.mode == "environments-ui":
        try: return full_ui()
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
