import gi,time,tempfile
from pathlib import Path
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

def settle(t=.5):
 end=time.monotonic()+t
 while time.monotonic()<end:
  while Gtk.events_pending():Gtk.main_iteration_do(False)
  time.sleep(.005)
def walk(w):
 yield w
 if isinstance(w,Gtk.Container):
  for child in w.get_children():yield from walk(child)
with tempfile.TemporaryDirectory(prefix='apx-chooser-response-') as td:
 path=Path(td)/'fixture.mcpack';path.write_bytes(b'fixture')
 w=Gtk.FileChooserDialog(title='APX response check',action=Gtk.FileChooserAction.OPEN,use_header_bar=True)
 w.add_buttons('_Cancelar',Gtk.ResponseType.CANCEL,'_Abrir',Gtk.ResponseType.OK)
 w.set_select_multiple(True);w.set_current_folder(td)
 events=[];w.connect('response',lambda w,r:events.append((r,w.get_filenames())))
 w.set_response_sensitive(Gtk.ResponseType.OK,False);w.show();settle();w.select_filename(str(path));settle()
 buttons=[x for x in walk(w) if isinstance(x,Gtk.Button) and x.get_label()=='_Abrir'];assert len(buttons)==1
 b=buttons[0];print('filename',w.get_filenames(),'response ID',w.get_response_for_widget(b),'sensitive',b.get_sensitive(),'lookup',w.get_widget_for_response(Gtk.ResponseType.OK),flush=True)
 assert b.get_sensitive() and w.get_widget_for_response(Gtk.ResponseType.OK)==b
 b.clicked();settle();print('responses',events,flush=True)
 assert events==[(Gtk.ResponseType.OK,[str(path)])],events
 w.destroy()
print('PASS: Open delivers chosen file through dialog response')

for action,response in ((Gtk.FileChooserAction.OPEN,Gtk.ResponseType.ACCEPT),(Gtk.FileChooserAction.SAVE,Gtk.ResponseType.ACCEPT)):
 with tempfile.TemporaryDirectory(prefix='apx-chooser-save-response-') as td:
  path=Path(td)/'fixture.txt';path.write_text('fixture')
  w=Gtk.FileChooserDialog(title='APX response regression',action=action,use_header_bar=True)
  w.add_buttons('_Cancelar',Gtk.ResponseType.CANCEL,'_Salvar' if action==Gtk.FileChooserAction.SAVE else '_Abrir',response)
  w.set_current_folder(td)
  if action==Gtk.FileChooserAction.SAVE:w.set_current_name('new.txt')
  events=[];w.connect('response',lambda w,r:events.append((r,w.get_filename())))
  w.show();settle()
  if action==Gtk.FileChooserAction.OPEN:w.select_filename(str(path));settle()
  button=w.get_widget_for_response(response);cancel=w.get_widget_for_response(Gtk.ResponseType.CANCEL)
  assert button and cancel and button.get_parent()==w.get_header_bar()
  button.clicked();settle()
  assert events==[(response,str(Path(td)/('new.txt' if action==Gtk.FileChooserAction.SAVE else 'fixture.txt')))],events
  events.clear();cancel.clicked();settle();assert events and events[0][0]==Gtk.ResponseType.CANCEL
  w.destroy()
print('PASS: native single-file Open, Save filename and Cancel responses')
