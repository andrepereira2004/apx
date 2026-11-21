"""Build instance-bound WinPE media from an owner-verified official Windows ISO.

The compiler is installed only in a disposable tooling root, never on the Host.
All heavy work is explicit future execution, not module import or installer staging.
"""
from pathlib import Path
from contextlib import contextmanager
import json
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from apx_portable_native import partition_node, validate_plan
from apx_portable_native_io import run, mounted, file_hash, regular

ASSETS=Path('/usr/share/apx/portable-native-v4')


def register_source(iso,sha256,index,driver_archive=None,driver_sha256=None):
    if not re.fullmatch('[a-f0-9]{64}',sha256) or type(index) is not int or not 1<=index<=100:
        raise ValueError('official ISO SHA256 and positive image index are required')
    source=regular(Path(iso).absolute(),minimum=1024**3)
    if file_hash(source)!=sha256:raise ValueError('ISO does not match the owner-registered official digest')
    value={'schema':4,'profile':'apx-portable-native-source-v4','iso':str(source),
           'sha256':sha256,'image_index':index}
    if driver_archive:
        path=regular(Path(driver_archive).absolute(),maximum=4*1024**3)
        if not re.fullmatch('[a-f0-9]{64}',driver_sha256 or '') or file_hash(path)!=driver_sha256:
            raise ValueError('driver archive SHA256 differs')
        value.update(driver_archive=str(path),driver_sha256=driver_sha256)
    return value


def source_check(value):
    if value.get('schema')!=4 or value.get('profile')!='apx-portable-native-source-v4':raise ValueError('native ISO source not registered')
    return register_source(value['iso'],value['sha256'],value['image_index'],value.get('driver_archive'),value.get('driver_sha256'))


def c_wide(value):
    # All wide strings in the header are generated paths/UUIDs, not UI input.
    if any(ord(c)<32 or ord(c)>126 or c in '"' for c in value):raise ValueError('unsafe generated C string')
    return 'L"'+value.replace('\\','\\\\')+'"'


def header(plan,disk_bytes,index,files):
    plan=validate_plan(plan);table=plan['after'];identity=plan['identity']
    if type(disk_bytes) is not int or disk_bytes<(table['lastlba']+1)*table['sectorsize']:
        raise ValueError('disk capacity does not contain GPT')
    lines=['#include <stdint.h>','#include <wchar.h>',
        'struct apx_part { unsigned number; const wchar_t *uuid,*type; uint64_t offset,length; };',
        'struct apx_file { const wchar_t *name; const char *sha256; };',
        '#define APX_DISK_GUID '+c_wide(table['id']),
        '#define APX_SERIAL '+c_wide(identity['serial']),
        '#define APX_WWN '+c_wide(identity['wwn']),
        '#define APX_DISK_BYTES '+str(disk_bytes)+'ULL',
        '#define APX_SECTOR_SIZE '+str(table['sectorsize']),
        '#define APX_FIRST_USABLE '+str(table['firstlba']*table['sectorsize'])+'ULL',
        '#define APX_USABLE_LENGTH '+str((table['lastlba']-table['firstlba']+1)*table['sectorsize'])+'ULL',
        '#define APX_IMAGE_INDEX '+str(index),
        '#define APX_LINUX_ESP '+c_wide(identity['esp_partuuid']),
        '#define APX_LINUX_PATH '+c_wide(r'\EFI\BOOT\BOOTX64.EFI'),
        '#define APX_GENERATION "'+plan['generation']+'"',
        '#define APX_PLAN_SHA256 "'+plan['sha256']+'"']
    for role,p in zip(('WINDOWS','ESP','MSR','SETUP'),plan['slots']):
        lines+=['#define APX_'+role+'_UUID '+c_wide(p['uuid']),
                '#define APX_'+role+'_UUID_TEXT "'+p['uuid']+'"']
    lines+=['#define APX_PART_COUNT '+str(len(table['partitions'])),'static const struct apx_part apx_parts[] = {']
    for p in table['partitions']:
        number=next(n for n in range(1,129) if partition_node(table['device'],n)==p['node'])
        lines+=['{'+str(number)+','+c_wide(p['uuid'])+','+c_wide(p['type'])+','+
                str(p['start']*table['sectorsize'])+'ULL,'+str(p['size']*table['sectorsize'])+'ULL},']
    lines+=['};','#define APX_FILE_COUNT '+str(len(files)),'static const struct apx_file apx_files[] = {']
    for name,sha in sorted(files.items()):
        if not re.fullmatch('[a-f0-9]{64}',sha) or '..' in Path(name).parts:raise ValueError('invalid WinPE input digest')
        lines+=['{'+c_wide(name.replace('/','\\'))+',"'+sha+'"},']
    return '\n'.join(lines+['};',''])


@contextmanager
def compiler_root(parent):
    directory=Path(tempfile.mkdtemp(prefix='tooling-',dir=parent))
    try:
        run('pacstrap','-K',directory,'base','mingw-w64-gcc',timeout=1800)
        yield directory
    finally:
        # pacstrap keyring agents belong only to this disposable root.
        try:run('gpgconf','--homedir',directory/'etc/pacman.d/gnupg','--kill','gpg-agent')
        except Exception:pass
        if any(str(directory)==line or line.startswith(str(directory)+'/') for line in run('findmnt','-rn','-o','TARGET').splitlines()):
            raise ValueError('compiler root still has mounts; preserve it for explicit cleanup')
        shutil.rmtree(directory)


def extract_drivers(archive,target):
    import tarfile
    with tarfile.open(archive) as tar:
        total=0
        for member in tar:
            path=Path(member.name)
            if path.is_absolute() or '..' in path.parts or not (member.isfile() or member.isdir()):
                raise ValueError('driver archive must contain only relative regular files/directories')
            total+=member.size
            if total>4*1024**3:raise ValueError('driver archive exceeds bound')
            dest=target/path
            if member.isdir():dest.mkdir(parents=True,exist_ok=True)
            else:
                dest.parent.mkdir(parents=True,exist_ok=True)
                with tar.extractfile(member) as src,dest.open('xb') as dst:shutil.copyfileobj(src,dst)
                dest.chmod(0o644)
    if not any(p.suffix.lower()=='.inf' for p in target.rglob('*') if p.is_file()):raise ValueError('driver archive has no INF files')


def wim_xml(image):
    raw=subprocess.run(['wimlib-imagex','info',str(image),'--xml'],check=True,capture_output=True,timeout=120).stdout
    return ET.fromstring(raw)


def build(plan,source,directory,disk_bytes):
    plan=validate_plan(plan);source=source_check(source);directory=Path(directory)
    directory.mkdir(mode=0o700,parents=True,exist_ok=False)
    output=directory/'media';output.mkdir();(output/'APX').mkdir()
    with mounted(source['iso'],readonly=True,options=['loop']) as iso:
        image=iso/'sources/install.wim'
        if not image.is_file():image=iso/'sources/install.esd'
        if not image.is_file():raise ValueError('ISO has no install.wim/install.esd')
        metadata=wim_xml(image)
        selected=[p for p in metadata.findall('IMAGE') if p.get('INDEX')==str(source['image_index'])]
        if len(selected)!=1 or selected[0].findtext('WINDOWS/ARCH')!='9':raise ValueError('selected image is not x86_64 Windows')
        # Export only the chosen edition, so WinPE always applies index 1.
        export=directory/'selected.wim'
        run('wimlib-imagex','export',image,str(source['image_index']),export,'--compress=LZX','--check',timeout=3600)
        for item in iso.iterdir():
            if item.name.lower()=='sources':continue
            if item.is_dir():shutil.copytree(item,output/item.name)
            elif item.is_file():shutil.copyfile(item,output/item.name)
        (output/'sources').mkdir()
        boot=output/'sources/boot.wim';shutil.copyfile(iso/'sources/boot.wim',boot)
        run('wimlib-imagex','split',export,output/'sources/install.swm','3500','--check',timeout=3600)
        export.unlink()
    # Windows installer distributions use different casing; normalize critical paths.
    for relative in ['efi/boot/bootx64.efi','boot/BCD','boot/boot.sdi']:
        current=output
        for name in relative.split('/'):
            matches=[p for p in current.iterdir() if p.name.lower()==name.lower()]
            if len(matches)!=1:raise ValueError('ISO boot file absent: '+relative)
            chosen=matches[0]
            if chosen.name!=name:chosen.rename(current/name)
            current=current/name
    for name in ['return.ps1','return-startup.cmd','provision.cmd']:
        source_asset=regular(ASSETS/name)
        if name.endswith('.cmd'):
            (output/'APX'/name).write_bytes(source_asset.read_text(encoding='utf-8').replace('\n','\r\n').encode('utf-8'))
        else:shutil.copyfile(source_asset,output/'APX'/name)
    if source.get('driver_archive'):extract_drivers(source['driver_archive'],output/'APX/Drivers')
    # Whole-media hashes become an input both to Linux recovery and to WinPE.
    # The helper and patched boot.wim are verified by Linux after compilation.
    inputs={str(p.relative_to(output)):file_hash(p) for p in output.rglob('*') if p.is_file() and p!=boot}
    builddir=directory/'build';builddir.mkdir()
    (builddir/'contract.h').write_text(header(plan,disk_bytes,1,inputs))
    shutil.copyfile(regular(ASSETS/'helper.c'),builddir/'helper.c')
    with compiler_root(directory) as tooling:
        (tooling/'build').mkdir(exist_ok=True)
        run('systemd-nspawn','--quiet','--directory='+str(tooling),'--register=no','--private-network','--read-only','--tmpfs=/tmp:mode=1777',
            '--bind='+str(builddir)+':/build','--chdir=/build',
            '/usr/bin/x86_64-w64-mingw32-gcc','-std=c11','-O2','-Wall','-Wextra','-municode','-static',
            '-o','apx-native.exe','helper.c','-ladvapi32',timeout=300)
    helper=output/'APX/apx-native.exe';shutil.copyfile(builddir/'apx-native.exe',helper)
    # Setup index is independently selected by metadata, not a fixed language/edition.
    info=wim_xml(boot)
    candidates=[p for p in info.findall('IMAGE') if p.findtext('WINDOWS/ARCH')=='9' and
                'setup' in (p.findtext('NAME','')+' '+p.findtext('DESCRIPTION','')).lower()]
    if len(candidates)!=1:raise ValueError('cannot uniquely identify the x86_64 Setup WinPE image')
    index=candidates[0].get('INDEX')
    startup=builddir/'winpeshl.ini'
    startup.write_bytes((ASSETS/'winpeshl.ini').read_text().replace('\n','\r\n').encode('ascii'))
    commands='add "'+str(helper)+'" /APX/apx-native.exe\nadd "'+str(startup)+'" /Windows/System32/winpeshl.ini\n'
    if (output/'APX/Drivers').is_dir():commands+='add "'+str(output/'APX/Drivers')+'" /APXDrivers\n'
    run('wimlib-imagex','update',boot,index,'--check','--rebuild',input=commands,timeout=1200)
    # Firmware boot.wim uses its own header's boot index. Make it explicit.
    run('wimlib-imagex','info',boot,index,'--boot')
    run('wimlib-imagex','verify',boot,timeout=1200)
    for exe in ['dism.exe','bcdboot.exe','cmd.exe','wpeinit.exe','wpeutil.exe']:
        run('wimlib-imagex','dir',boot,index,'--path=/Windows/System32/'+exe)
    files={str(p.relative_to(output)):file_hash(p) for p in output.rglob('*') if p.is_file()}
    total=sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
    if total>plan['slots'][3]['size']*plan['after']['sectorsize']-256*1024**2:raise ValueError('Windows media exceeds reserved setup capacity')
    if any(p.stat().st_size>=4*1024**3 for p in output.rglob('*') if p.is_file()):raise ValueError('media has a file too large for FAT32')
    return {'schema':4,'profile':'apx-portable-native-media-v4','generation':plan['generation'],
            'plan_sha256':plan['sha256'],'source':source,'files':files,'media_bytes':total,
            'boot_wim_index':int(index),'image_index':1}
