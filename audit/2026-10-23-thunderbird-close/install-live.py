from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
exec((HERE/'live-client.py').read_text())
s.settimeout(20)
r=cmd('WebDriver:ExecuteAsyncScript',{'script':'''let done=arguments[arguments.length-1];(async()=>{
let {AddonManager}=ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs");let id="apx-close-message@apx.local";
let addon=await AddonManager.getAddonByID(id);
if(!addon){let file=Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsIFile);file.initWithPath("/home/apx/.cache/apx-thunderbird-close-addon.xpi");let install=await AddonManager.getInstallForFile(file);await install.install();addon=await AddonManager.getAddonByID(id);}
let a=Services.wm.getMostRecentWindow("mail:3pane").document.getElementById("tabmail").currentAbout3Pane;
let d=a?.document.getElementById("messageBrowser")?.contentDocument;
done({id,version:addon.version,active:addon.isActive,buttonPresent:!!d?.querySelector('[data-extensionid="apx-close-message@apx.local"]'),permissions:addon.userPermissions});
})().catch(e=>done({error:String(e)}));''','args':[]})['value']
assert 'error' not in r and r['active'],r
(HERE/'installed-live.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
# Leave all application windows open while disabling the temporary test listener.
print(js('''let {Marionette}=ChromeUtils.importESModule("chrome://remote/content/components/Marionette.sys.mjs");Services.env.set("MOZ_MARIONETTE", "");setTimeout(()=>Marionette.uninit(),300);return "Temporary listener stopping; Thunderbird remains open.";'''))
