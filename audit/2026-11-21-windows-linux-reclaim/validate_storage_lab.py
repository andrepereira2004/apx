#!/usr/bin/env python3
"""Disposable loop-device encryption/Btrfs validation; never uses pilot partitions."""
import json,os,pathlib,subprocess,tempfile
root=pathlib.Path(tempfile.mkdtemp(prefix='apx-reclaim-storage-',dir='/var/lib/apx/tmp'))
root.chmod(0o700)
def run(*args,input=None):return subprocess.check_output(args,input=input,stderr=subprocess.PIPE)
secret=os.urandom(48); loops=[]; maps=[]; mounted=False
names=['apx-reclaim-lab-'+str(os.getpid())+'-'+str(n) for n in range(2)]
mount=root/'mnt';mount.mkdir()
try:
 for index,name in enumerate(names):
  image=root/('member-'+str(index));image.touch();image.chmod(0o600)
  with image.open('r+b') as f:f.truncate(384*1024**2)
  loop=run('losetup','--find','--show',str(image)).decode().strip()
  assert loop.startswith('/dev/loop');loops.append(loop)
  run('cryptsetup','luksFormat','--batch-mode','--type=luks2','--pbkdf=pbkdf2','--key-file=-',loop,input=secret)
  run('cryptsetup','open','--key-file=-',loop,name,input=secret);maps.append(name)
 run('mkfs.btrfs','-q','/dev/mapper/'+names[0])
 run('mount','/dev/mapper/'+names[0],str(mount));mounted=True
 (mount/'preserved.txt').write_text('existing-linux-data')
 run('btrfs','device','add','/dev/mapper/'+names[1],str(mount))
 run('btrfs','filesystem','sync',str(mount))
 run('umount',str(mount));mounted=False
 for name in reversed(maps):run('cryptsetup','close',name)
 maps=[]
 # Re-open both encrypted members with the same credential, as the initramfs must.
 for loop,name in zip(loops,names):
  run('cryptsetup','open','--key-file=-',loop,name,input=secret);maps.append(name)
 run('mount','-o','device=/dev/mapper/'+names[1],'/dev/mapper/'+names[0],str(mount));mounted=True
 assert (mount/'preserved.txt').read_text()=='existing-linux-data'
 run('btrfs','device','stats','-c',str(mount))
 print(json.dumps({'encrypted_members':2,'old_data_preserved':True,'remount_after_unlock':True,'device_errors':0,'pilot_partitions_touched':False}))
finally:
 secret=b''
 if mounted:run('umount',str(mount))
 for name in reversed(maps):run('cryptsetup','close',name)
 for loop in reversed(loops):run('losetup','--detach',loop)
 import shutil;shutil.rmtree(root)
