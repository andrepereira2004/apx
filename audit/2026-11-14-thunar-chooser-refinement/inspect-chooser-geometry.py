import gi,time
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,Pango
w=Gtk.FileChooserDialog(title='Wallpaper deste Environment',action=Gtk.FileChooserAction.OPEN)
w.add_buttons('Cancelar',Gtk.ResponseType.CANCEL,'Escolher',Gtk.ResponseType.OK)
w.set_current_folder('/home/apx/Documents');w.show()
def walk(x):
 yield x
 if isinstance(x,Gtk.Container):
  for c in x.get_children():yield from walk(c)
end=time.monotonic()+.6
while time.monotonic()<end:
 while Gtk.events_pending():Gtk.main_iteration_do(False)
 time.sleep(.005)
for x in walk(w):
 if not x.get_mapped():continue
 if isinstance(x,(Gtk.Button,Gtk.ScrolledWindow,Gtk.TreeView,Gtk.Paned,Gtk.Stack)):
  a=x.get_allocation();ctx=x.get_style_context();p=ctx.get_padding(x.get_state_flags());b=ctx.get_border(x.get_state_flags())
  print(x.__gtype__.name,x.get_name(),ctx.list_classes(),(a.x,a.y,a.width,a.height),'margin',x.get_margin_start(),'padding',p.left,p.right,p.top,p.bottom,'border',b.left,b.right,'cssmargin',ctx.get_margin(x.get_state_flags()).top,ctx.get_margin(x.get_state_flags()).bottom)
  if isinstance(x,Gtk.ScrolledWindow):
   h=x.get_hadjustment();print('HADJ',h.get_value(),h.get_lower(),h.get_upper(),h.get_page_size())
  if isinstance(x,Gtk.TreeView):print('TREE',x.get_show_expanders(),x.get_level_indentation(),x.get_grid_lines(),x.get_style_context().to_string(Gtk.StyleContextPrintFlags.RECURSE))
for x in walk(w):
 if isinstance(x,Gtk.Label) and x.get_text() in ('Documents','apx'):
  print('LABEL BEFORE',x.get_text(),x.get_preferred_width(),x.get_layout().get_pixel_size(),x.get_style_context().get_property('font',x.get_state_flags()).to_string())
  attrs=Pango.AttrList();attrs.insert(Pango.attr_weight_new(Pango.Weight.BOLD));x.set_attributes(attrs)
  print('LABEL ATTRBOLD',x.get_preferred_width(),x.get_layout().get_pixel_size())
w.destroy()
