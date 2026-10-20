from test_apx_media_progress import helper
import unittest,json
from unittest.mock import patch
from types import SimpleNamespace

class NotificationActions(unittest.TestCase):
    def setUp(self): self.m=helper()
    def test_capabilities_and_history(self):
        active=[dict(id=7,summary='Test',actions={'default':'Abrir'})]
        with patch.object(self.m.subprocess,'run',side_effect=[SimpleNamespace(returncode=0,stdout=json.dumps(active)),SimpleNamespace(returncode=0,stdout=json.dumps(active+[dict(id=8)]))]):
            notes,count=self.m.notifications()
        self.assertEqual(count,1)
        self.assertTrue(notes[0]['can_open'])
        self.assertFalse(notes[1]['can_open'])
    def test_open_uses_default_action(self):
        with patch.object(self.m,'notifications',return_value=([dict(id=7,active=True,can_open=True)],1)),patch.object(self.m.subprocess,'run',return_value=SimpleNamespace(returncode=0)) as run:
            self.m.notification_action('open','7')
        self.assertEqual(run.call_args.args[0],['/usr/bin/makoctl','invoke','-n','7','default'])
    def test_mark_all_targets_snapshot_and_preserves_history(self):
        with patch.object(self.m,'notifications',return_value=([dict(id=7,active=True),dict(id=8,active=False)],1)),patch.object(self.m.subprocess,'run',return_value=SimpleNamespace(returncode=0)) as run:
            self.m.notification_action('read-all')
        self.assertEqual(run.call_count,1)
        self.assertEqual(run.call_args.args[0],['/usr/bin/makoctl','dismiss','-n','7'])
    def test_stale_or_unopenable_never_invokes(self):
        with patch.object(self.m,'notifications',return_value=([dict(id=7,active=True,can_open=False)],1)),patch.object(self.m.subprocess,'run') as run:
            for action,ident in [('open','7'),('read','8'),('read','-1'),('read','7;foo')]:
                with self.assertRaises(ValueError):self.m.notification_action(action,ident)
            run.assert_not_called()
    def test_backend_failure_is_reported(self):
        with patch.object(self.m,'notifications',return_value=([dict(id=7,active=True)],1)),patch.object(self.m.subprocess,'run',return_value=SimpleNamespace(returncode=1)):
            with self.assertRaises(RuntimeError):self.m.notification_action('read','7')
