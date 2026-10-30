"""Exercise Flatpak export symlinks through the real interactive remover."""
import os
from pathlib import Path
import pty
import select
import tempfile
import time
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-application-remove-v1'


class RemovalTests(unittest.TestCase):
    def run_removal(self, scope, choice, invalid=False):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            prefix = '/var/lib/flatpak' if scope == 'system' else str(base / '.local/share/flatpak')
            exported = prefix + '/exports/share/applications/com.example.App.desktop'
            resolved = prefix + '/app/com.example.App/x86_64/stable/hash/export/share/applications/com.example.App.desktop'
            if invalid:
                resolved = '/outside/application.desktop'
            realpath = base / 'realpath'
            realpath.write_text('#!/bin/bash\nif [[ "$1" == -ms ]]; then printf "%s\\n" "$EXPORT"; else printf "%s\\n" "$RESOLVED"; fi\n')
            flatpak = base / 'flatpak'
            flatpak.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$CALLS"\n')
            realpath.chmod(0o755)
            flatpak.chmod(0o755)
            child, fd = pty.fork()
            if child == 0:
                env = dict(os.environ, HOME=directory, PATH=directory + ':' + os.environ['PATH'],
                           EXPORT=exported, RESOLVED=resolved, CALLS=str(base / 'calls'))
                os.execve('/bin/bash', ['bash', str(SCRIPT), exported], env)
            os.write(fd, (choice + '\n').encode())
            output = b''
            deadline = time.monotonic() + 5
            status = None
            try:
                while time.monotonic() < deadline:
                    if select.select([fd], [], [], .1)[0]:
                        try:
                            chunk = os.read(fd, 65536)
                        except OSError:
                            break
                        if not chunk:
                            break
                        output += chunk
                else:
                    os.kill(child, 9)
                    self.fail('removal prompt timed out')
            finally:
                os.close(fd)
                _, status = os.waitpid(child, 0)
            calls = (base / 'calls').read_text().splitlines() if (base / 'calls').exists() else []
            return os.waitstatus_to_exitcode(status), calls, output.decode()

    def test_system_export_keeps_scope_and_data(self):
        code, calls, _ = self.run_removal('system', '1')
        self.assertEqual((code, calls), (0, ['uninstall', '--system', '--', 'com.example.App']))

    def test_user_export_explicit_delete_data(self):
        code, calls, _ = self.run_removal('user', '2')
        self.assertEqual((code, calls), (0, ['uninstall', '--user', '--delete-data', '--', 'com.example.App']))

    def test_cancel_does_not_uninstall(self):
        code, calls, _ = self.run_removal('system', '0')
        self.assertEqual((code, calls), (0, []))

    def test_export_outside_installation_rejected(self):
        code, calls, _ = self.run_removal('system', '1', invalid=True)
        self.assertEqual((code, calls), (3, []))
