from pathlib import Path
import ast,subprocess,tempfile,json
ROOT=Path(__file__).resolve().parents[2]
flags=['-I/var/lib/apx/environments/minecraft/root/usr/include', '-I/usr/include/glib-2.0','-I/usr/lib/glib-2.0/include','-I/usr/include/json-glib-1.0','-I/usr/include/cairo','-lgio-2.0','-lgobject-2.0','-lglib-2.0','-ljson-glib-1.0','-lgmodule-2.0','-lcairo']
with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
 helper=Path(tmp).resolve()/'helper'
 tree=ast.parse((ROOT/'tests/test_apx_rofi_files_native_v1.py').read_text())
 fixture=next(x.value for x in ast.walk(tree) if isinstance(x,ast.Constant) and isinstance(x.value,str) and x.value.startswith('#!/usr/bin/python3'))
 helper.write_text(fixture);helper.chmod(0o755)
 binary=helper.parent/'harness'
 subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',f'-DAPX_FILES_HELPER="{helper}"',str(ROOT/'tests/apx_rofi_files_mode_harness.c'),'-o',str(binary)]+flags,check=True)
 r=subprocess.run([str(binary)],capture_output=True,text=True,timeout=25)
 Path(__file__).with_name('results.log').write_text(r.stdout+r.stderr)
 print(r.stdout+r.stderr);assert r.returncode==0
subprocess.run(['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror',str(ROOT/'scripts/physical-pilot/apx-rofi-files-mode-v1.c'),'-o',str(Path(__file__).with_name('files-candidate.so'))]+flags,check=True)
