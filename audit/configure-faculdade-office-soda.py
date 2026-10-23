import sys,subprocess,json
from pathlib import Path
sys.path.insert(0,'/home/apx/.cache/apx-office-install')
import wine4office_backend as b
prefix='/home/apx/.wine4office-offline';wine='/home/apx/.local/share/wine4office/soda-test/soda-11.0-29-experimental-x86_64/bin/wine'
root=Path(prefix)/'drive_c/odt'
assert (root/'Office/Data/apx-download-manifest.json').is_file()
config=root/'configuration.xml'
config.write_text(config.read_text().replace('Level="Full"','Level="None"'))
b.ensure_safe_x11_defaults(prefix,wine)
locker=Path(prefix)/'drive_c/ProgramData/Microsoft/Office/ClickToRunPackageLocker'
if locker.is_file() and not locker.is_symlink():locker.chmod(locker.stat().st_mode|0o600)
print('Configuring Office from verified complete Microsoft downloads',flush=True)
try:
 b._stream_command([wine,'C:\\odt\\setup.exe','/configure','C:\\odt\\configuration.xml'],b.wine_environment(prefix,wine),lambda s:print(s,flush=True))
except subprocess.CalledProcessError as error:
 print('Installer exit:',error.returncode,flush=True)
apps=[app for app in ('word','excel','powerpoint','onenote') if b.find_office_app(prefix,app)]
assert all(app in apps for app in ('word','excel','powerpoint')),apps
config_saved=b.load_config();config_saved.update(prefix=prefix,wine=wine,use_x11=True);b.save_config(config_saved)
print('Installed apps:',apps,flush=True)
print(b.create_app_shortcuts(apps,prefix,wine,False),flush=True)
print(json.dumps(b.environment_status(prefix,wine),default=str),flush=True)
