"""Stable upstream resolution for new Environment applications; no Host installs."""
from pathlib import Path, PurePosixPath
import datetime
import fcntl
import hashlib
import io
import json
import os
import re
import subprocess
import tarfile
import tempfile
import time
import urllib.request
import zipfile

REPOSITORIES = {'brave-bin':'brave/brave-browser', 'localsend-bin':'localsend/localsend',
                'gridcraft':'storytold/gridcraft','wordcraft':'storytold/wordcraft','deckcraft':'storytold/deckcraft'}
KEYRING = Path('/usr/share/apx/chatgpt-release-keyring.gpg')
OPENAI = 'https://persistent.oaistatic.com/codex-app-prod/linux/arch/x86_64/'

class FreshnessError(RuntimeError): pass

def fetch(url, limit=4*1024*1024):
    request=urllib.request.Request(url,headers={'User-Agent':'APX-stable-package-resolution/1','Cache-Control':'no-cache'})
    with urllib.request.urlopen(request,timeout=45) as response:
        if not response.url.startswith('https://'): raise FreshnessError('Redirecionamento sem HTTPS')
        data=response.read(limit+1)
    if len(data)>limit: raise FreshnessError('Resposta do fornecedor demasiado grande')
    return data

def latest_release(repository):
    value=json.loads(fetch('https://api.github.com/repos/'+repository+'/releases/latest'))
    if value.get('draft') is not False or value.get('prerelease') is not False or not re.fullmatch(r'v?\d+(?:\.\d+){1,3}',value.get('tag_name','')):
        raise FreshnessError('O fornecedor não devolveu uma versão estável válida')
    return value

def github_asset(release, repository, name):
    asset=next((a for a in release['assets'] if a['name']==name),None)
    prefix='https://github.com/'+repository+'/releases/download/'+release['tag_name']+'/'
    if not asset or not asset.get('browser_download_url','').startswith(prefix) or not re.fullmatch(r'sha256:[0-9a-f]{64}',asset.get('digest') or ''):
        raise FreshnessError('O fornecedor não publicou um pacote verificável: '+name)
    return asset['browser_download_url'],asset['digest'][7:]

def download(url, target, digest, limit=768*1024**2):
    request=urllib.request.Request(url,headers={'User-Agent':'APX-stable-package-resolution/1'})
    sha=hashlib.sha256();total=0
    with urllib.request.urlopen(request,timeout=60) as response,target.open('wb') as stream:
        if not response.url.startswith('https://'): raise FreshnessError('Redirecionamento sem HTTPS')
        while chunk:=response.read(1024*1024):
            total+=len(chunk)
            if total>limit: raise FreshnessError('Pacote demasiado grande')
            sha.update(chunk);stream.write(chunk)
        stream.flush();os.fsync(stream.fileno())
    if sha.hexdigest()!=digest: raise FreshnessError('O pacote não corresponde ao SHA-256 do fornecedor')
    target.chmod(0o644)

def package_info(path):
    with tarfile.open(path,'r:*') as archive:
        member=archive.getmember('.PKGINFO')
        if member.size>65536: raise FreshnessError('Metadados de pacote demasiado grandes')
        text=archive.extractfile(member).read().decode()
    return dict(line.split(' = ',1) for line in text.splitlines() if ' = ' in line)

def rebuild_brave(current, archive, target, version):
    """Replace the vendor payload; retain reviewed launcher, icons and desktop files."""
    with tarfile.open(current,'r:*') as old,zipfile.ZipFile(archive) as upstream,tarfile.open(target,'w:zst') as result:
        total=sum(m.file_size for m in upstream.infolist())
        if total>2*1024**3: raise FreshnessError('Imagem Brave demasiado grande')
        metadata=old.extractfile('.PKGINFO').read().decode()
        metadata=re.sub(r'^pkgver = .+$','pkgver = 1:'+version+'-1',metadata,flags=re.M)
        metadata=re.sub(r'^provides = brave=.+$','provides = brave='+version,metadata,flags=re.M)
        metadata=re.sub(r'^builddate = .+$','builddate = '+str(int(time.time())),metadata,flags=re.M)
        metadata=re.sub(r'^size = .+$','size = '+str(total),metadata,flags=re.M)
        data=metadata.encode();member=tarfile.TarInfo('.PKGINFO');member.size=len(data);member.mode=0o644;result.addfile(member,io.BytesIO(data))
        for member in old:
            if member.name=='usr' or member.name.startswith('usr/'):
                result.addfile(member,old.extractfile(member) if member.isfile() else None)
        for entry in upstream.infolist():
            name=PurePosixPath(entry.filename)
            if name.is_absolute() or '..' in name.parts or not name.parts or (entry.external_attr>>16)&0o170000==0o120000:
                raise FreshnessError('Caminho inválido no arquivo Brave')
            member=tarfile.TarInfo('opt/brave-bin/'+str(name));member.uid=member.gid=0;member.mtime=int(time.time())
            member.mode=(entry.external_attr>>16)&0o777 or (0o755 if entry.is_dir() else 0o644)
            if entry.is_dir(): member.type=tarfile.DIRTYPE;result.addfile(member)
            else:
                if name.name in {'brave','chrome_crashpad_handler','chrome-management-service'}: member.mode=0o755
                if name.name=='chrome-sandbox':member.mode=0o4755
                member.size=entry.file_size
                with upstream.open(entry) as stream:result.addfile(member,stream)
    target.chmod(0o644)

def rebuild_localsend(current, archive, target, version):
    with tarfile.open(current,'r:*') as old,tarfile.open(archive,'r:*') as upstream,tarfile.open(target,'w:zst') as result:
        members=upstream.getmembers()
        if sum(m.size for m in members)>2*1024**3: raise FreshnessError('Arquivo LocalSend demasiado grande')
        text=old.extractfile('.PKGINFO').read().decode()
        text=re.sub(r'^pkgver = .+$','pkgver = '+version+'-1',text,flags=re.M)
        text=re.sub(r'^builddate = .+$','builddate = '+str(int(time.time())),text,flags=re.M)
        text=re.sub(r'^size = .+$','size = '+str(sum(m.size for m in members)),text,flags=re.M)
        data=text.encode();meta=tarfile.TarInfo('.PKGINFO');meta.mode=0o644;meta.size=len(data);result.addfile(meta,io.BytesIO(data))
        for member in old:
            if member.name=='usr' or member.name.startswith('usr/'):
                result.addfile(member,old.extractfile(member) if member.isfile() else None)
        for member in members:
            name=PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts or not (member.isfile() or member.isdir()):
                raise FreshnessError('Caminho inválido no arquivo LocalSend')
            member.name='opt/localsend/'+str(name);member.uid=member.gid=0;member.mode &= 0o777
            result.addfile(member,upstream.extractfile(member) if member.isfile() else None)
    target.chmod(0o644)


def repackage_office(current, downloaded, target, package, version):
    with tarfile.open(current,'r:*') as old,tarfile.open(downloaded,'r:*') as upstream,tarfile.open(target,'w:zst') as result:
        metadata=upstream.extractfile('.PKGINFO').read().decode()
        if package_info(downloaded)['pkgname']!='ai.storyteller.'+package:
            raise FreshnessError('O pacote ArtCraft não pertence à aplicação esperada')
        metadata=re.sub(r'^(pkgname|pkgbase) = .+$',lambda m:m[1]+' = '+package,metadata,flags=re.M)
        data=metadata.encode();member=tarfile.TarInfo('.PKGINFO');member.mode=0o644;member.size=len(data);result.addfile(member,io.BytesIO(data))
        for member in upstream:
            if member.name.startswith('.'): continue
            name=PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts: raise FreshnessError('Caminho ArtCraft inválido')
            if package=='deckcraft' and member.name=='usr/bin/deckcraft': member.name='usr/lib/deckcraft/deckcraft'
            result.addfile(member,upstream.extractfile(member) if member.isfile() else None)
        if package=='deckcraft':
            member=old.getmember('usr/bin/deckcraft');result.addfile(member,old.extractfile(member))
            data=json.dumps({'apps':{'deckcraft':{'Pinned':'v'+version}}}).encode()
            member=tarfile.TarInfo('usr/share/apx/deckcraft/versions.json');member.size=len(data);member.mode=0o644;result.addfile(member,io.BytesIO(data))
    target.chmod(0o644)


def verify_signature(data, signature):
    subprocess.run(['gpgv','--keyring',str(KEYRING),str(signature),str(data)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)

def openai_latest(work):
    db=work/'openai-chatgpt.db';db.write_bytes(fetch(OPENAI+'openai-chatgpt.db'))
    sig=work/'openai-chatgpt.db.sig';sig.write_bytes(fetch(OPENAI+'openai-chatgpt.db.sig'))
    verify_signature(db,sig)
    with tarfile.open(db,'r:*') as archive:
        for member in archive:
            if member.name.endswith('/desc') and member.size<65536:
                text=archive.extractfile(member).read().decode()
                def field(name):
                    match=re.search(r'^%'+name+r'%\n([^\n]+)',text,re.M)
                    return match[1] if match else ''
                if field('NAME')=='chatgpt-bin':
                    name=field('FILENAME');sha=field('SHA256SUM')
                    if Path(name).name!=name or not name.startswith('chatgpt-bin-') or not re.fullmatch('[a-f0-9]{64}',sha):break
                    return field('VERSION'),name,OPENAI+name,sha
    raise FreshnessError('ChatGPT não está no índice assinado atual')

def ensure_current_package(package, current, directory):
    if package in {'nvidia-utils','salvador-de-mundos-apx'}: return current
    if package not in REPOSITORIES and package!='chatgpt-bin': raise FreshnessError('Aplicação sem fornecedor de atualização: '+package)
    directory=Path(directory);current=Path(current)
    with (directory/'.freshness.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        manifest=directory/(package+'-v1.json');record=json.loads(manifest.read_text())
        current=directory/record['filename']
        if hashlib.sha256(current.read_bytes()).hexdigest()!=record['sha256']:raise FreshnessError('O pacote guardado foi alterado')
        with tempfile.TemporaryDirectory(prefix='.fresh-',dir=directory) as folder:
            work=Path(folder);info=package_info(current)
            if package=='chatgpt-bin':
                version,name,url,sha=openai_latest(work)
                same=info['pkgver']==version
            else:
                repository=REPOSITORIES[package];release=latest_release(repository);version=release['tag_name'].lstrip('v')
                same=info['pkgver'].split(':')[-1].rsplit('-',1)[0]==version
                if not same:
                    if package=='brave-bin':name='brave-browser-'+version+'-linux-amd64.zip'
                    elif package=='localsend-bin': name='LocalSend-'+version+'-linux-x86-64.tar.gz'
                    else:name=package+'-'+version+'-linux-x86_64.pkg.tar.zst'
                    url,sha=github_asset(release,repository,name)
            if not same:
                print('A obter '+package+' '+version+' do fornecedor…',flush=True)
                downloaded=work/name
                # Reuse an already downloaded, verified Brave zip only for this run.
                cache=directory/'.brave-latest.zip.download'
                if package=='brave-bin' and cache.is_file() and hashlib.sha256(cache.read_bytes()).hexdigest()==sha:
                    downloaded.write_bytes(cache.read_bytes())
                elif (directory/('.inspect-'+name)).is_file() and hashlib.sha256((directory/('.inspect-'+name)).read_bytes()).hexdigest()==sha:
                    downloaded.write_bytes((directory/('.inspect-'+name)).read_bytes())
                else:download(url,downloaded,sha)
                if package=='brave-bin':
                    filename='brave-bin-1:'+version+'-1-x86_64.pkg.tar.zst';candidate=work/filename
                    rebuild_brave(current,downloaded,candidate,version)
                elif package=='localsend-bin':
                    filename='localsend-bin-'+version+'-1-x86_64.pkg.tar.zst';candidate=work/filename
                    rebuild_localsend(current,downloaded,candidate,version)
                elif package in {'gridcraft','wordcraft','deckcraft'}:
                    filename=package+'-'+version+'-1-x86_64.pkg.tar.zst';candidate=work/filename
                    repackage_office(current,downloaded,candidate,package,version)
                else:filename=name;candidate=downloaded
                if package=='chatgpt-bin':
                    sig=work/(name+'.sig');sig.write_bytes(fetch(url+'.sig'));verify_signature(candidate,sig)
                candidate_info=package_info(candidate)
                expected_version=('1:'+version+'-1') if package=='brave-bin' else version
                if candidate_info.get('pkgname')!=package or candidate_info.get('arch')!='x86_64' or (candidate_info.get('pkgver')!=expected_version if package in {'brave-bin','chatgpt-bin'} else candidate_info.get('pkgver','').rsplit('-',1)[0]!=version):
                    raise FreshnessError('A identidade do pacote não coincide com a versão estável')
                target=directory/filename
                # Keep old artifact and manifest for rollback; publish only verified bytes.
                backup=directory/(package+'-v1.before-'+str(time.time_ns())+'.json');backup.write_bytes(manifest.read_bytes());backup.chmod(0o644)
                os.replace(candidate,target);target.chmod(0o644)
                record=dict(schema=1,package=package,filename=filename,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),upstream_url=url,upstream_archive_sha256=sha)
                stage=work/'manifest.json';stage.write_text(json.dumps(record,indent=2)+'\n');stage.chmod(0o644);os.replace(stage,manifest)
                current=target
            return current
