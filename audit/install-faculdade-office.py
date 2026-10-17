import sys
sys.path.insert(0,'/home/apx/.cache/apx-office-install')
import wine4office_backend as b
from pathlib import Path
prefix='/home/apx/.wine4office'
wine='/home/apx/.local/share/wine4office/runner/bin/wine'
out=lambda s: print(s,flush=True)
if b.classify_prefix(prefix)!='valid':out(b.create_environment(prefix,wine,False,out))
xml=b.build_office_configuration('O365ProPlusRetail',['pt-pt','en-us']).replace('Channel="Current"','Channel="Current" Version="16.0.20326.20144"').replace('<Display Level="Full" />','<Display Level="Full" AcceptEULA="TRUE" />').replace('    </Product>','      <ExcludeApp ID="Outlook" />\n      <ExcludeApp ID="Access" />\n      <ExcludeApp ID="Publisher" />\n      <ExcludeApp ID="Teams" />\n      <ExcludeApp ID="OneDrive" />\n      <ExcludeApp ID="Lync" />\n    </Product>')
config=Path('/home/apx/.cache/apx-office-install/configuration.xml');config.write_text(xml)
out(b.install_office_with_odt(prefix,wine,config,out))
out(b.create_app_shortcuts(['word','excel','powerpoint','onenote'],prefix,wine))
