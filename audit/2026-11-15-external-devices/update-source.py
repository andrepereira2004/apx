from pathlib import Path
import difflib, subprocess, tempfile
repo=Path(__file__).resolve().parents[2]
build=Path('/var/lib/apx/environments/faculdade/root/var/tmp/thunar-4.20.10/thunar/thunar-shortcuts-model.c')
before=build.read_text()
s=before
needle='static void\nthunar_shortcuts_model_load_line ('
helper='''/* The Host exports removable files through this bridge; no block devices
 * or Environment-local eject operation are exposed. */
static gboolean
thunar_shortcuts_model_is_removable_bridge (GFile *location)
{
  const gchar *path = location != NULL ? g_file_peek_path (location) : NULL;
  return path != NULL && g_str_has_prefix (path, "/media/apx-usb/")
         && path[sizeof ("/media/apx-usb/") - 1] != '\\0';
}



'''
assert s.count(needle)==1
s=s.replace(needle,helper+needle)
needle='  /* append the shortcut to the list */\n  thunar_shortcuts_model_add_shortcut (model, shortcut);'
replacement='''  /* Dynamic bridge bookmarks belong with devices, not personal folders. */
  if (thunar_shortcuts_model_is_removable_bridge (file_path))
    {
      shortcut->group = THUNAR_SHORTCUT_GROUP_DEVICES_MOUNTS;
      g_clear_object (&shortcut->gicon);
      shortcut->gicon = g_themed_icon_new ("drive-removable-media-usb");
    }

'''+needle
assert s.count(needle)==1
s=s.replace(needle,replacement)
needle='      if (shortcut->group == THUNAR_SHORTCUT_GROUP_PLACES_BOOKMARKS)'
s=s.replace(needle,'      if (shortcut->group == THUNAR_SHORTCUT_GROUP_PLACES_BOOKMARKS\n          || thunar_shortcuts_model_is_removable_bridge (shortcut->location))',2)
patch=repo/'patches/thunar-partilha-4.20.10.patch'
oldpatch=patch.read_text(); end=oldpatch.index('--- a/thunar/thunar-shortcuts-model.h')
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'thunar/thunar-shortcuts-model.c'; p.parent.mkdir(); p.write_text(before)
 subprocess.run(['patch','-R','-p1','--batch'],input=oldpatch[:end],text=True,cwd=td,check=True,capture_output=True)
 pristine=p.read_text()
 newdiff=''.join(difflib.unified_diff(pristine.splitlines(True),s.splitlines(True),fromfile='a/thunar/thunar-shortcuts-model.c',tofile='b/thunar/thunar-shortcuts-model.c',n=0))
 patch.write_text(newdiff+oldpatch[end:])
 p.write_text(pristine)
 subprocess.run(['patch','--dry-run','-p1','--batch'],input=newdiff,text=True,cwd=td,check=True)
build.write_text(s)
chooser=repo/'config/environment-shell-v1/local/lib/apx/chooser-places.c'
s=chooser.read_text()
needle='    else if (section == 2) rank = 100;'
assert s.count(needle)==1
s=s.replace(needle,'    else if (uri && g_str_has_prefix(uri, "file:///media/apx-usb/")) rank = 100;\n'+needle)
needle='    if (label) g_object_set(row, "label", label, NULL);'
assert s.count(needle)==1
s=s.replace(needle,'    else if (uri && g_str_has_prefix(uri, "file:///media/apx-usb/")) icon = "drive-removable-media-usb";\n'+needle)
chooser.write_text(s)
print('source and patch updated')
