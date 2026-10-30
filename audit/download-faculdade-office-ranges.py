from pathlib import Path
import urllib.request,concurrent.futures,hashlib,json,os,time
root=Path('/home/apx/.wine4office/drive_c/odt/Office/Data');version='16.0.20326.20144'
base='https://officecdn.microsoft.com/pr/492350f6-3a01-4f97-b9c0-c7c6ddf67d60/Office/Data/'
files=[version+'/'+n for n in ['stream.x64.x-none.dat','stream.x64.en-us.dat','stream.x64.pt-pt.dat','stream.x64.x-none.dat.cat','stream.x64.en-us.dat.cat','stream.x64.pt-pt.dat.cat','i641033.cab','i642070.cab','s641033.cab','s642070.cab']]+['v64.cab']
def fetch(rel):
 path=root/rel;url=base+rel
 with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=30) as r:total=int(r.headers['Content-Length'])
 partial=path.with_suffix(path.suffix+'.part');path.parent.mkdir(parents=True,exist_ok=True)
 if not (path.is_file() and path.stat().st_size==total):
  start=partial.stat().st_size if partial.exists() else 0
  assert start<=total
  fd=os.open(partial,os.O_RDWR|os.O_CREAT,0o644)
  def chunk(bounds):
   a,z=bounds
   for retry in range(4):
    try:
     with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes={a}-{z}'}),timeout=45) as response:
      assert response.status==206
      assert response.headers['Content-Range']==f'bytes {a}-{z}/{total}'
      data=response.read(z-a+2);assert len(data)==z-a+1
      assert os.pwrite(fd,data,a)==len(data)
     return len(data)
    except Exception:
     if retry==3:raise
     time.sleep(1+retry)
  try:
   parts=[(a,min(total-1,a+4*1024**2-1)) for a in range(start,total,4*1024**2)]
   finished=start
   with concurrent.futures.ThreadPoolExecutor(max_workers=8 if total>500*1024**2 else 2) as pool:
    for n in pool.map(chunk,parts):
     finished+=n
     if finished//(256*1024**2)!=(finished-n)//(256*1024**2):print(rel,f'{finished}/{total}',flush=True)
   assert finished==total;os.fsync(fd)
  except Exception:
   os.ftruncate(fd,start);raise
  finally:os.close(fd)
  assert partial.stat().st_size==total;os.replace(partial,path)
 digest=hashlib.sha256()
 with path.open('rb') as f:
  while data:=f.read(1024**2):digest.update(data)
 record={'path':rel,'bytes':total,'sha256':digest.hexdigest(),'source':url};print(json.dumps(record),flush=True);return record
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:records=list(ex.map(fetch,files))
(root/'apx-download-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
