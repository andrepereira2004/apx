import importlib.machinery
import importlib.util
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('face_state', str(ROOT/'config/environment-shell-v1/local/bin/apx-face-auth-state-v1'))
spec = importlib.util.spec_from_loader(loader.name, loader)
state = importlib.util.module_from_spec(spec)
loader.exec_module(state)

class FaceStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.proc = self.root/'proc'; self.proc.mkdir()
        self.runtime = self.root/'run'; self.runtime.mkdir()
        self.add_process(10, 1, 'hyprlock', 100)
        self.add_process(20, 10, 'python', 200, [state.COMPARE])
        self.lock = state.process(10, self.proc)

    def add_process(self, pid, parent, comm, start, args=()):
        p = self.proc/str(pid); p.mkdir(exist_ok=True)
        fields = ['S', str(parent)] + ['0']*17 + [str(start)]
        (p/'stat').write_text(f'{pid} ({comm}) '+ ' '.join(fields))
        (p/'comm').write_text(comm)
        (p/'cmdline').write_bytes(b'\0'.join(x.encode() for x in args))

    def marker(self, pid=20, start=200, age=0):
        p = self.runtime/f'apx-howdy-camera-{pid}-{start}.active'
        p.touch(mode=0o600); os.chmod(p, 0o600)
        os.utime(p, (time.time()-age, time.time()-age)); return p

    def read(self):
        return state.capture_state(self.lock, self.runtime, self.proc)

    def test_prepare_is_not_capture(self): self.assertEqual(self.read(), 'preparing')
    def test_fresh_frames_are_capture(self):
        self.marker(); self.assertEqual(self.read(), 'capturing')
    def test_stalled_camera_is_not_still_capturing(self):
        self.marker(age=5); self.assertEqual(self.read(), 'waiting_frame')
    def test_pid_reuse_rejects_marker(self):
        self.marker(start=199); self.assertEqual(self.read(), 'preparing')
    def test_terminal_auth_cannot_drive_lock_status(self):
        self.add_process(20, 1, 'python', 200, [state.COMPARE])
        self.marker(); self.assertEqual(self.read(), 'ready')
    def test_other_lock_is_not_this_lock(self):
        self.add_process(30, 1, 'hyprlock', 300)
        self.add_process(20, 30, 'python', 200, [state.COMPARE])
        self.marker(); self.assertEqual(self.read(), 'ready')
    def test_dead_process_marker_cannot_report_capture(self):
        (self.proc/'20/cmdline').unlink(); self.marker()
        self.assertEqual(self.read(), 'ready')
    def test_symlink_marker_is_ignored(self):
        target = self.runtime/'foreign'; target.touch()
        (self.runtime/'apx-howdy-camera-20-200.active').symlink_to(target)
        self.assertEqual(self.read(), 'preparing')
    def test_process_name_with_parentheses_parses(self):
        self.add_process(22, 10, 'worker (camera)', 800)
        self.assertEqual(state.process(22, self.proc)['start'], 800)
        self.assertEqual(state.lock_ancestor(22, self.proc)['pid'], 10)
    def test_missing_backend_is_password_only(self):
        self.assertFalse(state.face_available(self.root))
    def test_idle_message_does_not_infer_failure(self):
        self.assertNotIn('falh', state.message('ready').lower())
        self.assertNotIn('reconhecido', state.message('capturing'))

class MarkerHeartbeatTests(unittest.TestCase):
    def test_heartbeat_is_best_effort_and_rate_limited(self):
        # Extract the actual patched function source from added/context diff lines.
        patch_text = (ROOT/'config/howdy-v1/howdy-apx/apx-camera-frame-state.patch').read_text()
        code = '\n'.join(line[1:] for line in patch_text.splitlines() if line.startswith('+') and not line.startswith('+++'))
        start = code.index('camera_state_path = None')
        end = code.index('atexit.register')
        import atexit
        scope = dict(os=os, time=time)
        exec(code[start:end], scope)
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, XDG_RUNTIME_DIR=directory):
            scope['publish_camera_frame_state']()
            p = Path(scope['camera_state_path']); self.assertTrue(p.exists())
            with patch.object(os, 'utime') as update:
                scope['publish_camera_frame_state'](); update.assert_not_called()
                scope['camera_state_last_update'] -= 1
                scope['publish_camera_frame_state'](); update.assert_called_once()
            scope['camera_state_last_update'] -= 1
            with patch.object(os, 'utime', side_effect=OSError('unavailable')):
                scope['publish_camera_frame_state']()  # UI cannot fail authentication.
            scope['clear_camera_frame_state'](); self.assertFalse(p.exists())
