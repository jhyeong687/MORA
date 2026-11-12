#!/usr/bin/env python3
"""Functional mobile pick/place baseline. No learned policy or depth camera.

Navigation uses SLAM; a known-size red cube is aligned with an RGB template.
Simulator object truth is only logged/evaluated, never used to generate targets.
"""
import argparse
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import subprocess
import time
import traceback
import numpy as np
from scipy.optimize import least_squares
from PIL import Image as PILImage
import rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image,CameraInfo
from std_msgs.msg import Float64,String
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from ros_gz_interfaces.msg import Contacts
from run_experiment import Experiment,yaw,wrap
from arm_kinematics import ArmKinematics,ARM_NAMES
from grid_planner import plan_grid

ROOT=Path(__file__).resolve().parent


class MobileTask(Experiment):
    def __init__(self,out):
        super().__init__(out,capture=False,control_frame='map')
        if self.cfg.get('scenario')!='pick_place':raise RuntimeError('Start with start_slam --scenario pick_place')
        self.task=self.cfg['task'];self.kin=ArmKinematics();self.arm_target=np.zeros(6);self.velocity=(0.,0.)
        self.arm_pub=[self.create_publisher(Float64,'/arm/'+n,10) for n in ARM_NAMES]
        self.hold_pose=None
        self.stage_pub=self.create_publisher(String,'/task/stage',10)
        self.timer=self.create_timer(.05,self.publish_targets)
        self.rgb=None;self.info=None;self.eval_object=None;self.object_samples=[];self.arm_samples=[]
        self.contact_events=[];self.contact_last={};self.contact_counts={};self.object_contact_time={};self.events=[];self.ik_records=[];self.last_record=-1e9;self.stage='starting'
        self.subs += [self.create_subscription(Image,'/wrist_cam/image',lambda m:setattr(self,'rgb',m),qos_profile_sensor_data),
            self.create_subscription(CameraInfo,'/wrist_cam/camera_info',lambda m:setattr(self,'info',m),qos_profile_sensor_data),
            self.create_subscription(Odometry,'/evaluation/object_odom',self.object_eval,qos_profile_sensor_data)]
        for finger in ['fixed','moving']:
            self.subs.append(self.create_subscription(Contacts,'/grasp/'+finger+'_contacts',lambda m,f=finger:self.contact(m,f),qos_profile_sensor_data))

    def object_eval(self,m):
        self.eval_object=m
        p=m.pose.pose.position
        self.object_samples.append({'sim_time':m.header.stamp.sec+m.header.stamp.nanosec*1e-9,'stage':self.stage,'xyz':[p.x,p.y,p.z],
            'speed':math.sqrt(sum(getattr(m.twist.twist.linear,a)**2 for a in ['x','y','z']))})

    def contact(self,m,finger):
        if m.contacts:
            if any(self.task['object']['name'] in name for c in m.contacts for name in [c.collision1.name,c.collision2.name]):
                self.object_contact_time[finger]=self.sim()
            self.contact_counts[finger]=self.contact_counts.get(finger,0)+1
            if self.sim()-self.contact_last.get(finger,-1e9)<.05:return
            self.contact_last[finger]=self.sim()
            self.contact_events.append({'sim_time':self.sim(),'stage':self.stage,'finger':finger,
                'pairs':[[c.collision1.name,c.collision2.name] for c in m.contacts]})

    def sim(self):return self.get_clock().now().nanoseconds/1e9

    def joints(self):
        m=self.data['/joint_states'][0];values=dict(zip(m.name,m.position))
        return np.array([values[n] for n in ARM_NAMES])

    def publish_targets(self):
        velocity=self.velocity
        if self.hold_pose is not None:
            try:
                pose=self.control_pose();a=yaw(pose.orientation);dx=self.hold_pose[0]-pose.position.x;dy=self.hold_pose[1]-pose.position.y
                velocity=(np.clip(.8*(dx*math.cos(a)+dy*math.sin(a)),-.025,.025),np.clip(1.5*wrap(self.hold_pose[2]-a),-.12,.12))
            except RuntimeError:velocity=(0.,0.)
        message=Twist();message.linear.x,message.angular.z=map(float,velocity);self.publisher.publish(message)
        for pub,value in zip(self.arm_pub,self.arm_target):pub.publish(Float64(data=float(value)))
        if '/joint_states' in self.data and self.sim()-self.last_record>.099:
            self.last_record=self.sim()
            self.arm_samples.append({'sim_time':self.sim(),'stage':self.stage,'target':self.arm_target.tolist(),'position':self.joints().tolist()})

    def command(self,v=0.,w=0.):self.velocity=(float(v),float(w))

    def wait(self,seconds):
        start=self.sim();deadline=time.monotonic()+max(30,seconds*5)
        while self.sim()-start<seconds:
            if time.monotonic()>deadline:raise RuntimeError('Simulation clock stalled')
            self.spin();self.check_feedback()

    def mark(self,stage,**extra):
        self.stage=stage
        event={'stage':stage,'sim_time':self.sim(),'utc':datetime.now(timezone.utc).isoformat(),**extra}
        self.events.append(event);(self.out/'events.json').write_text(json.dumps(self.events,indent=2))
        self.stage_pub.publish(String(data=json.dumps(event)));print(json.dumps(event),flush=True)
        log=(self.out/'captures.log').open('a')
        subprocess.Popen(['/usr/bin/python3',str(ROOT/'capture_visuals.py'),stage,'--output',str(self.out/'captures'/stage),
            '--note',f'Functional RGB-only mobile manipulation; stage {stage}'],stdout=log,stderr=subprocess.STDOUT);log.close()

    def world_to_map(self,xy):
        sx,sy,a=self.cfg['spawn'];c,s=math.cos(a),math.sin(a)
        return np.array([[c,s],[-s,c]])@(np.array(xy)-[sx,sy])

    def scene_target_in_base(self,world):
        # Scene specification is an explicit prior, not an object-truth topic.
        target=self.world_to_map(world[:2]);pose=self.control_pose();a=yaw(pose.orientation)
        delta=target-[pose.position.x,pose.position.y]
        return np.r_[np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]])@delta,world[2]]

    def navigate(self,world_goal,label):
        self.hold_pose=None
        self.mark(label)
        goal=self.world_to_map(world_goal[:2]);pose=self.control_pose();start=[pose.position.x,pose.position.y]
        rects=[[*self.world_to_map(t['center']),*t['size']] for t in self.task['tables']]
        route=plan_grid(self.map,start,goal,rects,radius=self.task['navigation']['inflation_radius'])
        (self.out/f'{label}_route.json').write_text(json.dumps({'frame':'map','route':route,'source':'SLAM grid + explicit table keepouts'},indent=2))
        for index,point in enumerate(route):
            deadline=time.monotonic()+300;sim_start=self.sim()
            while True:
                self.spin();self.check_feedback();pose=self.control_pose()
                dx,dy=np.array(point)-[pose.position.x,pose.position.y];distance=math.hypot(dx,dy)
                if distance < (.028 if index==len(route)-1 else .045):break
                if time.monotonic()>deadline or self.sim()-sim_start>150:raise RuntimeError('Navigation waypoint timed out')
                error=wrap(math.atan2(dy,dx)-yaw(pose.orientation));v=min(.08,.6*distance) if abs(error)<.25 else 0.
                scan=self.data['/scan'][0]
                front=[r for i,r in enumerate(scan.ranges) if abs(wrap(scan.angle_min+i*scan.angle_increment))<.28 and math.isfinite(r)]
                if v and front and min(front)<.19:raise RuntimeError('Laser obstacle stop before contact')
                self.command(v,np.clip(1.5*error,-.5,.5))
        self.command();self.wait(.5);deadline=time.monotonic()+80
        while True:
            self.spin();self.check_feedback();error=wrap(world_goal[2]-self.cfg['spawn'][2]-yaw(self.control_pose().orientation))
            if abs(error)<.025:break
            if time.monotonic()>deadline:raise RuntimeError('Goal orientation timed out')
            self.command(0,np.clip(1.3*error,-.4,.4))
        self.command();self.wait(1.5)

    def hold_base(self):
        pose=self.control_pose();self.hold_pose=[pose.position.x,pose.position.y,yaw(pose.orientation)]

    def move_arm(self,target,settle=1.0):
        target=np.array(target,dtype=float)
        for name,value in zip(ARM_NAMES,target):
            lo,hi=self.kin.limits[name]
            if not lo<=value<=hi:raise RuntimeError('Requested joint outside model limit: '+name)
        old=self.arm_target.copy();duration=max(1.,float(np.max(np.abs(target-old)))/.22);start=self.sim();deadline=time.monotonic()+duration*5+30
        while self.sim()-start<duration:
            if time.monotonic()>deadline:raise RuntimeError('Arm trajectory timed out')
            self.arm_target=old+(target-old)*min(1.,(self.sim()-start)/duration)
            self.spin();self.check_feedback()
        self.arm_target=target;self.wait(settle)
        error=np.abs(self.joints()[:5]-target[:5])
        if np.max(error)>.12:raise RuntimeError(f'Arm cannot hold requested pose; joint errors {error.tolist()}')

    def move_tcp(self,point,gripper=None):
        result=self.kin.solve(point,seed=self.joints(),tool_axis=np.array([1,0,0]),axis_index=2,
            tcp_offset=self.task['grasp']['cube_center_in_tool'],tool_x=np.array([0,1,0]))
        self.ik_records.append({'stage':self.stage,'target_base_m':list(map(float,point)),**result})
        if result['position_error_m']>.005:raise RuntimeError('Target not reachable by SO-101 model')
        grip=self.arm_target[5] if gripper is None else gripper
        self.move_arm(result['q']+[grip])
        # Remove steady gravity sag using joint feedback, within the original
        # torque and position caps. Simulator object pose is not consulted.
        desired=np.array(result['q'])
        for _ in range(3):
            error=desired-self.joints()[:5]
            if np.max(np.abs(error))<.003:break
            target=self.arm_target.copy()
            for i,name in enumerate(ARM_NAMES[:5]):
                lo,hi=self.kin.limits[name];target[i]=np.clip(target[i]+.8*error[i],lo+.002,hi-.002)
            self.move_arm(target,settle=.7)

    def close_gripper(self):
        start=self.sim();last=start;stable=None;deadline=time.monotonic()+40
        while self.sim()-start<12:
            self.spin();self.check_feedback();now=self.sim()
            self.arm_target[5]=max(self.task['grasp']['close_joint'],
                self.arm_target[5]-self.task['grasp']['closing_speed']*(now-last))
            last=now
            both=all(now-self.object_contact_time.get(f,-1e9)<.10 for f in ['fixed','moving'])
            loaded=self.joints()[5]-self.arm_target[5]>.008
            if both and loaded:
                stable=now if stable is None else stable
                if now-stable>.25:
                    self.arm_target[5]=max(self.task['grasp']['close_joint'],
                        self.joints()[5]-self.task['grasp']['hold_compression_rad'])
                    self.wait(1)
                    if not all(self.sim()-self.object_contact_time.get(f,-1e9)<.15 for f in ['fixed','moving']):
                        raise RuntimeError('Finger contact was lost while establishing grip')
                    self.mark('grip_contact_verified',gripper_target=float(self.arm_target[5]))
                    return
            else:stable=None
            if now-start>8 and abs(self.joints()[5]-self.task['grasp']['close_joint'])<.015:
                raise RuntimeError('Gripper closed freely without trapping the cube')
            if time.monotonic()>deadline:raise RuntimeError('Grasp feedback timed out')
        raise RuntimeError('Could not establish sustained contact on both fingers')

    def rgb_target(self,prior):
        self.wait(.5)
        if self.rgb is None or self.info is None:raise RuntimeError('Missing wrist RGB or CameraInfo')
        msg=self.rgb
        pixels=np.frombuffer(msg.data,dtype=np.uint8).reshape(msg.height,msg.step)[:,:msg.width*3].reshape(msg.height,msg.width,3)
        if msg.encoding=='bgr8':pixels=pixels[:,:,::-1]
        if msg.encoding not in ['rgb8','bgr8']:raise RuntimeError('Unsupported RGB format '+msg.encoding)
        mask=(pixels[:,:,0]>100)&(pixels[:,:,0]>pixels[:,:,1].astype(float)*1.8)&(pixels[:,:,0]>pixels[:,:,2].astype(float)*1.8)
        rows,cols=np.where(mask)
        PILImage.fromarray(pixels).save(self.out/'pickup_rgb.png')
        if len(rows)<15:raise RuntimeError('Known red cube is not visible in wrist RGB')
        observed=np.array([cols.min(),rows.min(),cols.max(),rows.max()],dtype=float)
        visible=np.array([cols.min()>0,rows.min()>0,cols.max()<msg.width-1,rows.max()<msg.height-1])
        cam=self.kin.fk(self.joints())['wrist_camera_optical'];inverse=np.linalg.inv(cam)
        K=np.array(self.info.k).reshape(3,3);size=np.array(self.task['object']['size'])
        corners=np.array([[i,j,k] for i in [-.5,.5] for j in [-.5,.5] for k in [-.5,.5]])*size
        def project(state):
            x,y,a=state;c,s=math.cos(a),math.sin(a);R=np.array([[c,-s,0],[s,c,0],[0,0,1]])
            points=corners@R.T+[x,y,prior[2]];opt=points@inverse[:3,:3].T+inverse[:3,3]
            uv=opt@K.T;uv=uv[:,:2]/uv[:,2:]
            return np.r_[uv.min(0),uv.max(0)]
        result=least_squares(lambda v:(project(v)-observed)[visible],[prior[0],prior[1],0],
            bounds=([.10,-.25,-math.pi/2],[.6,.25,math.pi/2]),max_nfev=100)
        estimate=np.r_[result.x[:2],prior[2]]
        record={'mode':'RGB known-cube bounding-box fit','prior_base_xyz':prior.tolist(),'estimated_base_xyz':estimate.tolist(),
            'bbox_pixels':observed.tolist(),'pixel_fit_rmse':float(np.sqrt(np.mean(result.fun**2))),
            'known_cube_size_m':size.tolist(),'known_table_height':True,'uses_depth_camera':False,'uses_object_truth_for_control':False}
        (self.out/'perception.json').write_text(json.dumps(record,indent=2));print('RGB target',record,flush=True)
        if record['pixel_fit_rmse']>5:raise RuntimeError('RGB cube template does not match observation')
        return estimate

    def perform(self,grasp_only=False):
        self.ready();self.wait(1)
        if grasp_only:
            prior=self.scene_target_in_base(self.task['object']['xyz'])
            if not .1<prior[0]<.45 or abs(prior[1])>.1:
                raise RuntimeError('Grasp-only mode requires spawning in front of the pickup table')
            self.mark('grasp_bench_ready')
        else:
            self.mark('mapping_started')
            self.drive(self.task['mapping_side']);self.mark('mapping_complete')
            self.navigate(self.task['pickup_base_world'],'navigate_pickup')
        self.mark('pickup_rgb_alignment')
        target=self.rgb_target(self.scene_target_in_base(self.task['object']['xyz']))
        # Approach closer using the RGB range if required to stay under the
        # conservative 7.4 V arm torque cap. SLAM still controls navigation.
        if target[0]>.245:
            distance=min(.07,target[0]-.235);pose=self.control_pose();ox,oy=pose.position.x,pose.position.y;a=yaw(pose.orientation)
            start=self.sim()
            while True:
                self.spin();self.check_feedback();p=self.control_pose()
                progress=(p.position.x-ox)*math.cos(a)+(p.position.y-oy)*math.sin(a)
                if progress>=distance:break
                if self.sim()-start>15:raise RuntimeError('Final visual alignment timed out')
                self.command(.025,0)
            self.command();self.wait(1);target=self.rgb_target(self.scene_target_in_base(self.task['object']['xyz']))
        self.hold_base();self.mark('pregrasp',target_base_xyz=target.tolist())
        self.move_tcp([target[0]-.06,target[1],target[2]+.055],self.task['grasp']['open_joint'])
        self.move_tcp([target[0]-.06,target[1],target[2]])
        self.mark('grasp_approach');self.move_tcp(target)
        self.mark('gripper_closing');self.close_gripper()
        self.mark('lifting');self.move_tcp(target+[0,0,self.task['grasp']['lift_distance']]);self.wait(1)
        # Evaluation may abort a failed trial; it never supplies a motion target.
        if self.eval_object is None or self.eval_object.pose.pose.position.z<self.task['object']['xyz'][2]+.05:
            raise RuntimeError('Physical grasp failed: object did not lift from the table')
        # Preserve the already verified lift pose during transfer. Folding into
        # a different elbow branch is unnecessary for this open tabletop task.
        self.mark('lift_verified')
        if grasp_only:
            self.wait(2);self.mark('grasp_bench_complete');return
        self.navigate(self.task['delivery_base_world'],'navigate_delivery')
        self.hold_base()
        self.mark('place_approach');place=self.scene_target_in_base(self.task['delivery_object_world'])
        if place[0]>.245:
            self.hold_pose=None
            distance=min(.08,place[0]-.235);pose=self.control_pose();ox,oy=pose.position.x,pose.position.y;a=yaw(pose.orientation)
            start=self.sim()
            while True:
                self.spin();self.check_feedback();p=self.control_pose()
                progress=(p.position.x-ox)*math.cos(a)+(p.position.y-oy)*math.sin(a)
                if progress>=distance:break
                if self.sim()-start>15:raise RuntimeError('Delivery approach timed out')
                self.command(.025,0)
            self.command();self.wait(1);self.hold_base();place=self.scene_target_in_base(self.task['delivery_object_world'])
        self.move_tcp(place+[0,0,.065]);self.move_tcp(place)
        self.mark('releasing');opening=self.arm_target.copy();opening[5]=self.task['grasp']['open_joint'];self.move_arm(opening,settle=1.5)
        self.move_tcp(place+[-.065,0,.06]);self.wait(2)
        self.mark('complete')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'results'/f'research_{datetime.now():%Y%m%d}'/f'pick_place_{datetime.now():%H%M%S}');parser.add_argument('--grasp-only',action='store_true');args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);rclpy.init();node=MobileTask(args.output)
    completed=False;error=None
    try:node.perform(grasp_only=args.grasp_only);completed=True
    except (Exception,KeyboardInterrupt) as exc:
        error=str(exc) or 'Interrupted';print(error,flush=True);(args.output/'error.txt').write_text(traceback.format_exc())
    finally:
        node.command()
        node.hold_pose=None
        if rclpy.ok():
            node.publish_targets()
        (args.output/'arm_samples.json').write_text(json.dumps(node.arm_samples))
        (args.output/'object_evaluation.json').write_text(json.dumps(node.object_samples))
        (args.output/'finger_contacts.json').write_text(json.dumps(node.contact_events))
        (args.output/'ik_records.json').write_text(json.dumps(node.ik_records,indent=2))
        metrics=node.report(completed,error,driving=False)
        for key in ['baseline_pass','occupied_cell_wall_distance_mean_m','occupied_cells_within_10cm_of_wall_fraction']:
            metrics.pop(key,None)
        final=node.object_samples[-1]['xyz'] if node.object_samples else None
        table=node.task['tables'][1];inside=False
        if final:
            inside=abs(final[0]-table['center'][0])<table['size'][0]/2-.016 and abs(final[1]-table['center'][1])<table['size'][1]/2-.016 and abs(final[2]-(table['top_height']+.016))<.02
        metrics.update({'test_kind':'grasp_bench' if args.grasp_only else 'mobile_pick_place','object_final_xyz':final,'object_on_delivery_table':inside,
            'mission_pass':bool(not args.grasp_only and completed and inside),'functional_pass':bool(completed and (args.grasp_only or inside)),
            'object_pose_used_for_control':False,'depth_camera_used':False,
            'grasp_attachment_used':False,'learned_policy_used':False,'control_rate_hz':20})
        metrics['contact_messages_received']=node.contact_counts
        metrics['contact_recording_max_hz_per_finger']=20
        (args.output/'metrics.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics,indent=2),flush=True)
        node.destroy_node()
        if rclpy.ok():rclpy.shutdown()
    if not metrics['functional_pass']:raise SystemExit(1)


if __name__=='__main__':main()
