import importlib.machinery
import importlib.util
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / 'config/environment-shell-v1/local/bin/apx-desktop-activity-v1'
loader = importlib.machinery.SourceFileLoader('apx_desktop_activity_mute', str(SOURCE))
spec = importlib.util.spec_from_loader(loader.name, loader)
activity = importlib.util.module_from_spec(spec)
loader.exec_module(activity)


class NotificationMuteTests(unittest.TestCase):
    def test_app_and_thread_scopes_and_expiration(self):
        one = dict(app='ZapZap', desktop_entry='zapzap.desktop', title='Ana')
        two = dict(app='ZapZap', desktop_entry='zapzap.desktop', title='Bruno')
        store = {'mutes': [{'scope': activity.notification_scope(one, 'thread'), 'until': time.time() + 900}]}
        self.assertTrue(activity.active_mute(store, one))
        self.assertFalse(activity.active_mute(store, two))
        store['mutes'][0]['until'] = time.time() - 1
        self.assertFalse(activity.active_mute(store, one))
        store['mutes'] = [{'scope': activity.notification_scope(one, 'app'), 'until': None}]
        self.assertTrue(activity.active_mute(store, one))
        self.assertTrue(activity.active_mute(store, two))

    def test_thread_requires_identifying_content(self):
        with self.assertRaises(ValueError):
            activity.notification_scope({'app': 'Mail'}, 'thread')

    def test_reactivation_works_without_an_unread_notification(self):
        with TemporaryDirectory() as directory, patch.object(activity, 'NOTIFICATION_STORE', Path(directory) / 'mutes.json'):
            with activity.notification_store() as store:
                store['mutes'].append({'scope': ['thread', 'zapzap', 'ana'], 'label': 'Ana', 'until': None})
            self.assertEqual(len(activity.notification_mutes()), 1)
            activity.unmute_notification_scope('["thread", "zapzap", "ana"]')
            self.assertEqual(activity.notification_mutes(), [])


if __name__ == '__main__':
    unittest.main()
