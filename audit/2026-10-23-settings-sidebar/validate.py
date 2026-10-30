import json, os, subprocess
from pathlib import Path
prefix=json.loads(Path('audit/2026-10-23-settings-sidebar/session-prefix.json').read_text())
program='''import runpy,json,gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib
m=runpy.run_path('/home/apx/.local/bin/apx-settings',run_name='validation')
w=m['Settings']();w.show_all()
while Gtk.events_pending(): Gtk.main_iteration()
rows=[]
for name,r in w.navigation_rows.items():
 box=r.get_child();im,lab=box.get_children()
 rows.append(dict(name=name,font=lab.get_style_context().get_font(Gtk.StateFlags.NORMAL).to_string(),height=r.get_allocated_height(),icon=im.get_pixel_size(),gicon=im.get_storage_type().value_nick))
assert all(r['icon']==16 and r['height']<=34 for r in rows),rows
# Navigation construction and computed metrics verified without changing preferences.
print(json.dumps(rows));w.destroy()
'''
r=subprocess.run(prefix+['python3','-c',program],capture_output=True,text=True)
Path('audit/2026-10-23-settings-sidebar/validation.json').write_text(r.stdout)
print(r.stdout,r.stderr);r.check_returncode()
