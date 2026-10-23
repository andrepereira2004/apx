#!/usr/bin/env python3
"""Portable headless admission wrapper; share the current lifecycle unchanged."""
import importlib.util
from pathlib import Path
import sys

directory = Path(__file__).resolve().parent
sys.path.insert(0, str(directory))
spec = importlib.util.spec_from_file_location('apx_current_runtime', directory / 'apx-lab-runtime-core.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.ROLES = {'hub', 'development', 'minimal'}
# Do not silently admit hardware-bound graphical roles on a generic machine.
if __name__ == '__main__':
    try:
        raise SystemExit(runtime.main())
    except (runtime.Refusal, runtime.subprocess.CalledProcessError) as error:
        print(f'APX refused: {error}', file=sys.stderr)
        raise SystemExit(2)
else:
    # The existing authenticated executor imports this entrypoint.
    globals().update({key: value for key, value in vars(runtime).items() if not key.startswith('__')})
