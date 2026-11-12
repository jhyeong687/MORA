#!/usr/bin/env python3
"""Identify effective encoder geometry in simulation, on a separate motion set.

Truth is used only in this identification tool. Its result is simulation-only;
neither physical wheel geometry nor command kinematics is changed.
"""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import traceback
import numpy as np
import rclpy
import yaml
from run_carry import CarryTask
from run_experiment import yaw


class Calibration(CarryTask):
    def __init__(self,out):
        self.truth_log=[];self.encoder_log=[];self.phases=[]
        super().__init__(out)

    def receive(self,topic,msg):
        super().receive(topic,msg)
        t=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
        if topic=='/ground_truth/odom':
            p=msg.pose.pose
            self.truth_log.append([t,p.position.x,p.position.y,yaw(p.orientation)])
        elif topic=='/joint_states':
            q=dict(zip(msg.name,msg.position));step=2*math.pi/self.cfg['base']['encoder_counts']
            self.encoder_log.append([t,round(q['axle_left']/step)*step,round(q['axle_right']/step)*step])

    def perform_calibration(self):
        self.ready();self.wait(2)
        for name,v,w,duration in [('forward',.06,0.,8),('reverse',-.06,0.,8),
                                   ('counterclockwise',0.,.35,20),('clockwise',0.,-.35,20)]:
            start=self.sim();self.command(v,w);self.wait(duration);self.command();self.wait(2)
            self.phases.append({'name':name,'start':start,'end':self.sim(),'v':v,'w':w})
            print(json.dumps(self.phases[-1]),flush=True)

    def identify(self):
        truth=np.asarray(self.truth_log);enc=np.asarray(self.encoder_log)
        truth=truth[np.r_[True,np.diff(truth[:,0])>0]]
        enc=enc[np.r_[True,np.diff(enc[:,0])>0]]
        truth[:,3]=np.unwrap(truth[:,3]);records=[]
        for phase in self.phases:
            values=truth[(truth[:,0]>=max(phase['start'],enc[0,0])) &
                         (truth[:,0]<=min(phase['end'],enc[-1,0]))]
            t=values[:,0];angles=(values[:-1,3]+values[1:,3])/2
            ds=float(np.sum(np.diff(values[:,1])*np.cos(angles)+np.diff(values[:,2])*np.sin(angles)))
            q0=np.array([np.interp(t[0],enc[:,0],enc[:,i]) for i in [1,2]])
            q1=np.array([np.interp(t[-1],enc[:,0],enc[:,i]) for i in [1,2]])
            records.append({**phase,'forward_distance_m':ds,'yaw_change_rad':float(values[-1,3]-values[0,3]),
                            'encoder_delta_rad':(q1-q0).tolist()})
        straight=records[:2];turns=records[2:]
        terms=np.array([sum(r['encoder_delta_rad'])/2 for r in straight]);distance=np.array([r['forward_distance_m'] for r in straight])
        radius=float(terms@distance/(terms@terms))
        individual_radii=distance/terms
        separation=np.array([radius*(r['encoder_delta_rad'][1]-r['encoder_delta_rad'][0])/r['yaw_change_rad'] for r in turns])
        if not (.025<radius<.045 and np.all((.13<separation)&(separation<.25))):
            raise RuntimeError('Identified geometry is implausible; inspect raw data')
        if np.ptp(individual_radii)/radius>.02 or np.ptp(separation)/separation.mean()>.05:
            raise RuntimeError('Directional calibration is inconsistent; do not apply')
        result={'kind':'simulation_identification','hardware_calibrated':False,
            'wheel_radius':radius,'wheel_separation':float(separation.mean()),
            'identified_utc':datetime.now(timezone.utc).isoformat(),'source_trial':str(self.out.resolve()),
            'scenario':self.cfg['scenario'],'payload_mass_kg':self.task['payload']['mass'],
            'profile':self.cfg['profile'],'nominal_wheel_radius':self.cfg['base']['wheel_radius'],
            'nominal_wheel_separation':self.cfg['base']['wheel_separation'],
            'tire_friction':self.cfg['base']['tire_friction'],'seed':self.cfg['seed'],
            'radius_forward_reverse_m':individual_radii.tolist(),'separation_ccw_cw_m':separation.tolist(),
            'scope':'Effective encoder odometry for this simulation condition; independent waypoint validation required.'}
        (self.out/'identification.json').write_text(json.dumps({'segments':records,'result':result},indent=2))
        (self.out/'calibration.yaml').write_text(yaml.safe_dump(result,sort_keys=False))
        return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);rclpy.init();node=Calibration(args.output);done=False
    try:
        node.perform_calibration();result=node.identify();done=True;print(json.dumps(result,indent=2),flush=True)
    except (Exception,KeyboardInterrupt):
        (args.output/'error.txt').write_text(traceback.format_exc());traceback.print_exc()
    finally:
        node.command()
        if rclpy.ok():node.publish_targets()
        (args.output/'raw_identification.json').write_text(json.dumps({'truth':node.truth_log,'encoders':node.encoder_log,'phases':node.phases},indent=2))
        (args.output/'configuration.json').write_text(json.dumps(node.cfg,indent=2))
        node.destroy_node()
        if rclpy.ok():rclpy.shutdown()
    if not done:raise SystemExit(1)


if __name__=='__main__':main()
