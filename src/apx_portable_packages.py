"""Bootstrap reviewed application packages without depending on a pilot cache."""
from pathlib import Path
import base64
import fcntl
import hashlib
import io
import json
import os
import shutil
import tarfile
import tempfile

import apx_package_freshness as upstream

SEED = Path('/usr/share/apx/config-seeds/portable-packages-v2')


def verify_seed(seed=SEED):
    if seed.is_symlink() or not seed.is_dir():
        raise upstream.FreshnessError('As receitas de aplicações não estão disponíveis')
    inventory = seed / 'SHA256SUMS.json'
    if inventory.is_symlink():
        raise upstream.FreshnessError('Manifesto de receitas inválido')
    hashes = json.loads(inventory.read_text())
    if set(p.name for p in seed.iterdir()) != set(hashes) | {'SHA256SUMS.json'}:
        raise upstream.FreshnessError('Receitas de aplicações incompletas')
    for name, digest in hashes.items():
        path = seed / name
        if Path(name).name != name or path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise upstream.FreshnessError('A receita foi alterada: ' + name)
    return hashes


def recipe_archive(package, target, seed):
    values = json.loads((seed / (package + '.json')).read_text())
    with tarfile.open(target, 'w:zst') as archive:
        for name, content in values.items():
            if name != '.PKGINFO' and (not name.startswith('usr/') or '..' in Path(name).parts):
                raise upstream.FreshnessError('Caminho de receita inválido')
            data = base64.b64decode(content['base64'], validate=True) if isinstance(content, dict) else content.encode()
            member = tarfile.TarInfo(name)
            member.size = len(data)
            member.mode = 0o755 if name.startswith('usr/bin/') else 0o644
            archive.addfile(member, io.BytesIO(data))


def publish(package, candidate, directory):
    info = upstream.package_info(candidate)
    if info.get('pkgname') != package or info.get('arch') != 'x86_64':
        raise upstream.FreshnessError('Identidade do pacote inválida')
    target = directory / candidate.name
    os.replace(candidate, target)
    target.chmod(0o644)
    record = dict(schema=1, package=package, filename=target.name,
                  sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    temporary = directory / ('.' + package + '.json')
    with temporary.open('x') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.chmod(0o644)
    os.replace(temporary, directory / (package + '-v1.json'))
    return target


def resolve(package, directory, seed=SEED):
    """Return a current verified package; no package is installed on the Host."""
    verify_seed(seed)
    supported = set(upstream.REPOSITORIES) | {'chatgpt-bin', 'salvador-de-mundos-apx'}
    if package not in supported:
        raise upstream.FreshnessError('Pacote portátil não suportado: ' + package)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True, mode=0o755)
    if directory.is_symlink() or directory.stat().st_uid != 0 or directory.stat().st_mode & 0o022:
        raise upstream.FreshnessError('Diretório de pacotes não confiável')
    # The executor runs with umask 0077. Packages contain public distribution
    # data; the namespace's root and alpm reader need traversal of this cache.
    directory.chmod(0o755)
    with (directory / '.portable-packages.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = directory / (package + '-v1.json')
        if manifest.exists():
            if manifest.is_symlink():
                raise upstream.FreshnessError('Manifesto de pacote inválido')
            record = json.loads(manifest.read_text())
            name = record['filename']
            current = directory / name
            if record.get('schema') != 1 or record.get('package') != package or Path(name).name != name or current.is_symlink() or hashlib.sha256(current.read_bytes()).hexdigest() != record['sha256']:
                raise upstream.FreshnessError('Pacote guardado inválido')
            return upstream.ensure_current_package(package, current, directory)
        with tempfile.TemporaryDirectory(prefix='.portable-', dir=directory) as folder:
            work = Path(folder)
            if package == 'salvador-de-mundos-apx':
                record = json.loads((seed / (package + '-v1.json')).read_text())
                source = seed / record['filename']
                if Path(record['filename']).name != record['filename'] or hashlib.sha256(source.read_bytes()).hexdigest() != record['sha256']:
                    raise upstream.FreshnessError('Artefacto Salvador inválido')
                candidate = work / source.name
                shutil.copyfile(source, candidate)
            elif package == 'chatgpt-bin':
                version, name, url, digest = upstream.openai_latest(work)
                candidate = work / name
                upstream.download(url, candidate, digest)
                signature = work / (name + '.sig')
                signature.write_bytes(upstream.fetch(url + '.sig'))
                upstream.verify_signature(candidate, signature)
                if upstream.package_info(candidate).get('pkgver') != version:
                    raise upstream.FreshnessError('Versão ChatGPT diferente do índice assinado')
            else:
                repository = upstream.REPOSITORIES[package]
                release = upstream.latest_release(repository)
                version = release['tag_name'].lstrip('v')
                if package == 'brave-bin':
                    name = 'brave-browser-' + version + '-linux-amd64.zip'
                elif package == 'localsend-bin':
                    name = 'LocalSend-' + version + '-linux-x86-64.tar.gz'
                else:
                    name = package + '-' + version + '-linux-x86_64.pkg.tar.zst'
                url, digest = upstream.github_asset(release, repository, name)
                downloaded = work / name
                upstream.download(url, downloaded, digest)
                candidate = work / (package + '-' + ('1:' if package == 'brave-bin' else '') + version + '-1-x86_64.pkg.tar.zst')
                template = work / 'recipe.pkg.tar.zst'
                if package in {'brave-bin', 'localsend-bin', 'deckcraft'}:
                    recipe_archive(package, template, seed)
                else:
                    # GridCraft/WordCraft need no APX launcher override, but
                    # the shared repackager still opens a packaging template.
                    with tarfile.open(template, 'w:zst'):
                        pass
                if package == 'brave-bin':
                    upstream.rebuild_brave(template, downloaded, candidate, version)
                elif package == 'localsend-bin':
                    upstream.rebuild_localsend(template, downloaded, candidate, version)
                else:
                    upstream.repackage_office(template, downloaded, candidate, package, version)
                if upstream.package_info(candidate).get('pkgver', '').split(':')[-1].rsplit('-', 1)[0] != version:
                    raise upstream.FreshnessError('Versão diferente do fornecedor')
            return publish(package, candidate, directory)
