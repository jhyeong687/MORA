#!/usr/bin/env python3
"""Small independent arm-joint motions; simulator benchmark, not hardware calibration."""
import argparse
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import time
import traceback
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from arm_kinematics import ARM_NAMES,ArmKinematics

ROOT=Path(__file__).resolve().parent


class ArmBench(Node):
    def __init__(self,out):
        super().__init__('r4_arm_bench',parameter_overrides=[rclpy.parameter.Parameter('use_sim_time',value=True)])
        self.out=out;self.kin=ArmKinematics();self.state={};self.state_wall=0;self.truth=None
        self.samples=[];self.target=dict.fromkeys(ARM_NAMES,0.0);self.stage='ready';self.last_publish=-1e9
        self.publishers_arm={n:self.create_publisher(Float64,'/arm/'+n,10) for n in ARM_NAMES}
        self.base=self.create_publisher(Twist,'/cmd_vel',10)
        self.sub=self.create_subscription(JointState,'/joint_states',self.receive,qos_profile_sensor_data)
        self.truth_sub=self.create_subscription(Odometry,'/ground_truth/odom',lambda m:setattr(self,'truth',m),qos_profile_sensor_data)
        self.max_tilt=0.0;self.max_displacement=0.0;self.origin=None

    def receive(self,m):
        self.state={n:(float(p),float(v),float(e)) for n,p,v,e in zip(m.name,m.position,m.velocity,m.effort)}
        self.state_wall=time.monotonic()

    def sim(self):return self.get_clock().now().nanoseconds/1e9

    def tick(self):
        rclpy.spin_once(self,timeout_sec=.02)
        now=self.sim()
        if now-self.last_publish < .05:return
        self.last_publish=now
        self.base.publish(Twist())
        for name,pub in self.publishers_arm.items():pub.publish(Float64(data=float(self.target[name])))
        if not set(ARM_NAMES)<=self.state.keys():return
        if time.monotonic()-self.state_wall>2:raise RuntimeError('Joint feedback stale')
        if self.truth is not None:
            p=self.truth.pose.pose.position;q=self.truth.pose.pose.orientation
            if self.origin is None:self.origin=np.array([p.x,p.y])
            self.max_displacement=max(self.max_displacement,float(np.linalg.norm(np.array([p.x,p.y])-self.origin)))
            self.max_tilt=max(self.max_tilt,math.degrees(math.acos(np.clip(1-2*(q.x*q.x+q.y*q.y),-1,1))))
            if self.max_tilt>10:raise RuntimeError('Base tilt exceeded 10 degrees')
        for name in ARM_NAMES:
            p,v,e=self.state[name];lo,hi=self.kin.limits[name]
            if not math.isfinite(p+v+e) or not lo-.02<=p<=hi+.02:raise RuntimeError('Invalid joint state: '+name)
        self.samples.append({'sim_time':now,'wall_time_utc':datetime.now(timezone.utc).isoformat(),'stage':self.stage,
            'target':dict(self.target),'position':{n:self.state[n][0] for n in ARM_NAMES},
            'velocity':{n:self.state[n][1] for n in ARM_NAMES},'effort':{n:self.state[n][2] for n in ARM_NAMES}})

    def run_phase(self,label,target,ramp=1.5,hold=1.0):
        print(label,flush=True);self.stage=label
        old=dict(self.target);start=self.sim();deadline=time.monotonic()+45
        while self.sim()-start < ramp+hold:
            if time.monotonic()>deadline:raise RuntimeError('Simulation clock stalled')
            blend=min(1,max(0,(self.sim()-start)/ramp))
            self.target={n:old[n]+(target[n]-old[n])*blend for n in ARM_NAMES}
            self.tick()
        self.target=dict(target)
        rows=[s for s in self.samples if s['stage']==label and s['sim_time']>start+ramp+.5]
        return {n:float(np.mean([abs(s['position'][n]-target[n]) for s in rows])) for n in ARM_NAMES} if rows else {}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    rclpy.init();node=ArmBench(args.output);done=False;error=None;checks=[]
    try:
        deadline=time.monotonic()+30
        while not(set(ARM_NAMES)<=node.state.keys() and node.truth is not None and node.sim()>0):
            if time.monotonic()>deadline:raise RuntimeError('Missing simulation joint states or clock')
            node.tick()
        zero=dict.fromkeys(ARM_NAMES,0.0)
        node.run_phase('baseline',zero,hold=1)
        excursions={'shoulder_pan':[.18,-.18],'shoulder_lift':[.18,.32],
            'elbow_flex':[.18,-.18],'wrist_flex':[-.18,-.32],'wrist_roll':[.25,-.25],'gripper':[.30,-.20]}
        for name,targets in excursions.items():
            for index,value in enumerate(targets):
                target=dict(zero);target[name]=value
                errors=node.run_phase(f'{name}_{index+1}_move',target)
                checks.append({'joint':name,'target_rad':value,'hold_mean_abs_error_rad':errors.get(name),
                    'pass':errors.get(name,1e9)<math.radians(3)})
                node.run_phase(f'{name}_{index+1}_return',zero,ramp=1.5,hold=.8)
        done=True
    except (Exception,KeyboardInterrupt) as exc:
        error=str(exc) or 'Interrupted';(args.output/'error.txt').write_text(traceback.format_exc())
    finally:
        if rclpy.ok():
            # Return slowly to the baseline after a completed test. On an error,
            # hold the latest measured angles rather than making a sudden jump.
            if not done:node.target={n:node.state.get(n,(0,0,0))[0] for n in ARM_NAMES}
            node.last_publish=-1e9;node.tick()
        metrics={'completed':done,'error':error,'checks':checks,'small_motion_pass':done and all(c['pass'] for c in checks),
            'max_base_tilt_deg':node.max_tilt,'max_base_translation_m':node.max_displacement,
            'max_motor_effort_nm':{n:max((abs(s['effort'][n]) for s in node.samples),default=0) for n in ARM_NAMES},
            'simulation_only':True,'full_range_verified':False,'grasp_verified':False,'self_collision_verified':False,
            'command_rate_hz':20,'joint_state_samples':len(node.samples)}
        (args.output/'metrics.json').write_text(json.dumps(metrics,indent=2));(args.output/'samples.json').write_text(json.dumps(node.samples))
        print(json.dumps(metrics,indent=2),flush=True);node.destroy_node()
        if rclpy.ok():rclpy.shutdown()
    if not metrics['small_motion_pass']:raise SystemExit(1)


if __name__=='__main__':main()
