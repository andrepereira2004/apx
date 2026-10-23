"""Temporary local MPRIS player for UI verification; produces no sound or network."""
import time,os
from pathlib import Path
from gi.repository import Gio,GLib
connection=Gio.bus_get_sync(Gio.BusType.SESSION,None)
connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','RequestName',GLib.Variant('(su)',('org.mpris.MediaPlayer2.apx_trial',0)),None,Gio.DBusCallFlags.NONE,1000,None)
xml='''<node><interface name="org.mpris.MediaPlayer2.Player">
<method name="PlayPause"/><method name="Previous"/><method name="Next"/>
<method name="SetPosition"><arg name="TrackId" type="o" direction="in"/><arg name="Position" type="x" direction="in"/></method>
<property name="PlaybackStatus" type="s" access="read"/><property name="Metadata" type="a{sv}" access="read"/>
<property name="Position" type="x" access="read"/><property name="Rate" type="d" access="read"/>
<property name="CanControl" type="b" access="read"/><property name="CanSeek" type="b" access="read"/>
<property name="CanGoNext" type="b" access="read"/><property name="CanGoPrevious" type="b" access="read"/>
</interface></node>'''
started=time.monotonic();base=42;playing=True

def position():return int((base+(time.monotonic()-started if playing else 0))*1000000)
def getprop(connection,sender,path,interface,name):
    values={'PlaybackStatus':GLib.Variant('s','Playing' if playing else 'Paused'),'Metadata':GLib.Variant('a{sv}',{'mpris:trackid':GLib.Variant('o','/apx/trial/one'),'mpris:length':GLib.Variant('x',240000000),'xesam:title':GLib.Variant('s','APX · teste do leitor'),'xesam:artist':GLib.Variant('as',['Pré-visualização local'])}), 'Position':GLib.Variant('x',position()),'Rate':GLib.Variant('d',1.0)}
    return values.get(name,GLib.Variant('b',name in ('CanControl','CanSeek')))
def method(connection,sender,path,interface,name,args,invocation):
    global base,started,playing
    if name=='SetPosition':
        track,value=args.unpack()
        if track=='/apx/trial/one':base=value/1000000;started=time.monotonic()
    elif name=='PlayPause':base=position()/1000000;started=time.monotonic();playing=not playing
    invocation.return_value(None)
connection.register_object('/org/mpris/MediaPlayer2',Gio.DBusNodeInfo.new_for_xml(xml).interfaces[0],method,getprop,None)
(Path.home()/'.cache/apx-island-player.pid').write_text(str(os.getpid()))
loop=GLib.MainLoop();GLib.timeout_add_seconds(120,lambda:(loop.quit(),False)[1]);loop.run()
