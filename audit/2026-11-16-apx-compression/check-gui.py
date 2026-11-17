import os,sys,tempfile,runpy,time,zipfile
from pathlib import Path
os.environ['GTK_MODULES']=str(Path.home()/'.local/lib/apx/libchooser-places.so')
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib

def walk(w):
 yield w
 if isinstance(w,Gtk.Container):
  for child in w.get_children():yield from walk(child)
def activate():
 for w in Gtk.Window.list_toplevels():
  if w.get_title()!='Comprimir':continue
  buttons=[b for b in walk(w) if isinstance(b,Gtk.Button) and b.get_label()=='Comprimir']
  if buttons:
   buttons[0].clicked();print('PASS: actual APX Comprimir button activated',flush=True);return False
 return True
with tempfile.TemporaryDirectory(prefix='apx-compress-gui-') as td:
 source=Path(td)/'sample file.txt';source.write_text('APX interface verification\n')
 GLib.timeout_add(600,activate)
 GLib.timeout_add_seconds(15,lambda:(_ for _ in ()).throw(RuntimeError('GUI timed out')))
 sys.argv=[str(Path.home()/'.local/bin/apx-compress-v1'),str(source)]
 runpy.run_path(sys.argv[0],run_name='__main__')
 output=Path(td)/'sample file.zip'
 with zipfile.ZipFile(output) as archive:assert archive.read(source.name)==source.read_bytes()
 print('PASS: production GUI created a valid ZIP; temporary fixture removed',flush=True)
# Also verify the same backend on the owner-approved FAT file bridge.
root=Path('/media/apx-usb/USB-4079-3F8D')
if root.is_mount():
 sys.path.insert(0,str(Path.home()/'.local/lib/apx'))
 from apx_compression import create_archive
 with tempfile.TemporaryDirectory(prefix='.apx-compression-test-',dir=root) as td:
  source=Path(td)/'fixture.txt';source.write_text('APX removable media verification\n')
  output=Path(td)/'verified.zip';create_archive([source],output,'zip')
  with zipfile.ZipFile(output) as archive:assert archive.read(source.name)==source.read_bytes()
 print('PASS: archive created and read on FAT USB bridge; fixture removed',flush=True)
