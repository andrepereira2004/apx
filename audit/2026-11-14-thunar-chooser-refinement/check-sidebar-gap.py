import gi,time
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
w=Gtk.FileChooserDialog(title='Wallpaper deste Environment',action=Gtk.FileChooserAction.OPEN)
w.add_buttons('Cancelar',Gtk.ResponseType.CANCEL,'Escolher',Gtk.ResponseType.OK)
w.set_current_folder('/home/apx/Pictures');w.show()
def walk(x):
 yield x
 if isinstance(x,Gtk.Container):
  for c in x.get_children():yield from walk(c)
end=time.monotonic()+.4
while time.monotonic()<end:
 while Gtk.events_pending():Gtk.main_iteration_do(False)
 time.sleep(.005)
for x in walk(w):
 if isinstance(x,Gtk.ListBoxRow) and x.get_mapped():
  a=x.get_allocation();ctx=x.get_style_context();state=x.get_state_flags();p=ctx.get_padding(state);b=ctx.get_border(state);m=ctx.get_margin(state)
  labels=[y.get_text() for y in walk(x) if isinstance(y,Gtk.Label)]
  print(labels,(a.y,a.height),'margin',m.top,m.bottom,'border',b.top,b.bottom,'padding',p.top,p.bottom,'widget-margin',x.get_margin_top(),x.get_margin_bottom())
w.destroy()
