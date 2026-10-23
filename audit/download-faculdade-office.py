from pathlib import Path
import urllib.request,concurrent.futures,hashlib,json,os
root=Path('/home/apx/.wine4office/drive_c/odt/Office/Data')
version='16.0.20326.20144'
base='https://officecdn.microsoft.com/pr/492350f6-3a01-4f97-b9c0-c7c6ddf67d60/Office/Data/'
files=[version+'/'+n for n in ['stream.x64.x-none.dat','stream.x64.en-us.dat','stream.x64.pt-pt.dat','stream.x64.x-none.dat.cat','stream.x64.en-us.dat.cat','stream.x64.pt-pt.dat.cat','i641033.cab','i642070.cab','s641033.cab','s642070.cab']]+['v64.cab']
def fetch(rel):
 path=root/rel;path.parent.mkdir(parents=True,exist_ok=True)
 partial=path.with_suffix(path.suffix+'.part');digest=hashlib.sha256();total=0
 with urllib.request.urlopen(base+rel,timeout=60) as response,partial.open('wb') as output:
  expected=int(response.headers['Content-Length'])
  while chunk:=response.read(1024*1024):
   output.write(chunk);digest.update(chunk);total+=len(chunk)
  assert total==expected,(rel,total,expected)
 os.replace(partial,path)
 record={'path':rel,'bytes':total,'sha256':digest.hexdigest(),'source':base+rel};print(json.dumps(record),flush=True);return record
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:records=list(ex.map(fetch,files))
(root/'apx-download-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
