#!/usr/bin/env python3
"""Read-only physical-pilot capacity preview used by the authenticated Hub."""
import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import uuid

sys.path.insert(0, "/usr/lib/apx")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from apx_native_instances_v3 import plan_second_windows, plan_slot_reuse


def read_command(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=15,
                          env={"PATH": "/usr/bin", "LC_ALL": "C"}).stdout


def trusted_json(path):
    info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid!=0 or info.st_gid!=0 or \
            stat.S_IMODE(info.st_mode) not in {0o400,0o600} or info.st_size>32768:
        raise ValueError('O registo Windows não é confiável.')
    return json.loads(path.read_bytes())


def preview(target, description, size_gib, *, generation=None):
    if not re.fullmatch(r"[a-z](?:[a-z0-9]|-(?=[a-z0-9])){0,26}", target) or target in {"hub", "windows"}:
        raise ValueError("Escolhe um nome diferente para o novo Windows.")
    if len(description) > 120 or description != description.strip() or any(ord(c) < 32 for c in description):
        raise ValueError("Descrição inválida.")
    if size_gib not in {80, 120, 160}:
        raise ValueError("Tamanho Windows inválido.")
    if Path("/var/lib/apx/environments", target).exists() or Path("/var/lib/apx/native-environments", target + ".json").exists():
        raise ValueError("Já existe um Environment com esse nome.")
    if Path("/var/lib/apx/native-environments/windows-pending.json").exists():
        raise ValueError("Conclui a operação Windows pendente antes de preparar outra.")
    if Path("/var/lib/apx/native-environments/pending-v3.json").exists():
        raise ValueError("Conclui a operação Windows pendente antes de preparar outra.")
    if Path("/etc/hostname").read_text().strip() != "apx-host" or Path("/sys/class/dmi/id/product_name").read_text().strip() != "82JU":
        raise ValueError("Este plano pertence ao computador APX de teste.")
    metadata = Path("/var/lib/apx/native-environments/windows.json")
    info = metadata.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or stat.S_IMODE(info.st_mode) != 0o400 or info.st_size > 4096:
        raise ValueError("O registo Windows não é confiável.")
    legacy = json.loads(metadata.read_bytes())
    serial = Path("/sys/class/block/nvme0n1/device/serial").read_text().strip()
    if serial != "S4DYNX0R253702" or legacy["disk_serial"] != serial:
        raise ValueError("O SSD selecionado mudou.")
    table = json.loads(read_command("/usr/bin/sfdisk", "--json", "/dev/nvme0n1"))["partitiontable"]
    slot_path=Path('/var/lib/apx/native-environments/free-slot-v3.json')
    if slot_path.exists() or len(table['partitions'])==7:
        if not slot_path.exists():raise ValueError('O espaço Windows existente precisa de recuperação antes de nova instalação.')
        slot=trusted_json(slot_path)
        if not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',slot.get('source_generation','')):
            raise ValueError('A origem do espaço Windows difere.')
        source=trusted_json(Path('/var/lib/apx/native-environments/migrations-v3')/slot['source_generation']/'plan.json')
        registry=Path('/var/lib/apx/native-environments/instances-v3')
        registry_info=registry.lstat()
        if not stat.S_ISDIR(registry_info.st_mode) or registry_info.st_uid!=0 or \
                registry_info.st_gid!=0 or stat.S_IMODE(registry_info.st_mode)!=0o700:
            raise ValueError('O catálogo Windows não é confiável.')
        if sorted(p.name for p in registry.glob('*.json'))!=['windows.json']:
            raise ValueError('Existe outra instalação Windows ativa neste espaço.')
        original=trusted_json(registry/'windows.json')
        expected_size=slot['size_sectors']*table['sectorsize']//1024**3
        if size_gib!=expected_size:
            raise ValueError('O espaço Windows reutilizável tem '+str(expected_size)+' GiB; escolhe esse tamanho.')
        plan=plan_slot_reuse(source,slot,table,[original],new_name=target,
                             new_generation=generation or str(uuid.uuid4()))
        return {'schema':3,'profile':'apx-native-creation-preview-v3','target':target,
                'description':description,'size_gib':size_gib,'can_create':False,
                'existing_windows_gib':plan['existing']['size_gib'],
                'apx_gib':round(source['apx_payload_bytes']/1024**3,1),
                'message':'O espaço de 80 GiB está reservado para outro Windows. A instalação de substituição ainda está em validação; esta verificação não altera o disco.',
                'plan':plan}
    ntfs = read_command("/usr/bin/ntfsresize", "--info", "--no-action", "/dev/nvme0n1p3")
    minimum = re.search(r"You might resize at (\d+) bytes", ntfs)
    if minimum is None:
        raise ValueError("Não foi possível medir o espaço do Windows atual.")
    luks = json.loads(read_command("/usr/bin/cryptsetup", "luksDump", "--disable-locks", "--dump-json-metadata", "/dev/nvme0n1p2"))
    segments = luks["segments"]
    if set(segments) != {"0"} or segments["0"]["type"] != "crypt":
        raise ValueError("A configuração do armazenamento APX mudou.")
    usage = os.statvfs("/")
    used = (usage.f_blocks - usage.f_bfree) * usage.f_frsize
    try:
        plan = plan_second_windows(table, legacy, new_name=target, new_generation=generation or str(uuid.uuid4()),
                                   new_gib=size_gib, ntfs_min_bytes=int(minimum.group(1)),
                                   apx_used_bytes=used, luks_header_bytes=int(segments["0"]["offset"]),
                                   measured_backup_required=True)
    except ValueError as error:
        if "capacity" in str(error):
            raise ValueError("Esse tamanho não cabe neste SSD mantendo o Windows atual e a reserva APX. Experimenta 80 GiB.") from error
        if "backup budget" in str(error):
            raise ValueError("É necessário libertar espaço no APX para guardar uma cópia do Windows antes da migração.") from error
        raise
    # This endpoint cannot start any storage/firmware action. The full offline
    # executor must be reviewed and tested before a confirm operation is added.
    return {"schema": 3, "profile": "apx-native-creation-preview-v3", "target": target,
            "description": description, "size_gib": size_gib, "can_create": False,
            "existing_windows_gib": plan["existing"]["size_gib"],
            "apx_gib": round(plan["apx_payload_bytes"] / 1024**3, 1),
            "message": "As partições cabem neste SSD. Antes da migração, o APX terá de medir e confirmar o espaço realmente ocupado pela cópia do Windows atual. Esta verificação não altera o disco.",
            "plan": plan}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--description", default="")
    parser.add_argument("--size-gib", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(preview(args.target, args.description, args.size_gib), ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
