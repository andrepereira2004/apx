from pathlib import Path
import urllib.request,concurrent.futures
repo=Path(__file__).resolve().parents[2];seed=repo/'config/environment-shell-v1';qml=seed/'quickshell/apx'
icons='battery battery-full battery-medium battery-low battery-warning battery-charging monitor pickaxe zap swords hexagon ghost chevron-right chevron-left calendar-days grid-2x2 hard-drive mic mic-off volume-2 volume-x sun keyboard wifi wifi-off wifi-low wifi-high bluetooth bluetooth-off bluetooth-connected lock-keyhole rotate-cw folder power refresh-cw terminal log-out plane calculator camera panels-top-left touchpad touchpad-off circle-alert circle-check shield-check globe search settings mouse headphones usb plus x check'.split()
files={f'quickshell/apx/icons/lucide/{name}.svg':f'https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{name}.svg' for name in icons}
files['quickshell/apx/icons/lucide/LICENSE.txt']='https://raw.githubusercontent.com/lucide-icons/lucide/main/LICENSE'
for name in ['JetBrainsMono-Regular.ttf','JetBrainsMono-Bold.ttf']:
 files['local/share/fonts/jetbrains-mono/'+name]='https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/fonts/ttf/'+name
files['local/share/fonts/jetbrains-mono/OFL.txt']='https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/OFL.txt'
def fetch(item):
 relative,url=item;data=urllib.request.urlopen(url,timeout=30).read();p=seed/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return relative
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for rel in pool.map(fetch,files.items()):print(rel)
