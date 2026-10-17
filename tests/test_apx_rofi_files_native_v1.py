"""Build and exercise the real Rofi mode; needs installed native build headers."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ['rofi', 'gio-2.0', 'gmodule-2.0', 'json-glib-1.0', 'cairo']


class NativeFilesModeTests(unittest.TestCase):
    def test_delayed_directory_does_not_block_and_stale_results_are_cancelled(self):
        if not shutil.which('gcc') or not shutil.which('pkg-config'):
            self.skipTest('native mode requires gcc and pkg-config')
        check = subprocess.run(['pkg-config', '--exists', *PACKAGES])
        if check.returncode:
            self.skipTest('native mode requires Rofi/GLib/JSON/Cairo headers')
        with tempfile.TemporaryDirectory(prefix='apx-rofi-native-') as tmp:
            base = Path(tmp)
            helper = base / 'helper'
            helper.write_text('''#!/usr/bin/python3
import json,os,sys,time
p=sys.argv[2]
time.sleep(.65)
if p.endswith('/Fail'):
    print('invalid JSON')
else:
    names=[('Docs','directory'),('Grande.zip','file')] if p==os.path.expanduser('~') else [('child.txt','file')]
    print(json.dumps({'directory':p,'entries':[{'path':p+'/'+n,'label':n,'icon':'folder' if k=='directory' else 'text-x-generic','kind':k,'search':n} for n,k in names]}))
''')
            helper.chmod(0o755)
            flags = subprocess.check_output(['pkg-config', '--cflags', '--libs', *PACKAGES], text=True).split()
            binary = base / 'harness'
            subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', f'-DAPX_FILES_HELPER="{helper}"', str(ROOT / 'tests/apx_rofi_files_mode_harness.c'), '-o', str(binary), *flags], check=True)
            result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('PASS:', result.stdout)
            print(result.stdout.strip())


if __name__ == '__main__':
    unittest.main()
