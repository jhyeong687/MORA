"""macOS: mjpython live.py, Space via custom hotkey P to pause our physics loop."""
from engine import Sim
import mujoco as mj
import mujoco.viewer, numpy as np,time,sys,traceback
from pathlib import Path
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--status',type=Path);parser.add_argument('--begin',type=int,default=0);args=parser.parse_args()
cases=[('01  |  STOWED DRIVE + STOP',dict(mode='drive'),7.),('02  |  STATIONARY ARM REACH',dict(mode='pick'),11.),('03  |  100 g / 3 deg / BRAKING',dict(mode='extbrake',load=.1,slope=3),9.),('04  |  80 mm DROP / TIP TEST',dict(mode='drive',speed=.15,drop=.08),8.)]
sim=Sim();idx=args.begin%len(cases);sim.reset(cases[idx][1]);flags={'pause':False,'next':False,'jump':None}
def key(k):
 if k in (80,112):flags['pause']=not flags['pause']
 if k in (78,110):flags['next']=True
 if 49<=k<=52:flags['jump']=k-49
def status(s):
 if args.status:
  tmp=args.status.with_suffix('.part');tmp.write_text(s);tmp.replace(args.status)
with mujoco.viewer.launch_passive(sim.m,sim.d,key_callback=key,show_left_ui=False,show_right_ui=False) as window:
 with window.lock():
  window.cam.azimuth=130;window.cam.elevation=-17;window.cam.distance=1.04;window.cam.lookat[:]=[0,0,.22]
  window.opt.geomgroup[3]=0
 scan=None;lastscan=-1;start=time.perf_counter()
 while window.is_running():
  start=time.perf_counter()
  with window.lock():
   if sim.d.time>=cases[idx][2] or flags['next'] or flags['jump'] is not None:
    idx=flags['jump'] if flags['jump'] is not None else (idx+1)%len(cases);flags['jump']=None;sim.reset(cases[idx][1]);lastscan=-1;flags['next']=False
   if not flags['pause']:
    for _ in range(10):sim.advance()
   if sim.d.time-lastscan>=.2 or lastscan<0:
    scan=sim.lasers();lastscan=sim.d.time
   ids,dist,dirs=scan;scene=window.user_scn;scene.ngeom=0
   origin=sim.d.site_xpos[sim.m.site('laser_origin').id].copy()
   for j in sorted(set(range(0,360,12)) | set(np.where((dist>0)&(dist<.16))[0][::3].tolist())):
    if dist[j]<=0:continue
    geom=scene.geoms[scene.ngeom];near=dist[j]<.16
    mj.mjv_initGeom(geom,mj.mjtGeom.mjGEOM_LINE,np.zeros(3),np.zeros(3),np.eye(3).flatten(),np.array([.92,.22,.09,.78] if near else [.10,.66,.64,.32]))
    mj.mjv_connector(geom,mj.mjtGeom.mjGEOM_LINE,1.0,origin,origin+dirs[j]*min(dist[j],.42));scene.ngeom+=1
   xy=sim.d.xpos[sim.base,:2];window.cam.lookat[0]=xy[0]+.015;window.cam.lookat[1]=xy[1]
  if hasattr(window,'set_texts'):
   window.set_texts([(mj.mjtFontScale.mjFONTSCALE_150,mj.mjtGridPos.mjGRID_TOPLEFT,cases[idx][0],f't = {sim.d.time:.1f} s   tilt = {sim.tilt():.1f} deg'),(mj.mjtFontScale.mjFONTSCALE_100,mj.mjtGridPos.mjGRID_BOTTOMLEFT,'P: pause   N: next   1-4: jump','Teal: lidar  |  Red: below min range')])
  window.sync()
  status(f'{cases[idx][0]}  {sim.d.time:.3f}  tilt={sim.tilt():.3f}')
  time.sleep(max(0,.020-(time.perf_counter()-start)))
status('closed')
