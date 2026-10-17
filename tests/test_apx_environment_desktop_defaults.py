from pathlib import Path
import sys,tempfile,unittest,subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from apx_environment_desktop_defaults import install_flatpak_defaults

class DesktopDefaultsTests(unittest.TestCase):
    def test_install_is_local_pinned_and_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'root';root.mkdir()
            install_flatpak_defaults(root,ROOT/'config/environment-flatpak-v1')
            install_flatpak_defaults(root,ROOT/'config/environment-flatpak-v1')
            self.assertTrue((root/'usr/local/libexec/apx-flatpak-nesting-v1').stat().st_mode&0o100)
            self.assertEqual((root/'etc/polkit-1/rules.d/49-apx-flatpak-environment.rules').stat().st_mode&0o777,0o644)
            self.assertIn('FLATPAK_DISABLE_REVOKEFS=1',(root/'etc/systemd/system/flatpak-system-helper.service.d/50-apx-no-revokefs.conf').read_text())
            self.assertTrue((root/'etc/systemd/system/multi-user.target.wants/apx-flatpak-nesting-v1.service').is_symlink())

    def test_tampered_seed_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'root';root.mkdir();seed=Path(d)/'seed';seed.mkdir()
            for p in (ROOT/'config/environment-flatpak-v1').iterdir():(seed/p.name).write_bytes(p.read_bytes())
            (seed/'apx-flatpak-nesting-v1').write_text('bad')
            with self.assertRaises(ValueError):install_flatpak_defaults(root,seed)
            self.assertEqual(list(root.iterdir()),[])

    def test_parent_symlink_cannot_write_outside_root(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'root';root.mkdir();outside=Path(d)/'outside';outside.mkdir()
            (root/'usr').symlink_to(outside)
            with self.assertRaises(ValueError):install_flatpak_defaults(root,ROOT/'config/environment-flatpak-v1')
            self.assertEqual(list(outside.iterdir()),[])

    def test_foreign_activation_link_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'root';root.mkdir();p=root/'etc/systemd/system/multi-user.target.wants/apx-flatpak-nesting-v1.service';p.parent.mkdir(parents=True);p.symlink_to('/tmp/foreign')
            with self.assertRaises(ValueError):install_flatpak_defaults(root,ROOT/'config/environment-flatpak-v1')
            self.assertEqual(p.readlink(),Path('/tmp/foreign'))

    def test_rule_only_authorizes_environment_owner_and_selected_flatpak_actions(self):
        rule=(ROOT/'config/environment-flatpak-v1/49-apx-flatpak-environment.rules').read_text()
        harness = """
const callbacks=[];
const polkit={addRule:f=>callbacks.push(f),Result:{YES:'yes',NOT_HANDLED:'unhandled'}};
""" + rule + """
const check=(id,user='apx',wheel=true)=>callbacks[0]({id},{user,isInGroup:g=>wheel&&g==='wheel',active:false,local:false});
const prefix='org.freedesktop.Flatpak.';
for (const action of ['app-install','runtime-install','app-update','runtime-update','app-uninstall','runtime-uninstall','modify-repo','update-remote','appstream-update']) {
 if(check(prefix+action)!=='yes')throw Error(action);
 if(check(prefix+action,'other')!=='unhandled')throw Error('other user');
 if(check(prefix+action,'apx',false)!=='unhandled')throw Error('not wheel');
}
for (const action of ['install-bundle','override-parental-controls','configure','configure-remote','unknown'])
 if(check(prefix+action)!=='unhandled')throw Error(action);
if(check('org.freedesktop.systemd1.manage-units')!=='unhandled')throw Error('unrelated');
"""
        subprocess.run(['node','-e',harness],check=True,capture_output=True,text=True)
