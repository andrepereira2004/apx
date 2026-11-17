import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

source = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-removable-notifications-v1'
loader = importlib.machinery.SourceFileLoader('usb_notifications', str(source))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)


class DeviceNotifications(unittest.TestCase):
    def test_connection_and_mount_give_one_notification(self):
        tracker = m.NotificationTracker()
        self.assertEqual(tracker.update({}, set(), set()), [])
        self.assertEqual(tracker.update({'u': 'Pen'}, set(), set()), [('Dispositivo ligado', 'Pen')])
        self.assertEqual(tracker.update({'u': 'Pen'}, {'u'}, set()), [])
        self.assertEqual(tracker.update({'u': 'Pen'}, {'u'}, set()), [])
        self.assertEqual(tracker.update({}, set(), set()), [('Dispositivo desligado', 'Pen')])

    def test_safe_remove_and_physical_unplug_are_not_duplicated(self):
        tracker = m.NotificationTracker()
        tracker.update({'u': 'Pen'}, {'u'}, set())
        events = tracker.update({'u': 'Pen'}, set(), {'u'})
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][0], 'Dispositivo removido em segurança')
        self.assertEqual(tracker.update({}, set(), {'u'}), [])
        self.assertEqual(tracker.update({'u': 'Pen'}, {'u'}, set()), [('Dispositivo ligado', 'Pen')])

    def test_restart_does_not_report_existing_devices_as_new(self):
        tracker = m.NotificationTracker()
        self.assertEqual(tracker.update({'u': 'Pen'}, {'u'}, set()), [])
        self.assertEqual(tracker.update({'u': 'Pen'}, {'u'}, set()), [])

    def test_suppressed_native_reappearance_is_not_a_new_connection(self):
        tracker = m.NotificationTracker()
        tracker.update({'u': 'Pen'}, {'u'}, set())
        tracker.update({'u': 'Pen'}, set(), {'u'})
        self.assertEqual(tracker.update({}, set(), {'u'}), [])
        self.assertEqual(tracker.update({'u': 'Pen'}, set(), {'u'}), [])

    def test_safe_marker_after_mount_signal_still_notifies(self):
        tracker = m.NotificationTracker()
        tracker.update({'u': 'Pen'}, {'u'}, set())
        self.assertEqual(tracker.update({'u': 'Pen'}, set(), set()), [])
        events = tracker.update({'u': 'Pen'}, set(), {'u'})
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][0], 'Dispositivo removido em segurança')

    def test_native_volume_change_while_bridge_mounted_is_not_a_disconnect(self):
        tracker = m.NotificationTracker()
        tracker.update({'u': 'Pen'}, {'u'}, set())
        self.assertEqual(tracker.update({}, {'u'}, set()), [])
        self.assertEqual(tracker.update({'u': 'Pen'}, {'u'}, set()), [])
        self.assertEqual(tracker.update({}, {'u'}, set()), [])
        self.assertEqual(tracker.update({}, set(), set()), [('Dispositivo desligado', 'u')])
