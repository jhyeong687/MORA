from engine import *
from test_cases import variants
import argparse, csv,time
P=ROOT/'results';P.mkdir(exist_ok=True)
def savecsv(path,rows):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
def longest(a,period):
 count=peak=0
 for v in a:
  count=(count+1) if v else 0;peak=max(count,peak)
 return round(peak*period,3)
def simulate(template,raw,traces=False):
 c=raw.copy()
 if 'q_deg' in c:c['q']=np.deg2rad(c['q_deg'])
 s=Sim(template);s.reset(c);m,d=s.m,s.d;dt=m.opt.timestep;stepcount=int(round(c['duration']/dt));period=.010;stride=int(round(period/dt))
 contacts=[m.geom(n).id for n in ['contact_left','contact_right','contact_rear_caster']+BALLS];lookup={g:i for i,g in enumerate(contacts)};env={s.floor,s.step,s.deck};force6=np.zeros(6)
 log=[];positions=[];all_torque=[];pose_sample=.04;warn0=np.array([v.number for v in d.warning])
 for i in range(stepcount):
  s.advance()
  if (i+1)%stride:continue
  forces=np.zeros(7);edge=False;other=0.;step_n=0.
  for j in range(d.ncon):
   ct=d.contact[j];ga,gb=map(int,ct.geom)
   if ga not in env and gb not in env:continue
   obj=gb if ga in env else ga
   mj.mj_contactForce(m,d,j,force6);normal=max(0.,force6[0])
   if obj in lookup: forces[lookup[obj]]+=normal
   else:other+=normal
   if s.step in (ga,gb):step_n+=normal
  mat=d.xmat[s.base].reshape(3,3);wheelgap=[]
  for jj in range(2):
   # Shortest distance to any terrain surface. This also works at cliffs and vertical step faces.
   gd=min(mj.mj_geomDistance(m,d,contacts[jj],g,.30,None) for g in env)
   wheelgap.append(gd*1000)
  tcp=mat.T@(d.site_xpos[m.site('tcp').id]-d.xpos[s.base]);speed=np.linalg.norm(d.qvel[:2]);err=np.abs(np.rad2deg(s.targets-d.qpos[s.qa[2:]]))
  log.append(dict(t=round(float(d.time),3),tilt=s.tilt(),x=float(d.qpos[0]),y=float(d.qpos[1]),speed=speed,yaw=float(np.rad2deg(np.arctan2(mat[1,0],mat[0,0]))),L=forces[0],R=forces[1],rear=forces[2],LF_gap=wheelgap[0],RF_gap=wheelgap[1],aux=sum(forces[3:]),other=other,step_force=step_n,tcp_x=tcp[0],tcp_z=tcp[2],arm_err=max(err),shoulder_tau=abs(s.last_cmd[3]),max_arm_tau=max(abs(s.last_cmd[2:])),max_wheel_tau=max(abs(s.last_cmd[:2])),com_x=d.subtree_com[s.base,0],com_y=d.subtree_com[s.base,1],com_z=d.subtree_com[s.base,2]))
  if traces and (i+1)%int(round(pose_sample/dt))==0:positions.append(d.qpos.copy())
 if not np.isfinite(d.qpos).all() or any(v.number>old for v,old in zip(d.warning,warn0)):raise AssertionError((raw,d.warning))
 # First 0.5 s is contact/servo settling. Positive control separately identified.
 settled=[t for t in log if t['t']>=.5];v=lambda f:np.array([row[f] for row in settled]);tilt=v('tilt')
 top=float(max(tilt));g_hit=longest(v('aux')>.25,period)
 lift=longest((v('L')<.1)|(v('R')<.1),period)
 rise=longest(((v('L')<.1)&(v('LF_gap')>1))|((v('R')<.1)&(v('RF_gap')>1)),period)
 intended=c.get('mode','drive')
 atrest=next(r for r in log if r['t']>=.70)
 stop=6.5 if intended=='extbrake' else 4.2 if intended=='drive' else None
 def sample(t):return min(log,key=lambda r:abs(r['t']-t))
 vpre=sample(stop-.04)['speed'] if stop else 0
 after=[r for r in log if stop and r['t']>=stop and r['speed']<.01]
 brakeDist=math.hypot(after[0]['x']-sample(stop)['x'],after[0]['y']-sample(stop)['y']) if after else None
 row=dict(case=c['id'],test_type=('control' if c['id']=='positive_control' or 'positive_control' in c['id'] else 'numerical' if 'convergence' in c['id'] else 'operating'),peak_deg=round(top,3),end_deg=round(tilt[-1],3),over45_time_s=longest(tilt>=45,period),tip45=bool(any(tilt>=45)),drive_wheel_unloaded_s=lift,drive_wheel_lift_s=rise,max_drive_wheel_gap_mm=round(max(v('LF_gap').max(),v('RF_gap').max()),3),guard_engaged_s=g_hit,peak_guard_load_N=round(v('aux').max(),2),rear_unloaded_s=longest(v('rear')<.1,period),structure_bearing_s=longest(v('other')>.5,period),step_contact_s=longest(v('step_force')>.25,period),peak_speed_m_s=round(v('speed').max(),4),net_x_m=round(float(d.qpos[0]),4),peak_yaw_deg=round(max(abs(v('yaw'))),1),prebrake_m_s=round(vpre,4),brake_distance_mm=round(brakeDist*1000,1) if brakeDist is not None and vpre>.02 else '',max_arm_nm=round(v('max_arm_tau').max(),3),max_wheel_nm=round(v('max_wheel_tau').max(),3),shoulder_over_rated_s=longest(v('shoulder_tau')>(.981 if c.get('arm_voltage',12)==12 else .4903),period),max_error_deg=round(v('arm_err').max(),2),max_tcp_x_mm=round(v('tcp_x').max()*1000,1),min_tcp_z_mm=round(v('tcp_z').min()*1000,1),settled_normal_N=round(atrest['L']+atrest['R']+atrest['rear']+atrest['aux']+atrest['other'],2),robot_mass_kg=round(m.body_subtreemass[s.base],4))
 if traces:
  savecsv(P/(c['id']+'_trace.csv'),log);np.savez_compressed(P/(c['id']+'_poses.npz'),qpos=np.array(positions),period=pose_sample)
 return row
if __name__=='__main__':
 template=mj.MjModel.from_xml_path(str(ROOT/'r4.xml'));rows=[]
 for c in variants():
  row=simulate(template,c,traces=not c['id'].startswith(('sweep','servo','front_ball','convergence')));rows.append(row)
  print(c['id'],row['peak_deg'],row['end_deg'],row['drive_wheel_lift_s'],row['guard_engaged_s'],row['max_arm_nm'],flush=True)
 savecsv(P/'scenarios.csv',rows);(P/'cases.json').write_text(json.dumps(list(variants()),indent=2))
