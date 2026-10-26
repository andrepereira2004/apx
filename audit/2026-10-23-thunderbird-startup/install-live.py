from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
exec((HERE/'live-client.py').read_text())
script='''let done=arguments[arguments.length-1];(async()=>{
let {AddonManager}=ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs");
let id="{ECFD45DC-CEE2-4784-BEEC-A33713B2288D}";
let addon=await AddonManager.getAddonByID(id);
if(!addon){let file=Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsIFile);file.initWithPath("/home/apx/.cache/apx-thunderbird-startup-addon.xpi");let install=await AddonManager.getInstallForFile(file);await install.install();addon=await AddonManager.getAddonByID(id);}
let w=Services.wm.getMostRecentWindow("mail:3pane"),t=w.document.getElementById("tabmail");
let closed=0;
for(let tab of [...t.tabInfo]){
 if(tab.mode.name!="contentTab")continue;
 let uri=tab.browser?.currentURI;
 if(!uri)continue;
 let host;try{host=uri.host;}catch(e){continue;}
 let path=uri.pathQueryRef;
 if((host=="live.thunderbird.net" && /\\/start(?:[/?]|$)/.test(path)) ||
    ((host=="www.thunderbird.net" || host=="thunderbird.net" || host=="give.thunderbird.net" || host=="donate.thunderbird.net") && /donat|appeal/.test(path))){t.closeTab(tab);closed++;}
}
let a=t.currentAbout3Pane;
let hasSelection=!!(a && a.threadTree.selectedIndex>=0);
if(hasSelection)a.threadTree.dispatchEvent(new a.Event("select"));
setTimeout(()=>done({addon:{id,version:addon.version,active:addon.isActive},startPage:Services.prefs.getBoolPref("mailnews.start_page.enabled"),donations:Services.prefs.getBoolPref("mail.inappnotifications.donation_enabled"),scrollToNew:Services.prefs.getBoolPref("mailnews.scroll_to_new_message"),closedPromotionalTabs:closed,existingSelectionRecorded:hasSelection}),1000);
})().catch(e=>done({error:String(e)}));'''
r=cmd('WebDriver:ExecuteAsyncScript',{'script':script,'args':[]})['value']
assert 'error' not in r,r
assert r['addon']['active'] and not r['startPage'] and not r['donations']
(HERE/'installed-live.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
print('Installation verified; application left open.')
