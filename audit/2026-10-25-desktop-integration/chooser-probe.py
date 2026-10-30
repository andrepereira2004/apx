"""Session-local GTK native chooser probe using only a private empty directory."""
import gi
import json
import subprocess
import tempfile
from pathlib import Path

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio

TITLE = 'APX disposable integration probe'
results = {'scope': 'GTK3 native chooser in active session; not Brave/Thunderbird validation', 'cases': []}


def hypr(verb):
    return json.loads(subprocess.check_output(['hyprctl', '-j', verb], text=True))


def sample():
    clients = hypr('clients')
    parent = next((c for c in clients if c.get('title') == TITLE), None)
    dialogs = [c for c in clients if c.get('class') == 'xdg-desktop-portal-gtk']
    active = hypr('activewindow')
    return dict(parent_geometry={k: parent[k] for k in ('at','size','floating') if k in parent} if parent else None,
                portal_dialogs=[{k: c[k] for k in ('size','floating','xwayland') if k in c} for c in dialogs],
                parent_focused=bool(parent and active.get('address') == parent.get('address')),
                portal_focused=active.get('class') == 'xdg-desktop-portal-gtk')


bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
names = bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','ListNames',None,None,Gio.DBusCallFlags.NONE,3000,None).unpack()[0]
results['portal_services'] = [n for n in names if 'portal' in n]
results['directory_default'] = Gio.AppInfo.get_default_for_type('inode/directory',False).get_id()
# Do not touch a chooser already being used by the owner.
if any(c.get('class') == 'xdg-desktop-portal-gtk' for c in hypr('clients')):
    raise SystemExit('Refusing probe while an existing portal chooser is open')
original = hypr('activewindow').get('address')
window = Gtk.Window(title=TITLE)
window.set_default_size(560, 320)
window.add(Gtk.Label(label='APX — teste temporário de integração'))
window.show_all()
index = 0
native = None
with tempfile.TemporaryDirectory(prefix='apx-chooser-probe-') as directory:
    def finish():
        current = hypr('activewindow')
        own = next((c for c in hypr('clients') if c.get('title') == TITLE), None)
        restore = own and current.get('address') == own.get('address')
        window.destroy()
        if restore and original:
            subprocess.run(['hyprctl','dispatch','focuswindow','address:'+original],capture_output=True)
        Gtk.main_quit()
        return False

    def start():
        global native
        action = [Gtk.FileChooserAction.OPEN, Gtk.FileChooserAction.SAVE][index]
        row = {'action': ['open','save'][index], 'before': sample()}
        results['cases'].append(row)
        native = Gtk.FileChooserNative.new(TITLE, window, action, None, None)
        native.set_current_folder(directory)
        if action == Gtk.FileChooserAction.SAVE:
            native.set_current_name('apx-disposable.txt')
        filt = Gtk.FileFilter(); filt.set_name('Texto'); filt.add_pattern('*.txt'); native.add_filter(filt)
        native.show()
        GLib.timeout_add(1800, during)
        return False

    def during():
        results['cases'][-1]['during'] = sample()
        native.hide(); native.destroy()
        GLib.timeout_add(700, after)
        return False

    def after():
        global index
        row = results['cases'][-1]
        row['after'] = sample()
        row['parent_geometry_stable'] = row['before']['parent_geometry'] == row['during']['parent_geometry'] == row['after']['parent_geometry']
        index += 1
        GLib.timeout_add(500, start if index < 2 else finish)
        return False

    GLib.timeout_add(900, start)
    GLib.timeout_add(12000, finish)
    try:
        Gtk.main()
    finally:
        if native:
            native.destroy()
        window.destroy()
    results['directory_empty_after'] = not any(Path(directory).iterdir())
print(json.dumps(results, indent=2))
