import subprocess,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py')]
def ipc():return json.loads(subprocess.check_output(RUN+['qs','ipc','-c','apx','call','host','popupStatus'],text=True))
p=subprocess.Popen(RUN+['timeout','10','ffplay','-loglevel','error','-f','v4l2','-video_size','640x480','-i','/dev/video0','-an','-window_title','APX camera indicator check','-x','320','-y','240'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
try:
 for i in range(20):
  state=ipc()
  if state['camera_active'] and state['island_transient']:break
  time.sleep(.25)
 assert state['camera_active'],state
 time.sleep(.7)
 state=ipc();rect=state['bar_targets']['media'];print(json.dumps({k:state[k] for k in ['camera_active','fullscreen','island_transient','media_width','media_summary_width','media_summary_x']}))
 for i in range(3):
  subprocess.run(RUN+['grim','-g',f"{int(rect['x'])},{int(rect['y'])} {int(rect['width'])}x{int(rect['height'])}",f'/home/apx/.cache/apx-camera-contour-{i}.png'],check=True)
  time.sleep(.3)
 (Path(__file__).parent/'camera-live.json').write_text(json.dumps(state,indent=2))
finally:
 p.wait(timeout=12)
 print(p.stderr.read())
