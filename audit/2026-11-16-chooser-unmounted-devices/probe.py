import gi,time,json
from pathlib import Path
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

def walk(w):
 yield w
 if isinstance(w,Gtk.Container):
  for c in w.get_children(): yield from walk(c)
def settle():
 end=time.monotonic()+1
 while time.monotonic()<end:
  while Gtk.events_pending():Gtk.main_iteration_do(False)
  time.sleep(.01)
for action in (Gtk.FileChooserAction.OPEN,Gtk.FileChooserAction.SAVE):
 w=Gtk.FileChooserDialog(title='APX devices check',action=action)
 w.add_button('Cancelar',Gtk.ResponseType.CANCEL);w.add_button('Abrir' if action==Gtk.FileChooserAction.OPEN else 'Salvar',Gtk.ResponseType.OK)
 w.show();settle()
 for row in walk(w):
  if row.find_property('uri'):
   print(json.dumps({'action':int(action),'label':row.get_property('label'),'uri':row.get_property('uri'),'section':row.get_property('section-type'),'place':row.get_property('place-type'),'visible':row.get_visible(),'child_visible':row.get_child_visible(),'header':row.get_header().get_text() if isinstance(row.get_header(),Gtk.Label) else None},ensure_ascii=False),flush=True)

 devices=[r for r in walk(w) if r.find_property('uri') and r.get_property('section-type')==2 and r.get_property('place-type')==3]
 assert len(devices)==1
 assert devices[0].get_child_visible() and devices[0].get_header().get_text()=='Dispositivos'
 assert w.get_widget_for_response(Gtk.ResponseType.OK) is not None
 w.destroy();settle()
