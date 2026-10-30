from pathlib import Path
import importlib.machinery
import importlib.util
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load():
    loader=importlib.machinery.SourceFileLoader('camera_activity',str(ROOT/'config/environment-shell-v1/local/bin/apx-microphone-activity-v1'))
    spec=importlib.util.spec_from_loader(loader.name,loader);m=importlib.util.module_from_spec(spec);loader.exec_module(m);return m

class CameraActivity(unittest.TestCase):
    def test_pipewire_camera_but_not_screen_capture(self):
        m=load()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'class/video4linux/video0/device').mkdir(parents=True);proc=root/'proc';proc.mkdir()
            camera=[{'info':{'state':'running','props':{'api.v4l2.path':'/dev/video0'}}}]
            self.assertTrue(m.camera_active(camera,root,proc))
            self.assertFalse(m.camera_active([{'info':{'state':'running','props':{'media.class':'Video/Source','node.name':'screen-cast'}}}],root,proc))
            self.assertFalse(m.camera_active([{'info':None}],root,proc))
    def test_direct_open_fd_only_for_physical_camera(self):
        m=load()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'class/video4linux/video0/device').mkdir(parents=True);proc=root/'proc';(proc/'42/fd').mkdir(parents=True)
            (proc/'42/fd/3').symlink_to('/dev/video99')
            self.assertFalse(m.camera_active([],root,proc))
            (proc/'42/fd/3').unlink();(proc/'42/fd/3').symlink_to('/dev/video0')
            self.assertTrue(m.camera_active([],root,proc))
