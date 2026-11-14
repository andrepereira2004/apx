import gi,time
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

def settle(t):
 end=time.monotonic()+t
 while time.monotonic()<end:
  while Gtk.events_pending():Gtk.main_iteration_do(False)
  time.sleep(.003)
def walk(w):
 yield w
 if isinstance(w,Gtk.Container):
  for c in w.get_children():yield from walk(c)
w=Gtk.FileChooserDialog(title='Wallpaper deste Environment',action=Gtk.FileChooserAction.OPEN)
w.add_buttons('Cancelar',Gtk.ResponseType.CANCEL,'Escolher',Gtk.ResponseType.OK);w.set_current_folder('/home/apx/Pictures');w.show();settle(.4)
h=w.get_header_bar();stack=next(x for x in walk(h) if isinstance(x,Gtk.Stack));entry=next(x for x in walk(h) if isinstance(x,Gtk.SearchEntry));path=stack.get_child_by_name('path');toggle=next(x for x in walk(h) if isinstance(x,Gtk.ToggleButton))
def pos(x):
 xx,yy=x.translate_coordinates(h,0,0);return yy,x.get_allocated_height()
p0=pos(path);toggle.set_active(True);settle(.25);e=pos(entry);toggle.set_active(False);settle(.05);p1=pos(path);running=stack.get_transition_running();settle(.25);p2=pos(path)
print('path before',p0,'search',e,'path during',p1,'path after',p2,'transition running',running)
assert p0==p1==p2 and running
w.destroy()
