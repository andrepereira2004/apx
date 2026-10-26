import json,subprocess
from pathlib import Path
prefix=json.loads(Path('audit/2026-10-23-settings-sidebar/session-prefix.json').read_text())
base="""import gi,runpy,json
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
"""
variants={
'settings':"w=runpy.run_path('/home/apx/.local/bin/apx-settings',run_name='check')['Settings']();h=w.get_titlebar()",
 'tasks':"app=Gtk.Application(application_id='org.apx.HeaderCheck');app.register(None);w=runpy.run_path('/home/apx/.local/bin/apx-task-manager',run_name='check')['Manager'](app);h=w.get_titlebar()",
 'files':"""w=Gtk.Window();w.get_style_context().add_class('thunar');h=Gtk.HeaderBar(show_close_button=True);h.set_has_subtitle(False);h.get_style_context().add_class('apx-files-header');l=Gtk.Label(label='Gestor de Ficheiros');l.get_style_context().add_class('title');h.set_custom_title(l);w.set_titlebar(h)"""}
results={}
for name,create in variants.items():
 code=base+create+"""
w.show_all()
while Gtk.events_pending():Gtk.main_iteration()
c=h.get_style_context();s=Gtk.StateFlags.NORMAL
print(json.dumps(dict(height=h.get_allocated_height(),minimum=h.get_preferred_height().minimum_height,padding=[c.get_padding(s).top,c.get_padding(s).bottom],border=[c.get_border(s).top,c.get_border(s).bottom],font=c.get_font(s).to_string())))
w.destroy()
"""
 r=subprocess.run(prefix+['python3','-c',code],capture_output=True,text=True);r.check_returncode();results[name]=json.loads(r.stdout)
assert len({v['height'] for v in results.values()}) == 1,results
Path('audit/2026-10-23-header-alignment/measurements.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
