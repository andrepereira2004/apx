import importlib.util,os,uuid
from pathlib import Path
spec=importlib.util.spec_from_file_location('client','/run/apx/host-services-client-v3.py');client=importlib.util.module_from_spec(spec);spec.loader.exec_module(client)
assert 'media.unmount' in client.exchange('capabilities.get',{})['operations']
print('PASS: active Environment descendant authenticated for media capability',flush=True)
root=Path('/media/apx-usb/USB-4079-3F8D');fixture=root/('.apx-unmount-test-'+uuid.uuid4().hex+'.txt')
try:
 with fixture.open('w+') as stream:
  stream.write('APX busy unmount validation\n');stream.flush()
  try:client.exchange('media.unmount',{'uuid':'4079-3F8D'})
  except RuntimeError as error:
   print('BUSY RESULT:',error,flush=True)
   assert 'utilização' in str(error)
  else:raise AssertionError('busy unmount unexpectedly succeeded')
  assert root.is_mount()
  assert not Path('/media/apx-usb/.ejected-4079-3F8D').exists()
 print('PASS: real busy volume stays mounted and is not marked safe',flush=True)
finally:
 fixture.unlink(missing_ok=True)
