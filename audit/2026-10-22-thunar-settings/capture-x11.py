"""Capture only the launcher's X11 drawable, without switching workspaces."""
import ctypes as C
import ctypes.util
from pathlib import Path
import struct,zlib
x=C.CDLL(ctypes.util.find_library('X11'))
x.XOpenDisplay.restype=C.c_void_p;x.XOpenDisplay.argtypes=[C.c_char_p]
d=x.XOpenDisplay(None);assert d
x.XDefaultRootWindow.argtypes=[C.c_void_p];x.XDefaultRootWindow.restype=C.c_ulong
x.XQueryTree.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_ulong),C.POINTER(C.c_ulong),C.POINTER(C.POINTER(C.c_ulong)),C.POINTER(C.c_uint)]
x.XFetchName.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_char_p)]
x.XFree.argtypes=[C.c_void_p]
def find(window,depth=0):
 name=C.c_char_p()
 if x.XFetchName(d,window,C.byref(name)) and name.value:
  match=name.value==b'Minecraft Launcher';x.XFree(name)
  if match:return window
 if depth>4:return None
 root=C.c_ulong();parent=C.c_ulong();children=C.POINTER(C.c_ulong)();count=C.c_uint()
 if not x.XQueryTree(d,window,C.byref(root),C.byref(parent),C.byref(children),C.byref(count)):return None
 ids=list(children[:count.value]);x.XFree(children)
 for child in ids:
  result=find(child,depth+1)
  if result:return result
window=find(x.XDefaultRootWindow(d));assert window
comp=C.CDLL(ctypes.util.find_library('Xcomposite'));comp.XCompositeNameWindowPixmap.argtypes=[C.c_void_p,C.c_ulong];comp.XCompositeNameWindowPixmap.restype=C.c_ulong
pixmap=comp.XCompositeNameWindowPixmap(d,window)
x.XGetGeometry.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_ulong),C.POINTER(C.c_int),C.POINTER(C.c_int),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint)]
r=C.c_ulong();a=C.c_int();b=C.c_int();w=C.c_uint();h=C.c_uint();border=C.c_uint();depth=C.c_uint();assert x.XGetGeometry(d,pixmap,C.byref(r),C.byref(a),C.byref(b),C.byref(w),C.byref(h),C.byref(border),C.byref(depth))
class XImage(C.Structure):
 _fields_=[('width',C.c_int),('height',C.c_int),('xoffset',C.c_int),('format',C.c_int),('data',C.c_void_p),('byte_order',C.c_int),('bitmap_unit',C.c_int),('bitmap_bit_order',C.c_int),('bitmap_pad',C.c_int),('depth',C.c_int),('bytes_per_line',C.c_int),('bits_per_pixel',C.c_int)]
x.XGetImage.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.c_int,C.c_uint,C.c_uint,C.c_ulong,C.c_int];x.XGetImage.restype=C.POINTER(XImage)
im=x.XGetImage(d,pixmap,0,0,w.value,h.value,C.c_ulong(-1),2);assert im
v=im.contents;assert v.bits_per_pixel==32 and v.byte_order==0
raw=C.string_at(v.data,v.bytes_per_line*v.height);rows=[]
for y in range(v.height):
 line=raw[y*v.bytes_per_line:y*v.bytes_per_line+v.width*4];rgb=bytearray(v.width*3)
 rgb[0::3]=line[2::4];rgb[1::3]=line[1::4];rgb[2::3]=line[0::4];rows.append(b'\0'+rgb)
def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',v.width,v.height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows),3))+chunk(b'IEND',b'')
Path('/home/apx/.cache/apx-launcher-native-capture.png').write_bytes(png);print(v.width,v.height)
