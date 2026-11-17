import gi,time
from pathlib import Path
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

def settle():
 end=time.monotonic()+.7
 while time.monotonic()<end:
  while Gtk.events_pending():Gtk.main_iteration_do(False)
  time.sleep(.01)
def walk(w):
 yield w
 if isinstance(w,Gtk.Container):
  for c in w.get_children():yield from walk(c)
w=Gtk.FileChooserDialog(title='APX USB validation',action=Gtk.FileChooserAction.OPEN)
w.set_current_folder('/home/apx/Downloads');w.show();settle()
rows=[x for x in walk(w) if x.find_property('uri') and x.get_property('uri')=='file:///media/apx-usb/Ventoy']
assert len(rows)==1,len(rows)
row=rows[0];assert row.get_visible() and row.get_child_visible()
header=row.get_header();assert header and header.get_text()=='Dispositivos'
assert row.get_property('start-icon').get_names()[0]=='drive-removable-media-usb'
row.emit('activate');settle()
assert w.get_current_folder()=='/media/apx-usb/Ventoy',w.get_current_folder()
print('PASS: chooser shows one USB row under Dispositivos, USB icon and navigation work')
w.destroy()
