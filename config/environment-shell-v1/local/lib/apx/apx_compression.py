"""Local APX archive creation, including Bedrock ZIP containers."""
from __future__ import annotations
import contextlib
import ctypes
import errno
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tarfile
import tempfile
import threading
import zipfile

FORMATS = (
    ('zip', 'ZIP', '.zip'), ('tar', 'TAR', '.tar'),
    ('tar.gz', 'TAR · gzip', '.tar.gz'), ('tar.xz', 'TAR · xz', '.tar.xz'),
    ('mcworld', 'Minecraft · Mundo Bedrock', '.mcworld'),
    ('mcpack', 'Minecraft · Pacote de recursos ou comportamento', '.mcpack'),
    ('mcaddon', 'Minecraft · Complemento', '.mcaddon'),
)
EXTENSIONS = {key: extension for key, _, extension in FORMATS}
MINECRAFT = {'mcworld', 'mcpack', 'mcaddon'}

class Cancelled(Exception):
    pass

def check_cancel(cancel):
    if cancel is not None and cancel.is_set():
        raise Cancelled('Compressão cancelada')

def extension_for_name(name):
    return next((key for key, _, ext in sorted(FORMATS, key=lambda f: -len(f[2]))
                 if name.lower().endswith(ext)), None)

def with_extension(name, kind):
    old = extension_for_name(name)
    if old:
        name = name[:-len(EXTENSIONS[old])]
    return name + EXTENSIONS[kind]

def suggest_format(paths):
    if len(paths) == 1 and paths[0].is_dir():
        if (paths[0] / 'level.dat').is_file() and (paths[0] / 'db').is_dir(): return 'mcworld'
        if (paths[0] / 'manifest.json').is_file(): return 'mcpack'
    if paths and all(p.suffix.lower() in {'.mcpack', '.mcworld'} for p in paths): return 'mcaddon'
    return 'zip'

class Entry:
    def __init__(self, name, path=None, archive=None, info=None, data=None):
        self.name, self.path, self.archive, self.info, self.data = name, path, archive, info, data
    @property
    def is_dir(self):
        return self.name.endswith('/')
    @property
    def is_link(self):
        return self.path.is_symlink() if self.path else bool(self.info and stat.S_ISLNK(self.info.external_attr >> 16))
    @property
    def size(self):
        if self.is_dir: return 0
        if self.data is not None: return len(self.data)
        if self.info: return self.info.file_size
        return self.path.lstat().st_size
    def open(self):
        if self.info: return self.archive.open(self.info)
        if self.data is not None:
            import io
            return io.BytesIO(self.data)
        return self.path.open('rb')

def filesystem_entries(paths, cancel=None):
    result = []
    def visit(path, name):
        check_cancel(cancel)
        if path.is_symlink():
            result.append(Entry(name, path=path))
        elif path.is_dir():
            result.append(Entry(name.rstrip('/') + '/', path=path))
            for child in sorted(path.iterdir()): visit(child, name.rstrip('/') + '/' + child.name)
        elif path.is_file(): result.append(Entry(name, path=path))
        else: raise ValueError('Não é possível comprimir este tipo de ficheiro: ' + str(path))
    for path in paths: visit(path, path.name)
    return result

def archive_entries(archive):
    result = []
    seen = set()
    for info in archive.infolist():
        path = PurePosixPath(info.filename)
        if path.is_absolute() or '..' in path.parts or '\\' in info.filename or not path.parts:
            raise ValueError('O ZIP contém um caminho inválido.')
        name = path.as_posix() + ('/' if info.is_dir() else '')
        if name in seen: raise ValueError('O ZIP contém nomes repetidos: ' + name)
        seen.add(name)
        result.append(Entry(name, archive=archive, info=info))
    return result

def flatten_single_root(entries):
    # Strip only enclosing folders shared by all selected entries. Never
    # search arbitrarily for a world among several different selected worlds.
    while entries:
        tops = {PurePosixPath(e.name).parts[0] for e in entries}
        if len(tops) != 1: break
        top = next(iter(tops)); prefix = top + '/'
        if any(e.name == top and not e.is_dir for e in entries): break
        flattened = []
        for e in entries:
            if e.name == prefix: continue
            if not e.name.startswith(prefix): return entries
            flattened.append(Entry(e.name[len(prefix):], e.path, e.archive, e.info, e.data))
        entries = flattened
    return entries

def validate_minecraft(entries, kind):
    if any(e.is_link for e in entries):
        raise ValueError('Os pacotes Minecraft não podem conter ligações simbólicas.')
    files = {e.name for e in entries if not e.is_dir}
    if kind == 'mcworld':
        if 'level.dat' not in files or not any(name.startswith('db/') for name in files):
            raise ValueError('Seleciona a pasta de um mundo Bedrock, com level.dat e a pasta db. Um mundo Java precisa de conversão antes de criar um .mcworld.')
    elif kind == 'mcpack' and 'manifest.json' not in files:
        raise ValueError('Seleciona a pasta do pacote Minecraft que contém manifest.json.')
    elif kind == 'mcaddon':
        if not files or any('/' in name or not name.lower().endswith(('.mcpack', '.mcworld')) for name in files):
            raise ValueError('Para criar um .mcaddon, seleciona pacotes .mcpack ou mundos .mcworld. Também podes selecionar pastas de pacotes com manifest.json.')

def publish_no_replace(source, target):
    # Linux renameat2 works on the removable FAT bridge as well as Btrfs.
    libc = ctypes.CDLL(None, use_errno=True)
    rename = getattr(libc, 'renameat2', None)
    if rename is None: raise OSError(errno.ENOSYS, 'O sistema não suporta publicação segura de arquivos')
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(source), -100, os.fsencode(target), 1) != 0:
        code = ctypes.get_errno()
        if code == errno.EEXIST: raise FileExistsError('Já existe um arquivo com esse nome. Escolhe outro nome.')
        raise OSError(code, os.strerror(code), str(target))

def write_zip(entries, output, cancel, progress):
    total = sum(e.size for e in entries) or 1
    done = 0
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for entry in entries:
            check_cancel(cancel)
            if entry.is_dir:
                archive.writestr(entry.name, b''); continue
            if entry.is_link:
                info = zipfile.ZipInfo(entry.name); info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(info, os.readlink(entry.path).encode()); continue
            # ZIP streams large worlds rather than holding them in memory.
            info = zipfile.ZipInfo(entry.name)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            if entry.path:
                import time
                stamp = time.localtime(entry.path.stat().st_mtime)[:6]
                if 1980 <= stamp[0] <= 2107: info.date_time = stamp
            elif entry.info: info.date_time = entry.info.date_time
            with entry.open() as source, archive.open(info, 'w', force_zip64=True) as target:
                while True:
                    check_cancel(cancel)
                    block = source.read(1024 * 1024)
                    if not block: break
                    target.write(block); done += len(block)
                    if progress: progress(min(done / total, 1), entry.name)

def create_archive(paths, output, kind, cancel=None, progress=None):
    if kind not in EXTENSIONS: raise ValueError('Formato não suportado')
    paths = [Path(os.path.abspath(p)) for p in paths]
    if not paths: raise ValueError('Seleciona pelo menos um ficheiro ou uma pasta.')
    output = Path(os.path.abspath(output))
    if output.exists() or output.is_symlink(): raise FileExistsError('Já existe um arquivo com esse nome. Escolhe outro nome.')
    for source in paths:
        if source.resolve() == output.resolve() or (source.is_dir() and output.resolve().is_relative_to(source.resolve())):
            raise ValueError('Escolhe uma pasta de destino fora da pasta selecionada.')
    check_cancel(cancel)
    with contextlib.ExitStack() as stack:
        # Existing world/pack ZIPs are repacked, not nested inside another ZIP.
        if kind in MINECRAFT and len(paths) == 1 and paths[0].is_file() and zipfile.is_zipfile(paths[0]):
            archive = stack.enter_context(zipfile.ZipFile(paths[0]))
            entries = archive_entries(archive)
        else:
            entries = filesystem_entries(paths, cancel)
        repackaged_addon = kind == 'mcaddon' and len(paths) == 1 and paths[0].is_file() and zipfile.is_zipfile(paths[0])
        if kind == 'mcaddon' and not repackaged_addon:
            # Build selected resource/behavior pack folders into proper inner
            # .mcpack archives, then distribute them together in one addon.
            temp_root = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='apx-addon-')))
            packs = []
            selected = paths
            if len(paths) == 1 and paths[0].is_dir() and not (paths[0] / 'manifest.json').is_file():
                selected = sorted(paths[0].iterdir())
            for index, source in enumerate(selected):
                if source.is_dir():
                    packaged = temp_root / (str(index) + '.mcpack')
                    create_archive([source], packaged, 'mcpack', cancel)
                    packs.append(Entry(source.name + '.mcpack', path=packaged))
                elif source.suffix.lower() in {'.mcpack', '.mcworld'} and zipfile.is_zipfile(source):
                    with zipfile.ZipFile(source) as archive:
                        validate_minecraft(archive_entries(archive), source.suffix[1:].lower())
                    packs.append(Entry(source.name, path=source))
                else:
                    raise ValueError('Um .mcaddon reúne pastas de pacotes Minecraft ou ficheiros .mcpack/.mcworld válidos.')
            entries = packs
        elif kind in MINECRAFT:
            entries = flatten_single_root(entries)
        if kind in MINECRAFT: validate_minecraft(entries, kind)
        if kind == 'mcaddon':
            for entry in entries:
                if entry.is_dir: continue
                with entry.open() as stream, zipfile.ZipFile(stream) as inner:
                    validate_minecraft(archive_entries(inner), Path(entry.name).suffix[1:].lower())
        names = [e.name for e in entries]
        if len(names) != len(set(names)): raise ValueError('Existem itens com o mesmo nome. Comprime-os separadamente ou seleciona a pasta que os contém.')
        fd, temporary = tempfile.mkstemp(prefix='.apx-compress-', suffix='.part', dir=output.parent)
        os.close(fd); temporary = Path(temporary)
        try:
            if kind in {'tar', 'tar.gz', 'tar.xz'}:
                total = sum(e.size for e in entries) or 1; done = 0
                mode = {'tar': 'w', 'tar.gz': 'w:gz', 'tar.xz': 'w:xz'}[kind]
                with tarfile.open(temporary, mode, dereference=False) as archive:
                    for entry in entries:
                        check_cancel(cancel)
                        info = archive.gettarinfo(str(entry.path), arcname=entry.name)
                        if info.isreg():
                            # tarfile.copyfileobj drives reads; check cancel per
                            # block even when one very large file is selected.
                            class Reader:
                                def __init__(self, stream): self.stream = stream
                                def read(self, n):
                                    nonlocal done
                                    check_cancel(cancel)
                                    block = self.stream.read(n); done += len(block)
                                    if progress: progress(min(done / total, 1), entry.name)
                                    return block
                            with entry.path.open('rb') as source: archive.addfile(info, Reader(source))
                        else: archive.addfile(info)
            else: write_zip(entries, temporary, cancel, progress)
            check_cancel(cancel)
            try: os.chmod(temporary, 0o644)
            except PermissionError:
                # FAT bridge ownership is Host-mapped; write access is already
                # granted by the mount even though chmod is unavailable.
                pass
            with temporary.open('rb') as stream: os.fsync(stream.fileno())
            publish_no_replace(temporary, output)
        finally: temporary.unlink(missing_ok=True)
    return output
