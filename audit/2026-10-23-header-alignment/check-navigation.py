import json,subprocess
from pathlib import Path
prefix=json.loads(Path('audit/2026-10-23-settings-sidebar/session-prefix.json').read_text())
source=Path('config/environment-shell-v1/local/bin/apx-settings').read_text()
program='''import gi,time,json,threading
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib
m={'__name__':'check'}
exec(SOURCE,m)
w=m['Settings']();w.show_all()
main=threading.get_ident();heartbeats=[];completed=[]
def slow():
 assert threading.get_ident()==main
 box=w.network[1];w.clear(box)
 m['command'](['/usr/bin/sleep','0.3'])
 completed.append('network');box.pack_start(Gtk.Label(label='done'),False,False,0)
w.render_network=slow
start=time.monotonic();w.stack.set_visible_child_name('network');elapsed=time.monotonic()-start
assert elapsed < .08,elapsed
GLib.timeout_add(10,lambda: heartbeats.append(time.monotonic()) or False)
limit=time.monotonic()+.08
while time.monotonic()<limit:
 while Gtk.events_pending():Gtk.main_iteration()
 time.sleep(.001)
assert heartbeats and not completed
# Leave while the request is pending: its completion cannot repaint this page.
w.stack.set_visible_child_name('printing')
limit=time.monotonic()+.4
while time.monotonic()<limit:
 while Gtk.events_pending():Gtk.main_iteration()
 time.sleep(.001)
assert not completed and w.stack.get_visible_child_name()=='printing'
# Same page can load afresh, finish, and become interactive.
w.stack.set_visible_child_name('network')
limit=time.monotonic()+1
while time.monotonic()<limit and not completed:
 while Gtk.events_pending():Gtk.main_iteration()
 time.sleep(.001)
assert completed==['network'] and w.network[1].get_sensitive()
# Actual read-only pages complete without blocking navigation or changing settings.
results={}
for name in w.sections:
 if name=='network':continue
 start=time.monotonic();w.stack.set_visible_child_name(name);duration=time.monotonic()-start
 limit=time.monotonic()+25
 while not getattr(w,name)[1].get_sensitive() and time.monotonic()<limit:
  while Gtk.events_pending():Gtk.main_iteration()
  time.sleep(.001)
 assert getattr(w,name)[1].get_sensitive(),name
 results[name]=round(duration,4)
assert w.get_titlebar() is None and not w.get_decorated()
w.destroy()
print(json.dumps({'slow_request_switch_seconds':elapsed,'heartbeat':bool(heartbeats),'stale_result_ignored':True,'real_page_switch_seconds':results}))
'''
r=subprocess.run(prefix+['python3','-c','SOURCE='+repr(source)+'\n'+program],capture_output=True,text=True,timeout=100)
print(r.stdout,r.stderr);r.check_returncode()
Path('audit/2026-10-23-header-alignment/navigation-results.json').write_text(r.stdout)
