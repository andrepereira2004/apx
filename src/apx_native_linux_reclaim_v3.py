"""Exact secondary-Windows retirement plan; no disk or credential I/O."""
from copy import deepcopy
from uuid import UUID

from apx_native_instances_v3 import canonical_layout, digest, validate_layout

PROFILE = 'apx-native-linux-reclaim-v3'
LINUX_LUKS = 'ca7d7ccb-63ed-4c53-861c-1742536059cc'
MAPPER = 'cryptreclaimed'


def plan_reclaim(table, marker, retired, original, luks_uuid):
    """Merge only p5/p6/p7; preserve every other partition byte-for-byte."""
    validate_layout(table)
    table = canonical_layout(table)
    if str(UUID(luks_uuid)) != luks_uuid:
        raise ValueError('invalid reclaim LUKS UUID')
    parts = {p['node']: p for p in table['partitions']}
    disk = table['device']
    if disk != '/dev/nvme0n1' or table['sectorsize'] != 512:
        raise ValueError('unsupported reclaim disk')
    selected = [parts[disk+'p'+str(n)] for n in (6, 7, 5)]
    if marker.get('profile') != 'apx-native-free-slot-v3' or marker.get('state') != 'free' \
            or marker.get('layout_sha256') != digest(table):
        raise ValueError('reclaim requires the exact cleared slot')
    if retired.get('state') != 'deleting' or retired.get('name') == 'windows' \
            or retired.get('generation') != marker.get('previous_generation'):
        raise ValueError('retired Windows identity differs')
    for record in (original, retired, marker):
        if record.get('disk_id', '').lower() != table['id'].lower() \
                or record.get('disk_serial') != original.get('disk_serial'):
            raise ValueError('reclaim disk identity differs')
    for key, part in zip(('esp_partuuid', 'msr_partuuid', 'windows_partuuid'), selected):
        if marker.get(key, '').lower() != part['uuid'].lower():
            raise ValueError('cleared slot partition identity differs')
    if retired.get('windows_partuuid', '').lower() != selected[2]['uuid'].lower() \
            or retired.get('esp_partuuid', '').lower() != selected[0]['uuid'].lower() \
            or retired.get('start_sector') != selected[2]['start'] \
            or retired.get('size_sectors') != selected[2]['size']:
        raise ValueError('retired Windows extent differs')
    if any(a['start']+a['size'] != b['start'] for a, b in zip(selected, selected[1:])):
        raise ValueError('cleared slot is not contiguous')
    original_part = parts.get(disk+'p3', {})
    if original.get('name') != 'windows' or original.get('state') != 'ready' \
            or original.get('windows_partuuid', '').lower() != original_part.get('uuid', '').lower() \
            or original.get('start_sector') != original_part.get('start') \
            or original.get('size_sectors') != original_part.get('size'):
        raise ValueError('preserved Windows identity differs')
    after = deepcopy(table)
    after['partitions'] = [p for p in after['partitions'] if p['node'] not in {disk+'p6', disk+'p7'}]
    reclaimed = next(p for p in after['partitions'] if p['node'] == disk+'p5')
    reclaimed.update(start=selected[0]['start'], size=sum(p['size'] for p in selected),
                     type=LINUX_LUKS, name='APX_LINUX_RECLAIMED')
    validate_layout(after)
    plan = dict(schema=3, profile=PROFILE, generation=retired['generation'],
                target=retired['name'], disk_serial=original['disk_serial'], before=table,
                after=canonical_layout(after), reclaimed=reclaimed, luks_uuid=luks_uuid,
                mapper=MAPPER, bytes=reclaimed['size']*512)
    plan['sha256'] = digest(plan)
    return plan


def validate_reclaim(plan):
    if plan.get('schema') != 3 or plan.get('profile') != PROFILE \
            or plan.get('mapper') != MAPPER \
            or plan.get('sha256') != digest({k: v for k, v in plan.items() if k != 'sha256'}):
        raise ValueError('reclaim plan differs')
    before, after = canonical_layout(plan['before']), canonical_layout(plan['after'])
    validate_layout(before); validate_layout(after)
    old = {p['node']: p for p in before['partitions']}
    new = {p['node']: p for p in after['partitions']}
    disk = '/dev/nvme0n1'
    if before['device'] != disk or after['device'] != disk \
            or {k: v for k, v in before.items() if k != 'partitions'} != \
               {k: v for k, v in after.items() if k != 'partitions'} \
            or set(new) != set(old)-{disk+'p6', disk+'p7'}:
        raise ValueError('reclaim disk layout differs')
    for node in set(new)-{disk+'p5'}:
        if new[node] != old[node]:
            raise ValueError('protected partition changed')
    selected = [old[disk+'p'+str(n)] for n in (6, 7, 5)]
    expected = dict(old[disk+'p5'], start=selected[0]['start'],
                    size=sum(p['size'] for p in selected), type=LINUX_LUKS,
                    name='APX_LINUX_RECLAIMED')
    if any(a['start']+a['size'] != b['start'] for a, b in zip(selected, selected[1:])) \
            or new[disk+'p5'] != expected or plan['reclaimed'] != expected \
            or plan['bytes'] != expected['size']*before['sectorsize'] \
            or str(UUID(plan['luks_uuid'])) != plan['luks_uuid']:
        raise ValueError('reclaim extent differs')
    return plan


def kernel_cmdline(text, luks_uuid):
    """Keep all existing boot options, adding an explicit secondary dependency."""
    tokens = text.strip().split()
    if any(t.startswith('rd.luks.name='+luks_uuid+'=') for t in tokens):
        raise ValueError('reclaim command line is already configured')
    flags = next((i for i, t in enumerate(tokens) if t.startswith('rootflags=')), None)
    if flags is None:
        raise ValueError('missing root subvolume options')
    tokens[flags] += ',device=/dev/mapper/'+MAPPER
    tokens += ['rd.luks.name='+luks_uuid+'='+MAPPER]
    return ' '.join(tokens)+'\n'


def crypttab(text, root_uuid, luks_uuid):
    lines = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith('#')]
    if lines:
        raise ValueError('existing initramfs crypttab needs review')
    return (f'cryptroot UUID={root_uuid} none luks,x-initrd.attach\n'
            f'{MAPPER} UUID={luks_uuid} none luks,x-initrd.attach\n')


SYSROOT_DEPENDENCY = ('[Unit]\nRequires=systemd-cryptsetup@cryptreclaimed.service\n'
                      'After=systemd-cryptsetup@cryptreclaimed.service\n')


def validate_storage_health(stats, proof, filesystem_uuid, now):
    """Accept historical corruption only with fresh, exact, clean scrub evidence.

    Never reset persistent counters or accept new errors relative to evidence.
    """
    fields = {'write_io_errs','read_io_errs','flush_io_errs','corruption_errs','generation_errs'}
    observed = {}
    for device in stats['device-stats']:
        values = {key:device[key] for key in fields}
        if any(type(value) is not int or value < 0 for value in values.values()):
            raise ValueError('Contadores de armazenamento inválidos.')
        if any(values[key] for key in fields-{'corruption_errs'}):
            raise ValueError('O Btrfs regista erros de I/O ou de geração. A integração foi bloqueada.')
        if any(values.values()):
            observed[device['device']] = values
    if not observed:
        return
    if not proof or proof.get('profile') != 'apx-clean-readonly-scrub-v3' \
            or proof.get('filesystem_uuid') != filesystem_uuid \
            or proof.get('clean_readonly_scrub') is not True \
            or not 0 <= now-proof.get('verified_at', 0) <= 24*3600 \
            or proof.get('historical_counters') != observed:
        raise ValueError('O Btrfs tem contadores históricos. É necessária uma verificação de leitura recente e sem erros antes de integrar o espaço.')
