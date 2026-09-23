#!/usr/bin/env python3
"""Build a generation-bound maintenance UKI in a private job directory only."""
import argparse,json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/usr/lib/apx');sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from apx_native_instances_v3 import validate_plan
from apx_native_offline_v3 import render

def build(job,rollback=False):
    plan=validate_plan(json.loads((job/'plan.json').read_bytes()))
    manifest=json.loads((job/'images/manifest.json').read_bytes())
    generation=plan['new']['generation'];action='rollback' if rollback else 'relocate'
    assets=job/('maintenance-'+action);assets.mkdir(mode=0o700)
    script=assets/'offline.sh';script.write_text(render(plan,manifest,rollback=rollback));script.chmod(0o755)
    unit=assets/'apx-native-offline-v3.service'
    unit.write_text('[Unit]\nDescription=APX native Windows offline migration\nDefaultDependencies=no\nConditionKernelCommandLine=apx.native_v3='+generation+'\nAfter=dev-mapper-cryptroot.device systemd-cryptsetup@cryptroot.service\nBefore=sysroot.mount initrd-root-fs.target\n[Service]\nType=oneshot\nExecStart=/usr/bin/apx-native-offline-v3\nStandardOutput=journal+console\nStandardError=journal+console\nTimeoutStartSec=infinity\n')
    hook_name='apx_native_v3_'+generation.replace('-','')
    hook=Path('/etc/initcpio/install')/hook_name
    if hook.exists():raise ValueError('maintenance build hook already exists')
    source=Path(__file__).parent
    library=Path('/usr/lib/apx') if Path('/usr/lib/apx/apx_native_offline_v3.py').exists() else source.parents[1]/'src'
    binaries=['bash','dd','stat','sha256sum','awk','cut','tr','id','blkid','blockdev','btrfs','cat','cryptsetup','mkdir','mount','mountpoint','sfdisk','sleep','sync','systemctl','umount','python3']
    text='#!/usr/bin/bash\nbuild() {\n add_module vfat\n'
    text+=''.join(' add_binary /usr/bin/'+name+'\n' for name in binaries)
    text+=' add_full_dir /usr/lib/python'+str(sys.version_info.major)+'.'+str(sys.version_info.minor)+'\n'
    for src,dest in [(script,'/usr/bin/apx-native-offline-v3'),(unit,'/usr/lib/systemd/system/apx-native-offline-v3.service'),(job/'plan.json','/usr/share/apx/native-v3-plan.json'),(source/'apx-native-offline-layout-v3.py','/usr/lib/apx/apx-native-offline-layout-v3.py'),(library/'apx_native_instances_v3.py','/usr/lib/apx/apx_native_instances_v3.py')]:
        text+=' add_file "'+str(src)+'" "'+dest+'"\n'
    text+=' add_symlink /usr/lib/systemd/system/initrd-root-fs.target.wants/apx-native-offline-v3.service ../apx-native-offline-v3.service\n}\n'
    hook.write_text(text);hook.chmod(0o644)
    config=assets/'mkinitcpio.conf';config.write_text('MODULES=(amdgpu nvidia nvidia_modeset nvidia_uvm nvidia_drm)\nBINARIES=()\nFILES=()\nHOOKS=(base systemd autodetect microcode modconf keyboard sd-vconsole block sd-encrypt filesystems fsck '+hook_name+')\nCOMPRESSION="zstd"\n')
    cmdline=assets/'cmdline';cmdline.write_text('rd.luks.name=3ad5fc06-c4eb-4bb2-936b-f75eff3bc1c4=cryptroot root=/dev/mapper/cryptroot rootflags=subvol=@ rw rd.plymouth=0 plymouth.enable=0 apx.native_v3='+generation+'\n')
    output=assets/'maintenance.efi'
    try:
        subprocess.run(['mkinitcpio','--nopost','-n','-c',str(config),'-k',os.uname().release,'-U',str(output),'--cmdline',str(cmdline),'--ukiconfig','/etc/kernel/uki.conf'],check=True)
        result=subprocess.run(['sbverify','--list',str(output)],check=True,text=True,capture_output=True)
        if 'image signature certificates' not in result.stdout:raise ValueError('maintenance UKI is not signed')
    finally:hook.unlink(missing_ok=True)
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--job',type=Path,required=True);parser.add_argument('--rollback',action='store_true');args=parser.parse_args()
    if os.geteuid()!=0:raise SystemExit('root required')
    print(build(args.job,args.rollback))
