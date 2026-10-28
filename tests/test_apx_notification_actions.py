from test_apx_media_progress import helper
import unittest,json,tempfile,sys,types
from pathlib import Path
from unittest.mock import patch,Mock
from types import SimpleNamespace

class NotificationActions(unittest.TestCase):
    def setUp(self):
        self.m=helper()
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.m.NOTIFICATION_STORE=Path(self.tmp.name)/'notifications.json'
        owner=patch.object(self.m,'notification_owner',return_value='bus:owner')
        owner.start();self.addCleanup(owner.stop)
    def test_capabilities_and_history(self):
        active=[dict(id=7,summary='Test',actions={'default':'Abrir'})]
        with patch.object(self.m.subprocess,'run',side_effect=[SimpleNamespace(returncode=0,stdout=json.dumps(active)),SimpleNamespace(returncode=0,stdout=json.dumps(active+[dict(id=8)]))]):
            notes,count=self.m.notifications()
        self.assertEqual(count,2)
        self.assertTrue(next(n for n in notes if n['mako_id']==7)['can_open'])
        self.assertFalse(next(n for n in notes if n['mako_id']==8)['can_open'])
    def test_open_uses_default_action(self):
        with patch.object(self.m,'notifications',return_value=([dict(id=7,active=True,can_open=True)],1)),patch.object(self.m.subprocess,'run',return_value=SimpleNamespace(returncode=0)) as run:
            self.m.notification_action('open','7')
        self.assertEqual(run.call_args.args[0],['/usr/bin/makoctl','invoke','-n','7','default'])
    def test_app_icon_and_desktop_entry_survive_history(self):
        item=dict(id=7,app_name='Example',app_icon='example-icon',desktop_entry='example.desktop',summary='Saved')
        responses=[SimpleNamespace(returncode=0,stdout=json.dumps([item])),SimpleNamespace(returncode=0,stdout='[]')]
        with patch.object(self.m.subprocess,'run',side_effect=responses):
            notes,_=self.m.notifications()
        self.assertEqual(notes[0]['icon'],'example-icon')
        self.assertEqual(notes[0]['desktop_entry'],'example.desktop')
        self.assertTrue(notes[0]['can_open'])
        with patch.object(self.m.subprocess,'run',side_effect=[SimpleNamespace(returncode=0,stdout='[]'),SimpleNamespace(returncode=0,stdout=json.dumps([item]))]):
            notes,_=self.m.notifications()
        self.assertFalse(notes[0]['active'])
        self.assertTrue(notes[0]['can_open'])
    def test_archived_notification_opens_installed_desktop_app(self):
        app=Mock();app.launch.return_value=True
        desktop=Mock();desktop.new.return_value=app
        repository=types.ModuleType('gi.repository');repository.GioUnix=SimpleNamespace(DesktopAppInfo=desktop)
        gi=types.ModuleType('gi');gi.repository=repository
        note=dict(id=7,active=False,can_open=True,default_action=False,desktop_entry='example.desktop')
        with patch.dict(sys.modules,{'gi':gi,'gi.repository':repository}),patch.object(self.m,'notifications',return_value=([note],1)),patch.object(self.m.subprocess,'run') as run:
            self.m.notification_action('open','7')
        desktop.new.assert_called_once_with('example.desktop')
        app.launch.assert_called_once_with([],None)
        run.assert_not_called()
    def test_toast_id_opens_its_exact_notification(self):
        note=dict(id=42,mako_id=7,active=True,can_open=True,default_action=True)
        with patch.object(self.m,'notifications',return_value=([note],1)),patch.object(self.m.subprocess,'run',return_value=SimpleNamespace(returncode=0)) as run:
            self.m.notification_action('open-mako','7')
        self.assertEqual(run.call_args.args[0],['/usr/bin/makoctl','invoke','-n','7','default'])
    def test_old_history_resolves_unique_installed_app(self):
        item=dict(id=7,app_name='Thunderbird',summary='Saved')
        responses=[SimpleNamespace(returncode=0,stdout='[]'),SimpleNamespace(returncode=0,stdout=json.dumps([item]))]
        with patch.object(self.m,'desktop_entries_by_name',return_value={'thunderbird':'org.mozilla.Thunderbird.desktop'}),patch.object(self.m.subprocess,'run',side_effect=responses):
            notes,_=self.m.notifications()
        self.assertEqual(notes[0]['desktop_entry'],'org.mozilla.Thunderbird.desktop')
        self.assertTrue(notes[0]['can_open'])
    def test_temporary_capture_notice_is_not_saved_in_centre(self):
        capture=dict(id=7,app_name='APX Captura',summary='Captura de ecrã')
        with patch.object(self.m.subprocess,'run',side_effect=[SimpleNamespace(returncode=0,stdout=json.dumps([capture])),SimpleNamespace(returncode=0,stdout='[]')]):
            notes,count=self.m.notifications()
        self.assertEqual((notes,count),([],0))
    def test_mark_all_targets_live_and_archived_snapshot(self):
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

    def test_expiry_and_service_restart_keep_unread_history(self):
        item=dict(id=7,summary='Saved test',actions={'default':'Open'})
        responses=[SimpleNamespace(returncode=0,stdout=json.dumps([item])),SimpleNamespace(returncode=0,stdout='[]')]
        with patch.object(self.m.subprocess,'run',side_effect=responses):
            notes,_=self.m.notifications()
        ident=notes[0]['id']
        with patch.object(self.m.subprocess,'run',side_effect=[SimpleNamespace(returncode=0,stdout='[]'),SimpleNamespace(returncode=0,stdout=json.dumps([item]))]):
            notes,count=self.m.notifications()
        self.assertEqual(count,1);self.assertFalse(notes[0]['active']);self.assertEqual(notes[0]['id'],ident)
        with patch.object(self.m,'notification_owner',return_value='new-bus:new-owner'),patch.object(self.m.subprocess,'run',side_effect=responses):
            notes,count=self.m.notifications()
        self.assertEqual(count,2);self.assertNotEqual(notes[0]['id'],ident)
        self.assertEqual(len({n['id'] for n in notes}),2)

    def test_archived_read_does_not_resurrect(self):
        item=dict(id=7,summary='Read test')
        responses=[SimpleNamespace(returncode=0,stdout='[]'),SimpleNamespace(returncode=0,stdout=json.dumps([item]))]
        with patch.object(self.m.subprocess,'run',side_effect=responses):
            notes,_=self.m.notifications()
        ident=notes[0]['id']
        with patch.object(self.m,'notifications',return_value=(notes,1)),patch.object(self.m.subprocess,'run') as run:
            self.m.notification_action('read',str(ident))
            run.assert_not_called()
        with patch.object(self.m.subprocess,'run',side_effect=responses):
            notes,count=self.m.notifications()
        self.assertEqual(count,0);self.assertEqual(notes,[])
        self.assertEqual(self.m.NOTIFICATION_STORE.stat().st_mode & 0o777,0o600)

    def test_group_read_uses_snapshot_and_leaves_other_groups(self):
        notes=[dict(id=1,active=False),dict(id=2,active=False),dict(id=3,active=False)]
        with patch.object(self.m,'notifications',return_value=(notes,3)),patch.object(self.m,'mark_notifications_read') as mark:
            self.m.notification_action('read-group','[1,2]')
        self.assertEqual([call.args[0] for call in mark.call_args_list],[{1},{2}])
        for raw in ('[true]','["1"]','[-1]','[]','{}','not-json'):
            with patch.object(self.m,'notifications',return_value=(notes,3)),patch.object(self.m,'mark_notifications_read') as mark:
                with self.assertRaises(ValueError):self.m.notification_action('read-group',raw)
                mark.assert_not_called()
