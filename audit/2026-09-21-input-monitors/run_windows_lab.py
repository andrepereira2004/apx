from pathlib import Path
import os,subprocess,json
out=Path(__file__).resolve().parent;lab=out/'windows-lab';tools=out/'windows-lab-tools';env=os.environ|{'LD_LIBRARY_PATH':str(tools/'usr/lib')}
command=[str(tools/'usr/bin/qemu-system-x86_64'),'-L',str(tools/'usr/share/qemu'),'-machine','q35,accel=kvm','-cpu','host','-m','4096','-smp','4','-nodefaults','-no-reboot','-display','none','-vga','std','-device','qemu-xhci','-device','usb-kbd','-device','usb-tablet','-drive','if=pflash,format=raw,readonly=on,file='+str(tools/'usr/share/edk2/x64/OVMF_CODE.4m.fd'),'-drive','if=pflash,format=raw,file='+str(lab/'OVMF_VARS.fd'),'-drive','if=none,id=disk,format=raw,cache=none,file='+str(lab/'disk.raw'),'-device','ide-hd,drive=disk,bus=ide.0,bootindex=1','-qmp','unix:'+str(lab/'qmp.sock')+',server=on,wait=off','-serial','file:'+str(lab/'serial.log'),'-pidfile',str(lab/'qemu.pid')]
(lab/'qemu-command.json').write_text(json.dumps(command,indent=2))
with (lab/'qemu.log').open('w') as log:
 p=subprocess.Popen(command,env=env,stdout=log,stderr=log,start_new_session=True)
print(p.pid)
