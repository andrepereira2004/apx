import subprocess,tempfile,time,zipfile,tarfile
from pathlib import Path
with tempfile.TemporaryDirectory(prefix='apx-create-archive-') as directory:
 root=Path(directory)
 file=root/'sample file.txt';file.write_text('APX ZIP and TAR compression test\n')
 folder=root/'sample folder';folder.mkdir();(folder/'nested.txt').write_text('Nested content\n')
 for extension in ('zip','tar'):
  output=root/('created.'+extension)
  subprocess.run(['/usr/bin/file-roller','--add-to='+str(output),str(file),str(folder)],check=True,timeout=25)
  deadline=time.monotonic()+10
  while True:
   try:
    if extension=='zip':
     with zipfile.ZipFile(output) as archive:
      assert archive.read('sample file.txt')==file.read_bytes()
      assert archive.read('sample folder/nested.txt')==(folder/'nested.txt').read_bytes()
    else:
     with tarfile.open(output) as archive:
      assert archive.extractfile('sample file.txt').read()==file.read_bytes()
      assert archive.extractfile('sample folder/nested.txt').read()==(folder/'nested.txt').read_bytes()
    break
   except (OSError,zipfile.BadZipFile,tarfile.TarError,KeyError):
    if time.monotonic()>deadline:raise
    time.sleep(.1)
  print('PASS: File Roller created',extension.upper(),'with selected file and nested folder; contents verified',flush=True)
print('PASS: disposable compression fixtures removed',flush=True)
