"""Enable desktop activation requests in independent graphical configurations."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
def transform(text):
 if 'focus_on_activate = true' in text:return text
 if 'focus_on_activate' in text:raise RuntimeError('Existing activation preference requires inspection')
 anchor='    misc = {\n'
 if text.count(anchor)!=1:raise RuntimeError('Ambiguous misc configuration')
 return text.replace(anchor,anchor+'        focus_on_activate = true,\n',1)
if __name__=='__main__':
 source=ROOT/'config/environment-shell-v1/hypr/hyprland.lua'
 source.write_text(transform(source.read_text()))
 spec=importlib.util.spec_from_file_location('deploy_menu',ROOT/'scripts/physical-pilot/deploy-menu-icons-20261018.py')
 deploy=importlib.util.module_from_spec(spec);spec.loader.exec_module(deploy)
 deploy.module.TRANSFORMS['hypr/hyprland.lua']=transform
 deploy.RELATIVES.append('hypr/hyprland.lua')
 deploy.main()
