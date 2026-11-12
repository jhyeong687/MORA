#!/usr/bin/env python3
"""Test SLAM waypoint navigation with an already-held, physically fixed load.

The initial fixed joint is a test fixture, not evidence of successful grasping.
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
import rclpy
from rclpy.qos import QoSProfile,DurabilityPolicy
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist,PoseStamped
from nav_msgs.msg import Path as NavPath
from visualization_msgs.msg import Marker,MarkerArray
from run_experiment import Experiment,yaw,wrap
from grid_planner import plan_grid
from arm_kinematics import ARM_NAMES

ROOT=Path(__file__).resolve().parent


class CarryTask(Experiment):
    def __init__(self,out):
        super().__init__(out,capture=False,control_frame='map')
        if self.cfg.get('scenario')!='carry':raise RuntimeError('Start with start_carry')
        self.task=self.cfg['task'];self.velocity=(0.,0.);self.events=[];self.arrivals=[]
        self.arm_publishers=[self.create_publisher(Float64,'/arm/'+n,10) for n in ARM_NAMES]
        self.timer=self.create_timer(.05,self.publish_targets)
        qos=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.route_pub=self.create_publisher(NavPath,'/carry/planned_path',qos)
        self.marker_pub=self.create_publisher(MarkerArray,'/carry/waypoints',qos)

    def sim(self):return self.get_clock().now().nanoseconds/1e9

    def command(self,v=0.,w=0.):self.velocity=(float(v),float(w))

    def publish_targets(self):
        msg=Twist();msg.linear.x,msg.angular.z=self.velocity;self.publisher.publish(msg)
        for i,pub in enumerate(self.arm_publishers):
            pub.publish(Float64(data=float(self.task['payload']['gripper_joint']) if i==5 else 0.))

    def wait(self,seconds):
        start=self.sim();deadline=time.monotonic()+max(20,seconds*5)
        while self.sim()-start<seconds:
            self.spin();self.check_feedback()
            if time.monotonic()>deadline:raise RuntimeError('Simulation clock stalled')

    def mark(self,stage,**extra):
        self.stage=stage;record={'stage':stage,'sim_time':self.sim(),'utc':datetime.now(timezone.utc).isoformat(),**extra}
        self.events.append(record);(self.out/'events.json').write_text(json.dumps(self.events,indent=2));print(json.dumps(record),flush=True)
        with (self.out/'captures.log').open('a') as log:
            subprocess.Popen(['/usr/bin/python3',str(ROOT/'capture_visuals.py'),stage,'--output',str(self.out/'captures'/stage),
                '--note','Already-held fixed payload; navigation test only, grasp and release not tested.'],stdout=log,stderr=subprocess.STDOUT)

    def world_to_map(self,xy):
        sx,sy,a=self.cfg['spawn'];c,s=math.cos(a),math.sin(a)
        return np.array([[c,s],[-s,c]])@(np.array(xy)-[sx,sy])

    def publish_waypoints(self):
        array=MarkerArray()
        for i,waypoint in enumerate(self.task['waypoints']):
            x,y=self.world_to_map(waypoint['world'][:2]);a=waypoint['world'][2]-self.cfg['spawn'][2]
            marker=Marker();marker.header.frame_id='map';marker.ns='carry_goals';marker.id=i*2;marker.type=Marker.ARROW
            marker.pose.position.x=float(x);marker.pose.position.y=float(y);marker.pose.position.z=.08
            marker.pose.orientation.z=math.sin(a/2);marker.pose.orientation.w=math.cos(a/2)
            marker.scale.x=.20;marker.scale.y=.04;marker.scale.z=.04;marker.color.r=.2;marker.color.g=.8;marker.color.b=1.;marker.color.a=1.
            array.markers.append(marker)
            text=Marker();text.header.frame_id='map';text.ns='carry_goals';text.id=i*2+1;text.type=Marker.TEXT_VIEW_FACING
            text.pose.position.x=float(x);text.pose.position.y=float(y);text.pose.position.z=.28;text.pose.orientation.w=1.
            text.scale.z=.13;text.color.r=1.;text.color.g=1.;text.color.b=1.;text.color.a=1.;text.text=f'{i+1}: {waypoint["name"]}'
            array.markers.append(text)
        self.marker_pub.publish(array)

    def navigate(self,waypoint):
        world=waypoint['world'];name=waypoint['name'];self.mark('navigate_'+name)
        goal=self.world_to_map(world[:2]);pose=self.control_pose();start=[pose.position.x,pose.position.y]
        tables=[[*self.world_to_map(t['center']),*t['size']] for t in self.task['tables']]
        route=plan_grid(self.map,start,goal,tables,radius=self.task['navigation']['inflation_radius'])
        (self.out/(name+'_route.json')).write_text(json.dumps({'frame':'map','route':route,'source':'SLAM occupancy grid and configured table keepouts'},indent=2))
        path=NavPath();path.header.frame_id='map';path.header.stamp=self.get_clock().now().to_msg()
        for x,y in [start]+route:
            p=PoseStamped();p.header=path.header;p.pose.position.x=float(x);p.pose.position.y=float(y);p.pose.orientation.w=1.;path.poses.append(p)
        self.route_pub.publish(path)
        for i,point in enumerate(route):
            sim_start=self.sim();deadline=time.monotonic()+240
            while True:
                self.spin();self.check_feedback();pose=self.control_pose()
                dx,dy=np.array(point)-[pose.position.x,pose.position.y];distance=math.hypot(dx,dy)
                if distance < (self.task['navigation']['map_arrival_tolerance']*.85 if i==len(route)-1 else .045):break
                if self.sim()-sim_start>140 or time.monotonic()>deadline:raise RuntimeError('Waypoint navigation timed out')
                error=wrap(math.atan2(dy,dx)-yaw(pose.orientation))
                speed=min(self.task['navigation']['max_speed'],.6*distance) if abs(error)<.25 else 0.
                scan=self.data['/scan'][0]
                front=[r for j,r in enumerate(scan.ranges) if abs(wrap(scan.angle_min+j*scan.angle_increment))<.28 and math.isfinite(r)]
                if speed and front and min(front)<.19:raise RuntimeError('Laser obstacle stop')
                self.command(speed,float(np.clip(1.5*error,-.5,.5)))
        self.command();self.wait(.5);deadline=time.monotonic()+80
        while True:
            self.spin();self.check_feedback();error=wrap(world[2]-self.cfg['spawn'][2]-yaw(self.control_pose().orientation))
            if abs(error)<.025:break
            if time.monotonic()>deadline:raise RuntimeError('Final waypoint orientation timed out')
            self.command(0,float(np.clip(1.3*error,-.4,.4)))
        self.command();self.wait(2)
        pose=self.control_pose();truth=self.data['/ground_truth/odom'][0].pose.pose
        map_error=float(np.linalg.norm(goal-[pose.position.x,pose.position.y]))
        truth_error=math.hypot(world[0]-truth.position.x,world[1]-truth.position.y)
        heading_error=math.degrees(wrap(world[2]-yaw(truth.orientation)))
        record={'name':name,'goal_world':world,'map_position_error_m':map_error,
            'evaluation_position_error_m':truth_error,'evaluation_heading_error_deg':heading_error,
            'pass':bool(map_error<self.task['navigation']['map_arrival_tolerance'] and
                truth_error<self.task['navigation']['evaluation_position_tolerance'] and
                abs(heading_error)<self.task['navigation']['evaluation_heading_tolerance_deg'])}
        self.arrivals.append(record);(self.out/'waypoint_results.json').write_text(json.dumps(self.arrivals,indent=2))
        self.mark('arrived_'+name,**record)

    def perform(self):
        self.ready();self.wait(1);self.publish_waypoints();self.mark('held_payload_ready')
        self.mark('mapping_started');self.drive(self.task['mapping_side']);self.mark('mapping_complete')
        for waypoint in self.task['waypoints']:self.navigate(waypoint)
        self.mark('carry_navigation_complete')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'results'/f'research_{datetime.now():%Y%m%d}'/f'carry_{datetime.now():%H%M%S}');args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);rclpy.init();node=CarryTask(args.output);done=False;error=None
    try:node.perform();done=True
    except (Exception,KeyboardInterrupt) as exc:
        error=str(exc) or 'Interrupted';(args.output/'error.txt').write_text(traceback.format_exc());print(error,flush=True)
    finally:
        node.command()
        if rclpy.ok():node.publish_targets()
        result=node.report(done,error,driving=False,emit=False)
        for key in ['baseline_pass','occupied_cell_wall_distance_mean_m','occupied_cells_within_10cm_of_wall_fraction']:result.pop(key,None)
        result.update({'test_kind':'already_held_payload_waypoint_navigation','payload_fixed_fixture':True,
            'payload_mass_kg':node.task['payload']['mass'],'simulated_total_mass_kg':node.cfg['imported_mass_kg'],
            'grasp_tested':False,'placement_tested':False,'waypoints':node.arrivals,
            'navigation_pass':bool(done and len(node.arrivals)==len(node.task['waypoints']) and all(r['pass'] for r in node.arrivals))})
        (args.output/'metrics.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
        node.destroy_node()
        if rclpy.ok():rclpy.shutdown()
    if not result['navigation_pass']:raise SystemExit(1)


if __name__=='__main__':main()
