/* APX portable native v4. Instance-bound WinPE installer and UEFI return tool.
 * No partition-table, formatting or global BCD writes are implemented here.
 * Expected geometry and media hashes are compiled from a root-approved plan.
 */
#define UNICODE
#define _UNICODE
#define _WIN32_WINNT 0x0601
#include <windows.h>
#include <winioctl.h>
#include <wincrypt.h>
#include <stdio.h>
#include <wchar.h>
#include <stdint.h>
#include <stddef.h>
#include "contract.h"

static const WCHAR *efi_ns=L"{8BE4DF61-93CA-11d2-AA0D-00E098032B8C}";
static WCHAR media[4],target[4],esp[4];
static DWORD disk_number;
static int return_disk_identity(void);
static int guidtext(const GUID *g,const WCHAR *s){
    WCHAR text[40];swprintf(text,40,L"%08lx-%04x-%04x-%02x%02x-%02x%02x%02x%02x%02x%02x",
        g->Data1,g->Data2,g->Data3,g->Data4[0],g->Data4[1],g->Data4[2],g->Data4[3],
        g->Data4[4],g->Data4[5],g->Data4[6],g->Data4[7]);return _wcsicmp(text,s)==0;
}
static int execute(const WCHAR *application,WCHAR *command,DWORD timeout){
    STARTUPINFOW si={0};PROCESS_INFORMATION pi={0};DWORD code=1;si.cb=sizeof(si);
    wprintf(L"APX: %ls\n",command);fflush(stdout);
    if(!CreateProcessW(application,command,NULL,NULL,FALSE,0,NULL,NULL,&si,&pi))return 0;
    DWORD waited=WaitForSingleObject(pi.hProcess,timeout);
    if(waited!=WAIT_OBJECT_0){TerminateProcess(pi.hProcess,1);WaitForSingleObject(pi.hProcess,30000);}
    else GetExitCodeProcess(pi.hProcess,&code);
    CloseHandle(pi.hThread);CloseHandle(pi.hProcess);return waited==WAIT_OBJECT_0&&code==0;
}
static int privilege(const WCHAR *name){
    HANDLE token;TOKEN_PRIVILEGES tp;LUID luid;
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))return 0;
    if(!LookupPrivilegeValueW(NULL,name,&luid)){CloseHandle(token);return 0;}
    tp.PrivilegeCount=1;tp.Privileges[0].Luid=luid;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    SetLastError(0);BOOL ok=AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL);
    DWORD error=GetLastError();CloseHandle(token);return ok&&error==ERROR_SUCCESS;
}
static int linux_option(const BYTE *data,DWORD length){
    /* EFI_LOAD_OPTION: attributes/u16 path length/UTF16 description/devicepath.
     * Only a GPT hard-drive node + the exact APX file path is accepted. */
    if(length<10)return 0;
    DWORD offset=6;while(offset+2<=length&&*(const WORD*)(data+offset))offset+=2;
    offset+=2;DWORD end=offset+*(const WORD*)(data+4);if(end>length)return 0;
    int hd=0,file=0;
    while(offset+4<=end){
        WORD size=*(const WORD*)(data+offset+2);if(size<4||offset+size>end)return 0;
        if(data[offset]==4&&data[offset+1]==1&&size==42&&data[offset+40]==2&&data[offset+41]==2){
            if(guidtext((const GUID*)(data+offset+24),APX_LINUX_ESP))hd++;
        }
        if(data[offset]==4&&data[offset+1]==4&&size>=6&&size%2==0){
            const WCHAR *name=(const WCHAR*)(data+offset+4);
            if(name[(size-4)/2-1]==0&&_wcsicmp(name,APX_LINUX_PATH)==0)file++;
        }
        offset+=size;
    }
    return offset==end&&hd==1&&file==1;
}
static int set_linux_next(void){
    if(!return_disk_identity())return 0;
    if(!privilege(SE_SYSTEM_ENVIRONMENT_NAME))return 0;
    WORD order[256],new_order[256],chosen=0;BYTE option[65536];int matches=0;
    DWORD size=GetFirmwareEnvironmentVariableW(L"BootOrder",efi_ns,order,sizeof(order));
    if(!size||size%2||size>sizeof(order))return 0;
    for(DWORD n=0;n<size/2;n++){
        WCHAR name[9];swprintf(name,9,L"Boot%04X",order[n]);
        DWORD got=GetFirmwareEnvironmentVariableW(name,efi_ns,option,sizeof(option));
        if(got&&linux_option(option,got)){chosen=order[n];matches++;}
    }
    if(matches!=1)return 0;
    DWORD count=1;new_order[0]=chosen;
    for(DWORD n=0;n<size/2;n++)if(order[n]!=chosen)new_order[count++]=order[n];
    if(count*2!=size)return 0;
    if(!SetFirmwareEnvironmentVariableW(L"BootOrder",efi_ns,new_order,size)||
       !SetFirmwareEnvironmentVariableW(L"BootNext",efi_ns,&chosen,2))return 0;
    WORD check[256],next;DWORD got=GetFirmwareEnvironmentVariableW(L"BootOrder",efi_ns,check,sizeof(check));
    return got==size&&!memcmp(check,new_order,size)&&
        GetFirmwareEnvironmentVariableW(L"BootNext",efi_ns,&next,2)==2&&next==chosen;
}

static int hardware_id(HANDLE handle){
    STORAGE_PROPERTY_QUERY query={0};BYTE buffer[65536];DWORD returned;
    query.PropertyId=StorageDeviceProperty;query.QueryType=PropertyStandardQuery;
    if(wcslen(APX_SERIAL)){
        if(!DeviceIoControl(handle,IOCTL_STORAGE_QUERY_PROPERTY,&query,sizeof(query),buffer,sizeof(buffer),&returned,NULL))return 0;
        STORAGE_DEVICE_DESCRIPTOR *desc=(void*)buffer;
        if(returned<sizeof(*desc)||!desc->SerialNumberOffset||desc->SerialNumberOffset>=returned)return 0;
        const char *serial=(const char*)buffer+desc->SerialNumberOffset;
        size_t bound=returned-desc->SerialNumberOffset,length=0;
        while(length<bound&&serial[length])length++;
        if(length==bound||length>255)return 0;
        while(length&&serial[length-1]==' ')length--;
        while(length&&*serial==' '){serial++;length--;}
        WCHAR wide[256];for(size_t n=0;n<length;n++)wide[n]=(unsigned char)serial[n];wide[length]=0;
        return !wcscmp(wide,APX_SERIAL);
    }
    /* WWN-only disks: binary device-associated identifiers are compared as
     * hexadecimal, with the same optional 0x prefix used by Linux lsblk. */
    query.PropertyId=StorageDeviceIdProperty;
    if(!DeviceIoControl(handle,IOCTL_STORAGE_QUERY_PROPERTY,&query,sizeof(query),buffer,sizeof(buffer),&returned,NULL))return 0;
    STORAGE_DEVICE_ID_DESCRIPTOR *desc=(void*)buffer;
    if(returned<sizeof(*desc)||desc->NumberOfIdentifiers>128)return 0;
    DWORD offset=offsetof(STORAGE_DEVICE_ID_DESCRIPTOR,Identifiers);
    for(DWORD n=0;n<desc->NumberOfIdentifiers;n++){
        if(offset+offsetof(STORAGE_IDENTIFIER,Identifier)>returned)return 0;
        STORAGE_IDENTIFIER *id=(void*)(buffer+offset);
        if(offset+offsetof(STORAGE_IDENTIFIER,Identifier)+id->IdentifierSize>returned)return 0;
        if(id->CodeSet==StorageIdCodeSetBinary&&id->Association==StorageIdAssocDevice&&id->IdentifierSize>0&&id->IdentifierSize<=64){
            WCHAR hex[129];for(WORD j=0;j<id->IdentifierSize;j++)swprintf(hex+2*j,3,L"%02x",id->Identifier[j]);
            const WCHAR *expected=APX_WWN;if(!_wcsnicmp(expected,L"0x",2))expected+=2;
            if(wcslen(expected)&&!_wcsicmp(hex,expected))return 1;
        }
        if(n+1<desc->NumberOfIdentifiers){if(id->NextOffset<offsetof(STORAGE_IDENTIFIER,Identifier)||offset+id->NextOffset<=offset)return 0;offset+=id->NextOffset;}
    }
    return 0;
}
static int load_drivers(const WCHAR *directory,unsigned depth){
    if(depth>12)return 0;
    WCHAR glob[1024];swprintf(glob,1024,L"%ls\\*",directory);
    WIN32_FIND_DATAW data;HANDLE search=FindFirstFileW(glob,&data);
    if(search==INVALID_HANDLE_VALUE)return GetLastError()==ERROR_PATH_NOT_FOUND||GetLastError()==ERROR_FILE_NOT_FOUND;
    int ok=1;
    do {
        if(!wcscmp(data.cFileName,L".")||!wcscmp(data.cFileName,L".."))continue;
        WCHAR path[1024];if(wcslen(directory)+wcslen(data.cFileName)+2>=1024){ok=0;break;}
        swprintf(path,1024,L"%ls\\%ls",directory,data.cFileName);
        if(data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY){if(!load_drivers(path,depth+1)){ok=0;break;}}
        else {const WCHAR *extension=wcsrchr(path,L'.');if(extension&&!_wcsicmp(extension,L".inf")){
            WCHAR command[2048];swprintf(command,2048,L"drvload.exe \"%ls\"",path);
            if(!execute(L"X:\\Windows\\System32\\drvload.exe",command,120000)){ok=0;break;}
        }}
    } while(FindNextFileW(search,&data));FindClose(search);return ok;
}

static int check_disk(DWORD number){
    WCHAR path[64];swprintf(path,64,L"\\\\.\\PhysicalDrive%lu",number);
    HANDLE h=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    if(h==INVALID_HANDLE_VALUE)return 0;
    BYTE buffer[65536];DWORD returned;DISK_GEOMETRY_EX geometry;
    int ok=0;
    if(!hardware_id(h))goto done;
    if(!DeviceIoControl(h,IOCTL_DISK_GET_DRIVE_GEOMETRY_EX,NULL,0,buffer,sizeof(buffer),&returned,NULL))goto done;
    memcpy(&geometry,buffer,sizeof(geometry));
    if(geometry.Geometry.BytesPerSector!=APX_SECTOR_SIZE||geometry.DiskSize.QuadPart!=APX_DISK_BYTES)goto done;
    if(!DeviceIoControl(h,IOCTL_DISK_GET_DRIVE_LAYOUT_EX,NULL,0,buffer,sizeof(buffer),&returned,NULL))goto done;
    DRIVE_LAYOUT_INFORMATION_EX *layout=(void*)buffer;
    if(returned<offsetof(DRIVE_LAYOUT_INFORMATION_EX,PartitionEntry)||layout->PartitionStyle!=PARTITION_STYLE_GPT||
       !guidtext(&layout->Gpt.DiskId,APX_DISK_GUID)||
       (uint64_t)layout->Gpt.StartingUsableOffset.QuadPart!=APX_FIRST_USABLE||
       (uint64_t)layout->Gpt.UsableLength.QuadPart!=APX_USABLE_LENGTH||layout->PartitionCount>128||
       offsetof(DRIVE_LAYOUT_INFORMATION_EX,PartitionEntry)+layout->PartitionCount*sizeof(PARTITION_INFORMATION_EX)>returned)goto done;
    unsigned actual=0;
    for(DWORD n=0;n<layout->PartitionCount;n++){
        PARTITION_INFORMATION_EX *p=&layout->PartitionEntry[n];if(!p->PartitionLength.QuadPart)continue;
        actual++;int found=0;
        for(unsigned j=0;j<APX_PART_COUNT;j++){
            const struct apx_part *e=&apx_parts[j];
            if(p->PartitionStyle==PARTITION_STYLE_GPT&&
               guidtext(&p->Gpt.PartitionId,e->uuid)&&guidtext(&p->Gpt.PartitionType,e->type)&&
               (uint64_t)p->StartingOffset.QuadPart==e->offset&&
               (uint64_t)p->PartitionLength.QuadPart==e->length)found++;
        }
        if(found!=1)goto done;
    }
    ok=actual==APX_PART_COUNT;
 done:CloseHandle(h);return ok;
}

static int return_disk_identity(void){
    /* Later native creations may change other slots. For return, bind the
     * protected APX ESP and hardware, and reject cloned ESP UUIDs on any disk. */
    const struct apx_part *expected=NULL;
    for(unsigned n=0;n<APX_PART_COUNT;n++)if(!_wcsicmp(apx_parts[n].uuid,APX_LINUX_ESP))expected=&apx_parts[n];
    if(!expected)return 0;
    unsigned matches=0,admitted=0;
    for(DWORD number=0;number<64;number++){
        WCHAR path[64];swprintf(path,64,L"\\\\.\\PhysicalDrive%lu",number);
        HANDLE handle=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
        if(handle==INVALID_HANDLE_VALUE)continue;
        BYTE raw[65536];DWORD got;
        if(DeviceIoControl(handle,IOCTL_DISK_GET_DRIVE_LAYOUT_EX,NULL,0,raw,sizeof(raw),&got,NULL)){
            DRIVE_LAYOUT_INFORMATION_EX *layout=(void*)raw;
            if(got>=offsetof(DRIVE_LAYOUT_INFORMATION_EX,PartitionEntry)&&layout->PartitionStyle==PARTITION_STYLE_GPT&&
               layout->PartitionCount<=128&&offsetof(DRIVE_LAYOUT_INFORMATION_EX,PartitionEntry)+layout->PartitionCount*sizeof(PARTITION_INFORMATION_EX)<=got){
                for(DWORD n=0;n<layout->PartitionCount;n++){
                    PARTITION_INFORMATION_EX *part=&layout->PartitionEntry[n];
                    if(part->PartitionStyle==PARTITION_STYLE_GPT&&guidtext(&part->Gpt.PartitionId,APX_LINUX_ESP)){
                        matches++;
                        if(guidtext(&layout->Gpt.DiskId,APX_DISK_GUID)&&guidtext(&part->Gpt.PartitionType,expected->type)&&
                           (uint64_t)part->StartingOffset.QuadPart==expected->offset&&
                           (uint64_t)part->PartitionLength.QuadPart==expected->length&&hardware_id(handle))admitted++;
                    }
                }
            }
        }
        CloseHandle(handle);
    }
    return matches==1&&admitted==1;
}

static int mount_role(const WCHAR *uuid,WCHAR *destination){
    const struct apx_part *expected=NULL;
    for(unsigned n=0;n<APX_PART_COUNT;n++)if(!_wcsicmp(apx_parts[n].uuid,uuid))expected=&apx_parts[n];
    if(!expected)return 0;
    WCHAR volume[MAX_PATH];HANDLE search=FindFirstVolumeW(volume,MAX_PATH);
    if(search==INVALID_HANDLE_VALUE)return 0;
    WCHAR selected[MAX_PATH]=L"";int count=0;
    do {
        size_t len=wcslen(volume);volume[len-1]=0;
        HANDLE h=CreateFileW(volume,0,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
        volume[len-1]=L'\\';
        if(h!=INVALID_HANDLE_VALUE){
            BYTE raw[4096];DWORD returned;
            if(DeviceIoControl(h,IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS,NULL,0,raw,sizeof(raw),&returned,NULL)){
                VOLUME_DISK_EXTENTS *ext=(void*)raw;
                if(ext->NumberOfDiskExtents==1&&ext->Extents[0].DiskNumber==disk_number&&
                   (uint64_t)ext->Extents[0].StartingOffset.QuadPart==expected->offset&&
                   (uint64_t)ext->Extents[0].ExtentLength.QuadPart==expected->length){wcscpy(selected,volume);count++;}
            }
            CloseHandle(h);
        }
    } while(FindNextVolumeW(search,volume,MAX_PATH));FindVolumeClose(search);
    if(count!=1)return 0;
    DWORD drives=GetLogicalDrives();
    for(WCHAR letter=L'Z';letter>=L'D';letter--)if(!(drives&(1u<<(letter-L'A')))){
        WCHAR mount[4]={letter,L':',L'\\',0};
        if(SetVolumeMountPointW(mount,selected)){wcscpy(destination,mount);destination[2]=0;return 1;}
    }
    return 0;
}
static int hash_file(const WCHAR *path,const char *expected){
    HANDLE file=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    if(file==INVALID_HANDLE_VALUE)return 0;
    HCRYPTPROV provider=0;HCRYPTHASH hash=0;BYTE buffer[65536],value[32];DWORD got,size=32;BOOL readok;
    int ok=0;if(!CryptAcquireContextW(&provider,NULL,NULL,PROV_RSA_AES,CRYPT_VERIFYCONTEXT))goto done;
    if(!CryptCreateHash(provider,CALG_SHA_256,0,0,&hash))goto done;
    while((readok=ReadFile(file,buffer,sizeof(buffer),&got,NULL))&&got)if(!CryptHashData(hash,buffer,got,0))goto done;
    if(!readok||!CryptGetHashParam(hash,HP_HASHVAL,value,&size,0)||size!=32)goto done;
    char text[65];for(unsigned n=0;n<32;n++)sprintf(text+2*n,"%02x",value[n]);
    ok=!strcmp(text,expected);
 done:if(hash)CryptDestroyHash(hash);if(provider)CryptReleaseContext(provider,0);CloseHandle(file);return ok;
}
static int status(const char *state){
    if(!media[0])return 0;
    WCHAR path[MAX_PATH];swprintf(path,MAX_PATH,L"%ls\\APX\\status.ini",media);
    FILE *out=_wfopen(path,L"wb");if(!out)return 0;
    fprintf(out,"profile=apx-portable-WinPE-status-v4\r\ngeneration=%s\r\nplan_sha256=%s\r\nstate=%s\r\nwindows_partuuid=%s\r\nesp_partuuid=%s\r\n",
        APX_GENERATION,APX_PLAN_SHA256,state,APX_WINDOWS_UUID_TEXT,APX_ESP_UUID_TEXT);
    int ok=!ferror(out);fflush(out);int close=fclose(out);return ok&&close==0;
}
static int install(void){
    if(!load_drivers(L"X:\\APXDrivers",0))return 0;
    DWORD matches=0;for(DWORD n=0;n<64;n++)if(check_disk(n)){disk_number=n;matches++;}
    if(matches!=1||!mount_role(APX_SETUP_UUID,media)||!mount_role(APX_WINDOWS_UUID,target)||!mount_role(APX_ESP_UUID,esp))return 0;
    WCHAR path[1024],command[4096];
    for(unsigned n=0;n<APX_FILE_COUNT;n++){
        swprintf(path,1024,L"%ls\\%ls",media,apx_files[n].name);
        if(!hash_file(path,apx_files[n].sha256))return 0;
    }
    swprintf(path,1024,L"%ls\\Windows",target);
    if(GetFileAttributesW(path)!=INVALID_FILE_ATTRIBUTES)return 0; /* retry needs Linux authorization/format */
    if(!check_disk(disk_number)||!status("applying"))return 0;
    swprintf(command,4096,L"\"X:\\Windows\\System32\\dism.exe\" /Apply-Image /ImageFile:%ls\\sources\\install.swm /SWMFile:%ls\\sources\\install*.swm /Index:%u /ApplyDir:%ls\\ /CheckIntegrity /LogPath:%ls\\APX\\dism.log",media,media,APX_IMAGE_INDEX,target,media);
    if(!execute(L"X:\\Windows\\System32\\dism.exe",command,4*60*60*1000))return 0;
    swprintf(command,4096,L"\"X:\\Windows\\System32\\cmd.exe\" /d /c \"%ls\\APX\\provision.cmd\" %ls",media,target);
    if(!execute(L"X:\\Windows\\System32\\cmd.exe",command,30*60*1000))return 0;
    if(!check_disk(disk_number))return 0;
    swprintf(command,4096,L"\"X:\\Windows\\System32\\bcdboot.exe\" %ls\\Windows /s %ls /f UEFI /v",target,esp);
    if(!execute(L"X:\\Windows\\System32\\bcdboot.exe",command,5*60*1000))return 0;
    const WCHAR *required[]={L"\\EFI\\Microsoft\\Boot\\bootmgfw.efi",L"\\EFI\\Microsoft\\Boot\\BCD"};
    for(unsigned n=0;n<2;n++){swprintf(path,1024,L"%ls%ls",esp,required[n]);if(GetFileAttributesW(path)==INVALID_FILE_ATTRIBUTES)return 0;}
    return status("boot-prepared");
}
int wmain(int argc,WCHAR **argv){
    if(argc==2&&!wcscmp(argv[1],L"--return")){
        if(!set_linux_next())return 2;
        WCHAR command[]=L"shutdown.exe /r /t 0";
        WCHAR app[MAX_PATH];GetSystemDirectoryW(app,MAX_PATH);wcscat(app,L"\\shutdown.exe");
        return execute(app,command,30000)?0:2;
    }
    if(argc!=2||wcscmp(argv[1],L"--install"))return 2;
    /* This binary runs installation only from the WinPE RAM drive. */
    WCHAR system[MAX_PATH];GetSystemWindowsDirectoryW(system,MAX_PATH);
    if(_wcsicmp(system,L"X:\\Windows"))return 2;
    int ok=install();if(!ok){status("failed");fwprintf(stderr,L"APX Windows: installation stopped. Evidence retained on setup media.\n");}
    WCHAR command[]=L"wpeutil.exe reboot";execute(L"X:\\Windows\\System32\\wpeutil.exe",command,60000);
    return ok?0:2;
}
