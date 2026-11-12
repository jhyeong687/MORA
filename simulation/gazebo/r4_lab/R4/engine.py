"""MuJoCo R4 model, bounded motor controller and physical test schedules."""
from pathlib import Path
import copy, math, json
import mujoco as mj
import numpy as np
ROOT=Path(__file__).resolve().parent
ORDER=['shoulder_pan','shoulder_lift','elbow_flex','wrist_flex','wrist_roll','gripper']
STOW=np.deg2rad([-10.2,-94.4,29.8,94.5,84.6,10.5])
PICK=np.deg2rad([0,83.8,-12.7,-.3,-4.2,9.3])
EXTEND=np.deg2rad([0,74,-69,0,0,10.5])
BALLS=['contact_guard_'+str(i)+'_'+str(j) for i in range(2) for j in range(2)]
def ramp(t,a,b,va,vb):
 u=np.clip((t-a)/(b-a),0,1);return va+(vb-va)*u
def ease(t,a,b):
 u=float(np.clip((t-a)/(b-a),0,1));return u*u*(3-2*u)
class Sim:
 def __init__(self,template=None):
  self.m=copy.copy(template) if template is not None else mj.MjModel.from_xml_path(str(ROOT/'r4.xml'))
  m=self.m
  self.motor=np.array([m.actuator('XL430_'+x).id for x in ('left','right')]+[m.actuator('STS3215_'+n).id for n in ORDER])
  self.joints=np.array([m.joint('axle_'+x).id for x in ('left','right')]+[m.joint(n).id for n in ORDER])
  self.qa=m.jnt_qposadr[self.joints];self.da=m.jnt_dofadr[self.joints]
  self.base=m.body('burger').id;self.payload=m.body('gripper_frame_link').id
  self.floor=m.geom('floor').id;self.step=m.geom('step').id;self.deck=m.geom('approach_deck').id;self.cg=m.body_ipos[self.base].copy()
  self.d=mj.MjData(m);self.targets=None
 def reset(self,case):
  self.case=case;m=self.m;d=self.d
  load=case.get('load',0);mass=max(1e-6,load)
  pg=m.geom('test_payload').id;m.geom_rgba[pg,3]=1. if load else 0.;m.geom_contype[pg]=2 if load else 0;m.geom_conaffinity[pg]=1 if load else 0
  m.body_mass[self.payload]=mass;m.body_inertia[self.payload,:]=max(1.e-10,.4*mass*.017**2)
  m.body_ipos[self.base]=self.cg+np.array(case.get('cg_shift',[0,0,0]))*1.02/m.body_mass[self.base]
  incline=np.deg2rad(case.get('slope',0));heading=np.deg2rad(case.get('downhill',0))
  m.opt.gravity[:]=9.81*np.array([np.sin(incline)*np.cos(heading),np.sin(incline)*np.sin(heading),-np.cos(incline)])
  self.gravity=m.opt.gravity.copy()
  m.geom_pos[self.step]=[case.get('step_x',1.2),0,case.get('step_height',0)-.05] if case.get('step_height',0)>0 else [1.2,0,-.101]
  if case.get('step_height',0)>0:m.geom_pos[self.step,0]+=.06
  drop=case.get('drop',0)
  m.geom_pos[self.floor,2]=-drop
  m.geom_pos[self.deck]=[case.get('edge_x',.24)-.8,0,-.04 if drop else -.24]
  if drop:m.geom_pos[self.step,2]=-1.
  for gid in range(m.ngeom):
   n=m.geom(gid).name
   if n.startswith('catch_housing_'):
    m.geom_contype[gid]=2 if case.get('housings',True) else 0
    m.geom_conaffinity[gid]=1 if case.get('housings',True) else 0
  for tag in ('left','right'):m.geom_friction[m.geom('contact_'+tag).id,0]=case.get('mu',.7)
  for n in BALLS:
   g=m.geom(n).id;b=m.geom_bodyid[g];m.body_pos[b,2]=.010+case.get('gap',.0005)
   m.geom_contype[g]=2 if case.get('guards',True) else 0;m.geom_conaffinity[g]=1 if case.get('guards',True) else 0
  m.opt.timestep=case.get('dt',.002)
  mj.mj_setConst(m,d);mj.mj_resetData(m,d)
  d.qpos[self.qa[2:]]=self.goal(0)[0]
  mj.mj_forward(m,d);self.last_cmd=np.zeros(8);self.kp=np.array([15,24,22,14,9,8]);self.kd=np.array([.20,.34,.27,.18,.11,.08])
 def goal(self,t):
  c=self.case;mode=c.get('mode','drive');q=STOW.copy();v=0.;yaw=0.
  if mode=='pick':
   u=ease(t,1,4.6)-ease(t,6.6,10.2);q=STOW+(PICK-STOW)*u;q[-1]-=np.deg2rad(8)*(ease(t,5,5.5)-ease(t,5.8,6.4))
  elif mode in ('extend','extbrake','control'):
   target=np.array(c.get('q',EXTEND));u=ease(t,.8,c.get('extend_end',4.2));q=STOW+(target-STOW)*u
   if mode=='extbrake':
    v=ramp(t,4.7,5.9,0,.18);v*=1-float(np.clip((t-6.5)/c.get('brake_time',.36),0,1))
  elif mode=='turn':
   yaw=ramp(t,.8,1.8,0,c.get('yaw',1.4))*(1-float(np.clip((t-4.5)/.4,0,1)))
   v=c.get('speed',0)*ease(t,.8,1.8)*(1-ease(t,4.5,4.9))
  else:
   speed=c.get('speed',.15);v=ramp(t,.8,1.8,0,speed)*(1-float(np.clip((t-4.2)/c.get('brake_time',1.),0,1)))
  return q,np.array([(v-.08*yaw)/.033,(v+.08*yaw)/.033])
 def advance(self):
  m,d=self.m,self.d;q,w=self.goal(d.time);vel=d.qvel[self.da]
  servo=self.case.get('arm_voltage',12)
  maximum=np.r_[[1.4]*2,[2.942 if servo==12 else 1.912]*6]
  w0=np.r_[[57*2*np.pi/60]*2,[(45 if servo==12 else 52)*2*np.pi/60]*6]
  cmd=np.r_[.32*(w-vel[:2]),self.kp*(q-d.qpos[self.qa[2:]])-self.kd*vel[2:]]
  pos=maximum*np.clip(1-vel/w0,0,1);neg=maximum*np.clip(1+vel/w0,0,1)
  if self.case.get('rated_cap'):
   bound=.981 if servo==12 else .4903;pos[2:]=np.minimum(pos[2:],bound);neg[2:]=np.minimum(neg[2:],bound)
  d.ctrl[self.motor]=np.clip(cmd,-neg,pos);self.last_cmd=d.ctrl[self.motor].copy();self.targets=q
  # Deliberate external torque used only in the positive control.
  if self.case.get('mode')=='control':
   d.xfrc_applied[self.base,4]=self.case.get('pulse_nm',0) if 5.0<=d.time<5.35 else 0.
  mj.mj_step(m,d)
 def lasers(self,n=360):
  m,d=self.m,self.d;sid=m.site('laser_origin').id
  th=np.arange(n)*2*np.pi/n
  dirs=np.c_[np.cos(th),np.sin(th),np.zeros(n)]@d.site_xmat[sid].reshape(3,3).T
  ids=np.full(n,-1,dtype=np.int32);dist=np.full(n,-1.)
  mj.mj_multiRay(m,d,d.site_xpos[sid],np.ascontiguousarray(dirs.ravel()),np.array([1,0,1,0,0,0],dtype=np.uint8),True,-1,ids,dist,None,n,8.0)
  return ids,dist,dirs
 def tilt(self):
  return float(np.rad2deg(np.arccos(np.clip(self.d.xmat[self.base].reshape(3,3)[2,2],-1,1))))
