import gi,time,uuid
from pathlib import Path
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
root=Path('/media/apx-usb/USB-4079-3F8D')
assert root.is_mount()
fixture=root/('.apx-access-test-'+uuid.uuid4().hex+'.txt')
fixture.write_text('APX USB file access validation\n')

def settle():
 end=time.monotonic()+.8
 while time.monotonic()<end:
  while Gtk.events_pending():Gtk.main_iteration_do(False)
  time.sleep(.01)
def walk(w):
 yield w
 if isinstance(w,Gtk.Container):
  for c in w.get_children(): yield from walk(c)
try:
 assert fixture.read_text()=='APX USB file access validation\n'
 for action in (Gtk.FileChooserAction.OPEN,Gtk.FileChooserAction.SAVE):
  w=Gtk.FileChooserDialog(title='APX USB access validation',action=action)
  w.add_button('Cancelar',Gtk.ResponseType.CANCEL)
  w.add_button('Abrir' if action==Gtk.FileChooserAction.OPEN else 'Salvar',Gtk.ResponseType.OK)
  w.show();settle()
  rows=[r for r in walk(w) if r.find_property('uri')]
  visible=[r for r in rows if r.get_visible() and r.get_child_visible() and (str(r.get_property('uri')).startswith('file:///media/apx-usb/') or r.get_property('section-type')==2)]
  print('visible devices',[(r.get_property('label'),r.get_property('uri')) for r in visible],flush=True)
  assert len(visible)==1
  row=visible[0];assert row.get_property('uri')==root.as_uri()
  assert row.get_header().get_text()=='Dispositivos'
  row.emit('activate');settle()
  assert w.get_current_folder()==str(root),w.get_current_folder()
  if action==Gtk.FileChooserAction.OPEN:
   w.set_show_hidden(True);w.select_filename(str(fixture));settle()
   assert w.get_filename()==str(fixture)
  else:
   w.set_current_name('apx-check-save.txt');settle()
   assert w.get_filename()==str(root/'apx-check-save.txt')
  assert w.get_widget_for_response(Gtk.ResponseType.OK).get_sensitive()
  print('PASS:',int(action),'sidebar click navigates to USB, file selection/save target accepted',flush=True)
  w.destroy();settle()
finally:
 fixture.unlink(missing_ok=True)
 print('PASS: temporary USB read/write fixture removed',flush=True)
