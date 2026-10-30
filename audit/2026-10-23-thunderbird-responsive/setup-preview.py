from pathlib import Path
import os,json,subprocess
REPO=Path(__file__).resolve().parents[2]
p=Path('/var/lib/apx/environments/faculdade/home/apx/.cache/apx-thunderbird-responsive-check')
p.mkdir(mode=0o700);os.chown(p,1000,1000)
prefs={'marionette.port':2829,'mail.provider.suppress_dialog_on_startup':True,'mailnews.start_page.enabled':False,'mail.shell.checkDefaultClient':False,'mail.accountmanager.accounts':'account1','mail.accountmanager.localfoldersserver':'server1','mail.account.account1.server':'server1','mail.server.server1.type':'none','mail.server.server1.name':'APX Preview','mail.server.server1.hostname':'Local Folders','mail.server.server1.userName':'nobody','mail.server.server1.directory':'/home/apx/.cache/apx-thunderbird-responsive-check/Mail/Local Folders','mail.server.server1.directory-rel':'[ProfD]Mail/Local Folders','mail.accountmanager.defaultaccount':'account1','mail.server.server1.check_new_mail':False,'mail.server.server1.login_at_startup':False,'browser.shell.checkDefaultBrowser':False,'mail.pane_config.dynamic':0,'mail.account.account1.identities':'id1','mail.identity.id1.useremail':'preview@example.invalid','mail.identity.id1.fullName':'APX Preview'}
(p/'user.js').write_text(''.join('user_pref('+json.dumps(k)+', '+json.dumps(v)+');\n' for k,v in prefs.items()));os.chown(p/'user.js',1000,1000)
subprocess.run(['python',str(REPO/'scripts/physical-pilot/apply-thunderbird-graphite-20261023.py'),str(p)],check=True)
