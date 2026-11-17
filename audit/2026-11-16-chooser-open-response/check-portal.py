from gi.repository import Gio,GLib
from pathlib import Path
import json
fixture=Path('/tmp/apx-portal-response-fixture.txt');fixture.write_text('APX chooser response fixture\n')
bus=Gio.bus_get_sync(Gio.BusType.SESSION,None);loop=GLib.MainLoop();result=[]
def response(connection,sender,path,interface,signal,parameters,data):
 code,values=parameters.unpack();result.append((code,values));print('RESPONSE',json.dumps(result),flush=True);loop.quit()
bus.signal_subscribe(None,'org.freedesktop.portal.Request','Response',None,None,Gio.DBusSignalFlags.NONE,response,None)
reply=bus.call_sync('org.freedesktop.portal.Desktop','/org/freedesktop/portal/desktop','org.freedesktop.portal.FileChooser','OpenFile',GLib.Variant('(ssa{sv})',('', 'APX portal response validation',{'handle_token':GLib.Variant('s','apx_response_test'),'multiple':GLib.Variant('b',True),'current_folder':GLib.Variant('ay',list(b'/tmp\0'))})),None,Gio.DBusCallFlags.NONE,10000,None)
print('REQUEST',reply.unpack(),flush=True)
GLib.timeout_add_seconds(35,lambda:(loop.quit(),False)[1]);loop.run()
assert result and result[0][0]==0 and result[0][1]['uris']==[fixture.as_uri()],result
print('PASS: real desktop portal delivers selected URI to client',flush=True)
