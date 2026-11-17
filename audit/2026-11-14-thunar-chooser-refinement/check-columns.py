import gi,tempfile,os,datetime
from pathlib import Path
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib
fixture=tempfile.TemporaryDirectory(prefix='apx-column-check-')
p=Path(fixture.name);(p/'example.txt').write_text('abc');(p/'folder').mkdir()
os.utime(p/'example.txt',(1700000000,1700000000))
w=Gtk.FileChooserDialog(title='column-check',action=Gtk.FileChooserAction.OPEN)
w.set_current_folder(str(p));errors=[];found=[]
def scan(x):
 if isinstance(x,Gtk.TreeView):
  cols=x.get_columns();titles=[c.get_title() for c in cols if c.get_visible()]
  assert titles==['Nome','Tamanho','Tipo','Data de modificação'],titles
  m=x.get_model();i=m.get_iter_first();results={}
  while i:
   name=m.get_value(i,0);texts={}
   for c in cols:
    if not c.get_visible():continue
    c.cell_set_cell_data(m,i,False,False)
    texts[c.get_title()]=[cell.get_property('text') for cell in c.get_cells() if isinstance(cell,Gtk.CellRendererText)]
   results[name]=texts;i=m.iter_next(i)
  print(results,flush=True)
  assert results['example.txt']['Tipo']==['.txt'],results
  assert results['folder']['Tipo']==['Pasta'],results
  assert '3' in results['example.txt']['Tamanho'][0],results
  assert results['example.txt']['Data de modificação'][0]==datetime.datetime.fromtimestamp(1700000000).strftime('%d/%m/%Y'),results
  for c in cols:
   if c.get_visible():
    sort=c.get_sort_column_id();assert sort>=0
    m.set_sort_column_id(sort,Gtk.SortType.DESCENDING)
    assert m.get_sort_column_id()==(sort,Gtk.SortType.DESCENDING)
  found.append(True)
 if isinstance(x,Gtk.Container):
  for child in x.get_children():scan(child)
def done():
 try:scan(w)
 except Exception as e: errors.append(e)
 w.destroy();Gtk.main_quit();return False
w.show();GLib.timeout_add(700,done);Gtk.main();fixture.cleanup()
if errors:raise errors[0]
assert found
print('PASS: headings, size, extension, directory type, fixed date and native sorting.')
