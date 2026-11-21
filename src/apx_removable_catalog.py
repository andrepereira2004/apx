"""Read public USB bridge identities without exposing Host block devices."""
import json
from pathlib import Path
import re


def read(path=Path('/media/apx-usb/volumes.json')):
    if not path.exists():
        return {}
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16384 or path.stat().st_mode & 0o022:
        raise ValueError('Untrusted USB catalogue')
    values = json.loads(path.read_text())
    if type(values) is not dict or len(values) > 32:
        raise ValueError('Invalid USB catalogue')
    result = {}
    for identity, item in values.items():
        if not re.fullmatch(r'[0-9a-fA-F-]{9,36}', identity) or type(item) is not dict or set(item) != {'name','label'} or item['name'] != 'USB-' + identity or item['label'] != 'USB ' + identity:
            raise ValueError('Invalid USB identity')
        result[identity] = (item['name'], item['label'])
    return result
