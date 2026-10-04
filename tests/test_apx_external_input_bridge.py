import importlib.util
from pathlib import Path
import struct
import unittest
from unittest.mock import patch, Mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bridge',ROOT/'scripts/physical-pilot/apx-external-input-bridge-v1.py')
bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)

class BridgeTests(unittest.TestCase):
    def test_remove_preserves_device_identity_and_fixes_message_length(self):
        properties=b'ACTION=add\0DEVNAME=/dev/input/event11\0SUBSYSTEM=input\0'
        header=bytearray(40);header[:8]=b'libudev\0'
        struct.pack_into('=II',header,16,40,len(properties))
        result=bridge.removal_packet(bytes(header)+properties)
        self.assertIn(b'ACTION=remove\0',result)
        self.assertIn(b'DEVNAME=/dev/input/event11\0',result)
        self.assertEqual(struct.unpack_from('=I',result,20)[0],len(result)-40)
        self.assertEqual(result[:20],header[:20])

    def test_policy_replacement_preserves_graphics_and_revokes_disconnected_hid(self):
        subject=bridge.Bridge.__new__(bridge.Bridge)
        subject.managed={'/dev/input/event11','/dev/input/event12'}
        subject.base_policies={'seat.service':[('/dev/dri/card1','rw'),('/dev/input/event3','rw'),('/dev/input/event11','rw')]}
        with patch.object(subject,'check'),patch.object(bridge,'run') as run:
            subject.update_policies({'/dev/input/event12':(13,1)})
        args=run.call_args.args[0]
        self.assertIn('DeviceAllow=/dev/dri/card1 rw',args)
        self.assertIn('DeviceAllow=/dev/input/event3 rw',args)
        self.assertIn('DeviceAllow=/dev/input/event12 rw',args)
        self.assertNotIn('DeviceAllow=/dev/input/event11 rw',args)
        self.assertIn('DeviceAllow=',args)

    def test_initial_connected_display_is_reconciled_once(self):
        subject=bridge.Bridge.__new__(bridge.Bridge)
        subject.proc=Path('/proc/123')
        subject.seatd='seat.service'
        subject.base_policies={'seat.service':[('/dev/dri/card2','rw')]}
        subject.display_snapshot=None
        subject.display_compositor=None
        subject.snapshot=()
        subject.receiver=Mock()
        subject.receiver.recv.side_effect=BlockingIOError
        status=Mock()
        status.read_text.return_value='connected\n'
        with patch.object(subject,'check'), patch.object(subject,'notify') as notify, \
                patch.object(bridge.Path,'glob',side_effect=lambda pattern: [status] if pattern.endswith('/status') else []):
            subject.refresh()
            notify.assert_called_once_with('/dev/dri/card2','drm','change')
            subject.refresh()
            notify.assert_called_once()
            status.read_text.return_value='disconnected\n'
            subject.refresh()
            self.assertEqual(notify.call_count,2)

    def test_connected_display_is_replayed_after_compositor_starts_and_restarts(self):
        subject=bridge.Bridge.__new__(bridge.Bridge)
        subject.proc=Path('/proc/123')
        subject.seatd='seat.service'
        subject.base_policies={'seat.service':[('/dev/dri/card2','rw')]}
        subject.display_snapshot=(('/sys/class/drm/card2-HDMI-A-1/status','connected'),)
        subject.display_compositor=None
        subject.snapshot=()
        subject.receiver=Mock()
        subject.receiver.recv.side_effect=BlockingIOError
        status=Mock()
        status.read_text.return_value='connected'
        first=Mock()
        first.parent.name='instance-one'
        first.is_socket.return_value=True
        second=Mock()
        second.parent.name='instance-two'
        second.is_socket.return_value=True
        sockets=[first]
        def glob(pattern):
            return sockets if pattern.endswith('/.socket.sock') else ([status] if pattern.endswith('/status') else [])
        with patch.object(subject,'check'), patch.object(subject,'notify') as notify, \
                patch.object(bridge.Path,'glob',side_effect=glob):
            subject.refresh()
            subject.refresh()
            sockets[:]=[]
            subject.refresh()
            sockets[:]=[second]
            subject.refresh()
            self.assertEqual(notify.call_count,2)

    def test_real_hotplug_is_forwarded_without_status_cache_change(self):
        subject=bridge.Bridge.__new__(bridge.Bridge)
        props=b"ACTION=change\0SUBSYSTEM=drm\0HOTPLUG=1\0DEVNAME=/dev/dri/card1\0"
        header=bytearray(40);header[:8]=b"libudev\0"
        struct.pack_into("=II",header,16,40,len(props))
        packet=bytes(header)+props
        subject.receiver=Mock()
        subject.receiver.recv.side_effect=[packet,BlockingIOError()]
        with patch.object(subject,"relay") as relay:
            subject.forward_display_events(["/dev/dri/card1"])
            relay.assert_called_once_with(packet)
        subject.receiver.recv.side_effect=[packet,BlockingIOError()]
        with patch.object(subject,"relay") as relay:
            subject.forward_display_events(["/dev/dri/card2"])
            relay.assert_not_called()

    def test_changed_session_blocks_policy_writes(self):
        subject=bridge.Bridge.__new__(bridge.Bridge)
        with patch.object(subject,'check',side_effect=RuntimeError('changed')),patch.object(bridge,'run') as run:
            with self.assertRaises(RuntimeError):subject.update_policies({})
        run.assert_not_called()

if __name__=='__main__':unittest.main()
