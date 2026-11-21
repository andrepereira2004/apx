#!/usr/bin/env python3
"""Read-only release audit for use after every shared APX control deployment."""
import importlib.util
import json
from pathlib import Path

path = Path('/usr/lib/apx/apx_native_hub_v3.py')
spec = importlib.util.spec_from_file_location('apx_native_release_audit', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
errors = module.release_errors()
print(json.dumps({'enabled': not errors, 'validation_errors': errors}, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
