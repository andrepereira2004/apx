import gi, time, tempfile
from pathlib import Path
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

def settle(t=.4):
 end=time.monotonic()+t
 while time.monotonic()<end:
  while Gtk.events_pending():Gtk.main_iteration_do(False)
  time.sleep(.003)
def walk(w):
 yield w
 if isinstance(w,Gtk.Container):
  for c in w.get_children():yield from walk(c)
def has(w,c):return w.get_style_context().has_class(c)
with tempfile.TemporaryDirectory(prefix='apx-portal-check-') as tmp:
 root=Path(tmp);(root/'image.png').write_bytes(b'test')
 for action,title in ((Gtk.FileChooserAction.OPEN,'Open'),(Gtk.FileChooserAction.SAVE,'Save')):
  w=Gtk.FileChooserDialog(title=title,action=action)
  w.add_buttons('_Cancel',Gtk.ResponseType.CANCEL,'_Open' if action==Gtk.FileChooserAction.OPEN else '_Save',Gtk.ResponseType.ACCEPT)
  w.set_current_folder(str(root))
  if action==Gtk.FileChooserAction.SAVE:w.set_current_name('new-image.png')
  w.show();settle()
  header=w.get_header_bar();actions=next(x for x in walk(header) if has(x,'apx-chooser-actions'))
  buttons=actions.get_children();assert len(buttons)==3
  assert w.get_response_for_widget(buttons[1])==Gtk.ResponseType.CANCEL
  assert w.get_response_for_widget(buttons[2])==Gtk.ResponseType.ACCEPT
  assert any(has(x,'apx-header-path') for x in walk(header))
  if action==Gtk.FileChooserAction.SAVE:
   assert buttons[1].get_label()=='Cancelar' and buttons[2].get_label()=='Salvar'
   assert any(isinstance(x,Gtk.Label) and x.get_text()=='Nome' and x.get_mapped() for x in walk(w))
   entries=[x for x in walk(w) if isinstance(x,Gtk.Entry) and x.get_text()=='new-image.png']
   assert len(entries)==1 and entries[0].get_mapped()
   assert w.get_filename()==str(root/'new-image.png'),w.get_filename()
  else:
   w.select_filename(str(root/'image.png'));settle()
   assert w.get_filename()==str(root/'image.png'),w.get_filename()
  search=buttons[0];search.set_active(True);settle(.25)
  assert not search.get_visible()
  search.set_active(False);settle(.25);assert search.get_visible()
  print('PASS:',title,'actions, file path, search and filename entry')
  w.destroy();settle(.05)
