"""Read-only classification of an interrupted native Windows v3 migration.

This produces evidence for a reviewed recovery plan. It never authorizes a
partition write or assumes that a matching GPT alone proves data integrity.
"""
import re
import hashlib
import os
import stat
from apx_native_instances_v3 import canonical_layout, validate_plan


def hash_extent(path, start_bytes, length_bytes):
    """Read an exact disk/image extent without mounting or writing it."""
    if type(start_bytes) is not int or type(length_bytes) is not int or start_bytes < 0 or length_bytes <= 0:
        raise ValueError('invalid recovery extent')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        info = os.fstat(fd)
        if not (stat.S_ISREG(info.st_mode) or stat.S_ISBLK(info.st_mode)):
            raise ValueError('recovery source is not a disk or regular image')
        if stat.S_ISREG(info.st_mode) and start_bytes + length_bytes > info.st_size:
            raise ValueError('recovery extent exceeds image')
        digest = hashlib.sha256()
        offset = start_bytes
        remaining = length_bytes
        while remaining:
            data = os.pread(fd, min(8 * 1024**2, remaining), offset)
            if not data:
                raise ValueError('short recovery extent read')
            digest.update(data)
            offset += len(data)
            remaining -= len(data)
        return digest.hexdigest()
    finally:
        os.close(fd)


def assess(plan, manifest, action, observed, *, status=None, copy_marker=None, destination_sha256=None,
           original_destination_sha256=None, original_backup_sha256=None):
    plan = validate_plan(plan)
    if action not in {'relocate', 'rollback'}:
        raise ValueError('unknown native migration action')
    if manifest.get('profile') != 'apx-native-image-backup-v3' or manifest.get('state') != 'verified-images' or manifest.get('plan_sha256') != plan['plan_sha256']:
        raise ValueError('verified image manifest required')
    image = manifest['prepared' if action == 'relocate' else 'original']
    expected_bytes = (plan['after' if action == 'relocate' else 'before']['partitions'][2]['size']
                      * plan['before']['sectorsize'])
    if image.get('bytes') != expected_bytes or not re.fullmatch(r'[0-9a-f]{64}', image.get('sha256', '')):
        raise ValueError('image identity differs from the plan')
    original = manifest['original']
    original_bytes = plan['before']['partitions'][2]['size'] * plan['before']['sectorsize']
    if original.get('file') != 'original.ntfs.raw' or \
            original.get('bytes') != original_bytes or not re.fullmatch(r'[0-9a-f]{64}', original.get('sha256', '')):
        raise ValueError('original backup identity differs from the plan')
    before, after = plan['before'], plan['after']
    starting, resulting = (before, after) if action == 'relocate' else (after, before)
    try:
        actual = canonical_layout(observed)
    except (ValueError, KeyError, TypeError, AttributeError):
        layout = 'unreadable'
    else:
        if actual == canonical_layout(starting):
            layout = 'starting'
        elif actual == canonical_layout(resulting):
            layout = 'result'
        else:
            layout = 'other'

    prefix = f"{plan['new']['generation']}:{plan['plan_sha256']}:{action}:"
    expected_marker = prefix + 'copy-verified:verify-windows'
    expected_complete = prefix + 'complete:write-gpt'
    marker_matches = copy_marker == expected_marker
    destination_matches = destination_sha256 == image['sha256']
    if layout == 'result' and status == expected_complete and marker_matches and destination_matches:
        decision = 'ready-for-finalizer-review'
    elif layout in {'unreadable', 'other'} and marker_matches and destination_matches:
        decision = 'manual-gpt-repair-review'
    elif action == 'relocate' and layout == 'starting' and isinstance(status, str) and status.startswith(prefix) and \
            original_backup_sha256 == original['sha256'] and \
            original_destination_sha256 is not None and original_destination_sha256 != original['sha256']:
        decision = 'manual-original-restore-review'
    elif layout in {'starting', 'result'} and marker_matches and destination_matches:
        decision = 'manual-recovery-review'
    else:
        decision = 'stop-no-write'
    return {'schema': 3, 'profile': 'apx-native-recovery-assessment-v3',
            'generation': plan['new']['generation'], 'action': action,
            'layout': layout, 'copy_marker_matches': marker_matches,
            'destination_matches_image': destination_matches,
            'original_backup_matches_image': original_backup_sha256 == original['sha256'],
            'original_destination_matches_image': original_destination_sha256 == original['sha256'],
            'status_matches_complete': status == expected_complete,
            'decision': decision}
