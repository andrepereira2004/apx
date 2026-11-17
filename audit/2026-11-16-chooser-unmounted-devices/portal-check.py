from gi.repository import Gio,GLib
import subprocess
bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
for method in ('OpenFile','SaveFile'):
 reply=bus.call_sync('org.freedesktop.portal.Desktop','/org/freedesktop/portal/desktop','org.freedesktop.portal.FileChooser',method,GLib.Variant('(ssa{sv})',('', 'APX verificar dispositivos',{'handle_token':GLib.Variant('s','apx_devices_'+method.lower()),'current_folder':GLib.Variant('ay',list(b'/home/apx/Downloads\0'))})),None,Gio.DBusCallFlags.NONE,10000,None)
 path=reply.unpack()[0];loop=GLib.MainLoop()
 def capture():
  subprocess.run(['grim','/tmp/apx-devices-'+method+'.png'],check=True)
  bus.call_sync('org.freedesktop.portal.Desktop',path,'org.freedesktop.portal.Request','Close',None,None,Gio.DBusCallFlags.NONE,5000,None)
  print('PASS:',method,'portal opened, captured, closed',flush=True);loop.quit();return False
 GLib.timeout_add(1500,capture);loop.run()
