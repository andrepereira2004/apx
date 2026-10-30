"""Run the existing native UI fixture, checking PNG pixels without optional Pillow."""
from pathlib import Path
import struct,zlib
ROOT=Path(__file__).resolve().parents[2]
def pixels(path):
 data=Path(path).read_bytes();pos=8;packed=b''
 while pos<len(data):
  n=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];chunk=data[pos+8:pos+8+n];pos+=n+12
  if kind==b'IHDR':w,h,depth,colour,_,_,interlace=struct.unpack('>IIBBBBB',chunk)
  if kind==b'IDAT':packed+=chunk
 assert depth==8 and colour in (2,6) and interlace==0,(depth,colour,interlace)
 channels=4 if colour==6 else 3;stride=w*channels;raw=zlib.decompress(packed);last=bytearray(stride);result=[]
 for y in range(h):
  offset=y*(stride+1);f=raw[offset];row=bytearray(raw[offset+1:offset+1+stride])
  for x in range(stride):
   a=row[x-channels] if x>=channels else 0;b=last[x];c=last[x-channels] if x>=channels else 0
   if f==1:predict=a
   elif f==2:predict=b
   elif f==3:predict=(a+b)//2
   elif f==4:
    p=a+b-c;dist=[abs(p-a),abs(p-b),abs(p-c)];predict=[a,b,c][dist.index(min(dist))]
   else:assert f==0;predict=0
   row[x]=(row[x]+predict)&255
  result.extend(tuple(row[x:x+channels]) for x in range(0,stride,channels));last=row
 return w,h,result
source=ROOT/'audit/2026-10-22-inbox-camera/validate-ui.py'
code=source.read_text();a=code.index(' from PIL import Image, ImageChops');b=code.index('finally:shutil.rmtree(stage)',a)
code=code[:a]+''' first=pixels(home/'.cache/camera-first.png');second=pixels(home/'.cache/camera-second.png')
 white=sum(1 for p in first[2] if min(p[:3])>220 and (len(p)==3 or p[3]>100))
 assert 4<white<250,white
 assert first!=second,'Contour pixels did not move'
 print('VISIBLE_WHITE_MOVING_TRACE_PASS',white)
'''+code[b:]
exec(compile(code,str(source),'exec'),dict(__file__=str(source),pixels=pixels))
