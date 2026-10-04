"""Generate per-instance WinPE assets; never execute or format a device.

The output is staged for validation before being embedded in a dedicated WIM.
Firmware entry registration remains the responsibility of the Linux finalizer.
"""
import re
from pathlib import Path
from apx_native_instances_v3 import validate_windows_install_plan


def render(plan, template: str, *, display_drivers=()):
    plan = validate_windows_install_plan(plan)
    reuse=plan['profile']=='apx-native-slot-reuse-plan-v3'
    if reuse and not display_drivers:
        raise ValueError('replacement Windows requires embedded display drivers')
    if len(display_drivers)>8 or any(not re.fullmatch(r'[a-z0-9_.]+_amd64_[0-9a-f]{16}', name) for name in display_drivers):
        raise ValueError('invalid display driver package name')
    table = plan['after']
    parts = {p['uuid'].lower(): p for p in table['partitions']}
    new = plan['new']
    windows = parts[new['partuuid']]
    esp = parts[new['esp_partuuid']]
    linux = table['partitions'][1]
    setup = table['partitions'][3]
    label_suffix = new['generation'].replace('-', '')[:7].upper()
    windows_label = 'APXW' + label_suffix
    esp_label = 'APXE' + label_suffix
    values = dict(profile='apx-native-windows-install-contract-v3', name=new['name'],
                  generation=new['generation'], plan_sha256=plan['plan_sha256'],
                  size_gib=new['size_gib'], disk_guid=table['id'].upper(),
                  disk_bytes=(table['lastlba'] + 34) * table['sectorsize'], image_index=6)
    for role, part in [('efi', esp), ('linux', linux), ('windows', windows), ('setup', setup)]:
        values[role + '_partition_guid'] = part['uuid'].upper()
        values[role + '_start_sector'] = part['start']
        values[role + '_sector_count'] = part['size']
    values['windows_label'], values['efi_label'] = windows_label, esp_label
    if display_drivers and not reuse:
        values['source_partition_guid'] = table['partitions'][2]['uuid'].upper()
        for index,name in enumerate(display_drivers,1):values['display_driver_'+str(index)]=name
    elif reuse:
        values['embedded_driver_count']=len(display_drivers)
        for index,name in enumerate(display_drivers,1):values['display_driver_'+str(index)]=name
    contract = ''.join(f'{key}={value}\r\n' for key, value in values.items())
    script = template.replace('\r\n', '\n')
    # Parameterize only exact, reviewed singleton assumptions. Guard every
    # replacement so a changed template cannot silently produce a mixed script.
    def replace(old, new_text):
        nonlocal script
        if old not in script:
            raise ValueError('WinPE template changed: ' + old[:80])
        script = script.replace(old, new_text)
    replace('@echo off', '@echo off\nchcp 65001 >nul')
    replace('v2', 'v3')
    replace('APXWINTARGET', windows_label)
    replace('"APX_EFI" "1024 MB"', f'"{esp_label}" "512 MB"')
    replace('EFI "APX_EFI"', f'EFI "{esp_label}"')
    # New Windows owns a separate EFI volume. Existing Linux/Windows EFI must
    # not be mounted or rewritten by this installer.
    for line in script.splitlines():
        if ('linux-boot-manager' in line or 'apx-efi-tree' in line or 'linux-boot-preservation' in line):
            replace(line + '\n', '')
    begin = script.index('X:\\Windows\\System32\\bcdedit.exe /sysstore')
    end = script.index('if not exist "%APX_MEDIA%\\sources\\install.swm" call :fatal APX-BCD-18', begin)
    script = script[:begin] + 'rem No global BCD or firmware writes; Linux registers the exact new EFI partition.\n' + script[end:]
    begin = script.index(':load_expected\n')
    end = script.index('\n:find_disk\n', begin)
    loading = ':load_expected\nif not exist "%APX_EXPECTED%" exit /b 1\n'
    loading += 'for /f "usebackq tokens=1,* delims==" %%A in ("%APX_EXPECTED%") do set "APX_%%A=%%B"\n'
    loading += ''.join(f'if not "!APX_{key}!"=="{value}" exit /b 1\n' for key, value in values.items())
    loading += f'set "APX_WINDOWS_SIZE_TEXT={new["size_gib"]} GB"\n'
    loading += f'set "APX_LINUX_SIZE_TEXT={linux["size"] * table["sectorsize"] // 1024**3} GB"\nexit /b 0\n'
    script = script[:begin] + loading + script[end:]
    if display_drivers and not reuse:
        driver_stage = 'set "APX_STEP=display-drivers"\necho APX Windows: a preparar os controladores dos monitores.\n'
        driver_stage += 'call :find_partition SOURCE "ebd0a0a2-b9e5-4433-87c0-68b6b72699c7" "-" "'+str(plan['existing']['size_gib'])+' GB" || call :fatal APX-DRIVER-02 source-partition\n'
        driver_stage += 'call :choose_letter SOURCE T || call :fatal APX-DRIVER-03 source-letter\n'
        driver_stage += 'call :mount_basic_partition !APX_PART_SOURCE! !APX_LETTER_SOURCE! SOURCE "APXWINTARGET" || call :fatal APX-DRIVER-04 source-volume\n'
        driver_stage += 'set "APX_SOURCE=!APX_LETTER_SOURCE!:\"\n'
        driver_stage += 'call :validate_contract "%APX_SOURCE%\\APX-'+new['generation']+'.ini" || call :fatal APX-DRIVER-05 source-contract\n'
        for index,name in enumerate(display_drivers,1):
            driver_stage += 'X:\\Windows\\System32\\dism.exe /Image:%APX_TARGET%\\ /Add-Driver /Driver:"%APX_SOURCE%\\Windows\\System32\\DriverStore\\FileRepository\\'+name+'" /Recurse >>"%APX_LOG%" 2>&1\n'
            driver_stage += 'if errorlevel 1 call :fatal APX-DRIVER-06 display-driver-'+str(index)+'\n'
        replace('set "APX_STEP=windows-boot-manager"',driver_stage+'\nset "APX_STEP=windows-boot-manager"')
    elif reuse:
        driver_stage='set "APX_STEP=display-drivers"\necho APX Windows: a preparar os controladores dos monitores.\n'
        for index,name in enumerate(display_drivers,1):
            driver_stage+='if not exist "X:\\APXDrivers\\'+name+'\\" call :fatal APX-DRIVER-07 embedded-driver-'+str(index)+'\n'
            driver_stage+='X:\\Windows\\System32\\dism.exe /Image:%APX_TARGET%\\ /Add-Driver /Driver:"X:\\APXDrivers\\'+name+'" /Recurse >>"%APX_LOG%" 2>&1\n'
            driver_stage+='if errorlevel 1 call :fatal APX-DRIVER-06 display-driver-'+str(index)+'\n'
        replace('set "APX_STEP=windows-boot-manager"',driver_stage+'\nset "APX_STEP=windows-boot-manager"')
    labels={'initialization':'A iniciar','disk-identity':'A verificar o SSD','partition-identities':'A verificar as partições',
            'apply-windows-11-pro':'A instalar o Windows','stage-apx-integration':'A preparar rede e integração APX',
            'windows-boot-manager':'A preparar o arranque','success-record':'Instalação concluída'}
    script='\n'.join(line+('\necho APX Windows: '+labels[line[14:-1]] if line.startswith('set "APX_STEP=') and line[14:-1] in labels else '') for line in script.split('\n'))
    # Generation-specific logs/status do not overwrite another installation's
    # diagnostics on shared media. Contract is also carried on target/new EFI.
    destination = 'APX\\Native\\' + new['name'] + '\\' + new['generation']
    shared_contract = '%APX_MEDIA%\\APX\\install-contract-v3.ini'
    if script.count(shared_contract) != 1:
        raise ValueError('WinPE setup contract template changed')
    script = script.replace(shared_contract, '%APX_MEDIA%\\' + destination + '\\install-contract-v3.ini')
    shared_status = '%APX_MEDIA%\\APX\\install-status-v3.ini'
    if script.count(shared_status) != 21:
        raise ValueError('WinPE status template changed')
    generation_line = 'echo generation=!APX_generation!'
    if script.count(generation_line) != 2:
        raise ValueError('WinPE generation status template changed')
    script = script.replace(generation_line, generation_line + '\n>>"' + shared_status + '" echo plan_sha256=!APX_plan_sha256!')
    script = script.replace(shared_status, '%APX_MEDIA%\\' + destination + '\\install-status-v3.ini')
    script = script.replace('%APX_MEDIA%\\APX\\install-', '%APX_MEDIA%\\' + destination + '\\install-')
    script = script.replace('%APX_MEDIA%\\APX\\dism-', '%APX_MEDIA%\\' + destination + '\\dism-')
    script = script.replace('%APX_MEDIA%\\APX\\bcd-', '%APX_MEDIA%\\' + destination + '\\bcd-')
    script = script.replace('APX native Windows installer v3 started.', 'APX native Windows installer v3 started: ' + new['name'] + '.')
    if '/sysstore' in script or '/set {bootmgr}' in script or '/set {fwbootmgr}' in script:
        raise ValueError('global firmware mutation survived generation')
    return {'contract': contract, 'script': script.replace('\n', '\r\n'),
            'windows_label': windows_label, 'efi_label': esp_label,
            'media_directory': destination, 'name': new['name'], 'generation': new['generation']}
