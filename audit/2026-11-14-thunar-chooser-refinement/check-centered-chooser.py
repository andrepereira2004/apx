import gi,time,tempfile,os
from pathlib import Path
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib,Gdk

def settle(seconds=.3):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  while Gtk.events_pending():Gtk.main_iteration_do(False)
  time.sleep(.005)
def walk(x):
 yield x
 if isinstance(x,Gtk.Container):
  for c in x.get_children():yield from walk(c)
def has_class(w,c):return w.get_style_context().has_class(c)
fixture=tempfile.TemporaryDirectory(prefix='apx-navigation-check-')
root=Path(fixture.name)
for n in ['a','b','c','branch']:(root/n).mkdir()
(root/'c'/'needle.txt').write_text('match');(root/'c'/'other.txt').write_text('other')
w=Gtk.FileChooserDialog(title='Wallpaper deste Environment',action=Gtk.FileChooserAction.OPEN)
w.add_buttons('Cancelar',Gtk.ResponseType.CANCEL,'Escolher',Gtk.ResponseType.OK)
w.set_current_folder(str(root/'a'));w.show();settle()
header=w.get_header_bar()
nav=next(x for x in walk(header) if has_class(x,'apx-chooser-navigation'))
back,forward=nav.get_children()[:2]
def state(folder,b,f):
 assert w.get_current_folder()==str(root/folder),(w.get_current_folder(),folder)
 assert (back.get_sensitive(),forward.get_sensitive())==(b,f),(back.get_sensitive(),forward.get_sensitive(),folder)
state('a',False,False)
initial_search=next(x for x in walk(header) if isinstance(x,Gtk.ToggleButton))
initial_entry=next(x for x in walk(header) if isinstance(x,Gtk.SearchEntry))
assert not initial_search.get_active() and initial_search.get_visible()
assert not initial_entry.get_mapped()
assert next(x for x in walk(header) if isinstance(x,Gtk.Stack)).get_visible_child_name()=='path'
print('PASS: fresh dialog starts with breadcrumbs and visible magnifier, search closed.')
for folder in ['b','c']:w.set_current_folder(str(root/folder));settle()
state('c',True,False)
back.clicked();back.clicked();settle();state('a',False,True)
forward.clicked();forward.clicked();settle();state('c',True,False)
back.clicked();settle();state('b',True,True)
w.set_current_folder(str(root/'branch'));settle();state('branch',True,False)
# A keyboard event follows the same history and boundaries.
event=Gdk.Event.new(Gdk.EventType.KEY_PRESS);event.keyval=Gdk.KEY_Left;event.state=Gdk.ModifierType.MOD1_MASK
w.emit('key-press-event',event);settle();state('b',True,True)
w.set_current_folder(str(root/'c'));settle()
search=next(x for x in walk(header) if isinstance(x,Gtk.ToggleButton))
entry=next(x for x in walk(header) if isinstance(x,Gtk.SearchEntry))
search.set_active(True);settle()
assert entry.get_mapped()
assert not search.get_visible()
assert entry.get_ancestor(Gtk.HeaderBar)==header
assert not any(x.get_visible() for x in walk(w) if x.get_name()=='pathbarbox' and x.get_parent().get_visible())
entry.set_text('needle');settle(1.5)
views=[x for x in walk(w) if isinstance(x,Gtk.TreeView) and x.get_mapped()]
rows=[]
for view in views:
 m=view.get_model()
 if m:
  i=m.get_iter_first()
  while i:
   rows.append(m.get_value(i,0))
   for column in view.get_columns():
    if column.get_sort_column_id() not in (1,2,3):continue
    assert column.get_alignment()==0.5
    assert all(cell.get_property('xalign')==0.5 for cell in column.get_cells() if isinstance(cell,Gtk.CellRendererText))
    if column.get_sort_column_id()==1:continue
    column.cell_set_cell_data(m,i,False,False)
    values=[c.get_property('text') for c in column.get_cells() if isinstance(c,Gtk.CellRendererText)]
    if column.get_sort_column_id()==2:assert values==['.txt'],values
    else:assert len(values[0])==10 and values[0][2]=='/' and values[0][5]=='/',values
   i=m.iter_next(i)
assert 'needle.txt' in rows and 'other.txt' not in rows,rows
entry.emit('stop-search');settle();assert not search.get_active() and not entry.get_mapped()
assert search.get_visible()
assert not [x.__gtype__.name for x in walk(w) if x.get_mapped() and x.get_has_tooltip()]
# Later tooltip updates must remain disabled.
back.set_tooltip_text('Voltar');assert not back.get_has_tooltip()
print('PASS: initial/end states, rapid back/forward, history branching, Alt+Left, inline native search/results, close and tooltip suppression.')
w.destroy();settle(.05);fixture.cleanup()
