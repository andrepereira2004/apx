"""Disposable regular-file GPT repair experiment for native Windows v3.

Block devices are rejected. This is not a physical recovery executor.
"""
import json
import os
from pathlib import Path
import re
import stat
import subprocess

from apx_native_instances_v3 import canonical_layout, validate_plan
from apx_native_offline_v3 import partition_script


def repair_regular_file(disk: Path, plan, action, assessment):
    plan = validate_plan(plan)
    if action not in {'relocate', 'rollback'}:
        raise ValueError('unknown repair action')
    if assessment.get('profile') != 'apx-native-recovery-assessment-v3' or \
            assessment.get('decision') != 'manual-gpt-repair-review' or \
            assessment.get('generation') != plan['new']['generation'] or \
            assessment.get('action') != action or \
            assessment.get('layout') not in {'unreadable', 'other'} or \
            not assessment.get('copy_marker_matches') or \
            not assessment.get('destination_matches_image'):
        raise ValueError('verified recovery assessment required')
    info = disk.lstat()
    if not stat.S_ISREG(info.st_mode) or disk.is_symlink():
        raise ValueError('laboratory GPT repair accepts regular files only')
    target = plan['after'] if action == 'relocate' else plan['before']
    if target['sectorsize'] != 512 or info.st_size != (target['lastlba'] + 34) * 512:
        raise ValueError('laboratory disk geometry differs')
    script = partition_script(target)
    result = subprocess.run(['/usr/bin/sfdisk', '--force', '--no-reread', '--wipe', 'never',
                             '--wipe-partitions', 'never', str(disk)], input=script, text=True,
                            capture_output=True, timeout=30)
    if result.returncode:
        raise ValueError('laboratory GPT repair failed: ' + result.stderr[-300:])
    fd = os.open(disk, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    observed = json.loads(subprocess.run(['/usr/bin/sfdisk', '--json', str(disk)], check=True,
                                       text=True, capture_output=True, timeout=15).stdout)['partitiontable']
    observed['device'] = target['device']
    for part in observed['partitions']:
        number = re.fullmatch(re.escape(str(disk)) + r'([1-7])', part['node'])
        if not number:
            raise ValueError('laboratory GPT partition numbering differs')
        part['node'] = target['device'] + 'p' + number.group(1)
    if canonical_layout(observed) != canonical_layout(target):
        raise ValueError('laboratory GPT repair result differs from plan')
    return observed
