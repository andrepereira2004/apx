import gi,time
gi.require_version('Gtk','3.0')
from gi.repository import GLib
GLib.set_prgname('thunar')
from gi.repository import Gtk
class TestWindow(Gtk.Window):
 __gtype_name__='ThunarWindow'
w=TestWindow();box=Gtk.Box();w.add(box);b=Gtk.Button(label='Test');b.set_tooltip_text('Before map');box.add(b)
def settle():
 end=time.monotonic()+.15
 while time.monotonic()<end:
  while Gtk.events_pending():Gtk.main_iteration_do(False)
  time.sleep(.005)
w.show_all();settle();assert not b.get_has_tooltip()
b.set_tooltip_text('After map');assert not b.get_has_tooltip()
dynamic=Gtk.Button(label='Later');dynamic.set_tooltip_text('Dynamic');box.add(dynamic);dynamic.show();settle();assert not dynamic.get_has_tooltip()
print('PASS: Thunar module suppresses existing, updated and dynamically added widget tooltips.')
w.destroy()
