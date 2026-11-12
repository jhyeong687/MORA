#!/usr/bin/env python3
"""Read-only base interface preflight for simulation or a real TurtleBot.

No motion publishers, model truth, or calibration parameters are used here.
Run in the same ROS domain/network as the base driver. Hardware is the default.
"""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from rcl_interfaces.srv import GetParameters
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformListener, TransformException


class Audit(Node):
    def __init__(self,args):
        super().__init__('r4_base_audit',parameter_overrides=[rclpy.parameter.Parameter('use_sim_time',value=args.sim)])
        self.args=args;self.records=defaultdict(list);self.frames={};self.tf_ok=defaultdict(int);self.tf_errors={}
        self.buffer=Buffer();self.listener=TransformListener(self.buffer,self);self.pending=[]
        self.subs=[self.create_subscription(typ,topic,lambda m,t=topic:self.receive(t,m),qos_profile_sensor_data)
            for topic,typ in [('/scan',LaserScan),('/scan_raw',LaserScan),('/odom',Odometry)]]
        self.parameter_requests=[];self.started=time.monotonic();self.ignored_parameter_nodes=[]
        self.tf_ready_after=None;self.discovery_scans_skipped=0

    def receive(self,topic,msg):
        stamp=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
        now=self.get_clock().now().nanoseconds/1e9
        self.records[topic].append([stamp,now,time.monotonic()])
        self.frames[topic]={'frame':msg.header.frame_id}
        if topic=='/odom':self.frames[topic]['child_frame']=msg.child_frame_id
        if topic=='/scan':
            self.frames[topic].update({'rays':len(msg.ranges),'range_min':msg.range_min,'range_max':msg.range_max})
            ready=self.buffer.can_transform('odom',msg.header.frame_id,Time())
            if self.args.require_map:ready=ready and self.buffer.can_transform('map',self.args.base_frame,Time())
            if ready and self.tf_ready_after is None:self.tf_ready_after=now+.5
            if self.tf_ready_after is not None and stamp>self.tf_ready_after:
                self.pending.append((msg.header.stamp,msg.header.frame_id,time.monotonic()))
            else:self.discovery_scans_skipped+=1

    def check_transforms(self):
        pending=[]
        for stamp,frame,received in self.pending:
            targets=['odom']+(['map'] if self.args.require_map else [])
            try:
                self.buffer.lookup_transform(self.args.base_frame,frame,Time.from_msg(stamp))
                for target in targets:self.buffer.lookup_transform(target,self.args.base_frame,Time.from_msg(stamp))
                self.tf_ok['scans']+=1
            except TransformException as exc:
                if time.monotonic()-received<.75:pending.append((stamp,frame,received))
                else:self.tf_errors[str(exc).split('\n')[0]]=self.tf_errors.get(str(exc).split('\n')[0],0)+1
        self.pending=pending

    def request_parameters(self):
        for name,namespace in self.get_node_names_and_namespaces():
            if name==self.get_name():continue
            # ROS launch's management node has no sensor timestamps or TF;
            # its wall clock is unrelated to the robot data plane.
            if name.startswith('launch_ros_'):
                self.ignored_parameter_nodes.append(name);continue
            full=namespace.rstrip('/')+'/'+name
            client=self.create_client(GetParameters,full+'/get_parameters')
            if client.service_is_ready():
                future=client.call_async(GetParameters.Request(names=['use_sim_time']))
                self.parameter_requests.append((full,client,future))

    def result(self):
        errors=[];topics={}
        for topic in ['/scan','/odom']:
            rows=np.asarray(self.records[topic])
            if len(rows)<5:errors.append('Missing or insufficient data: '+topic);continue
            dt=np.diff(rows[:,0]);ages=rows[3:,1]-rows[3:,0]
            regressions=int(np.sum(dt<0));duplicates=int(np.sum(dt==0))
            positive=dt[dt>0];hz=1/np.median(positive) if len(positive) else 0.
            topics[topic]={'messages':len(rows),'stamp_hz':float(hz),'timestamp_regressions':regressions,
                'duplicate_stamps':duplicates,'age_p95_s':float(np.percentile(ages,95)),**self.frames[topic]}
            if regressions or duplicates:errors.append(topic+' has non-increasing timestamps')
            if hz<(3 if topic=='/scan' else 10):errors.append(topic+' rate below baseline requirement')
            if np.min(ages)<-.05 or np.percentile(ages,95)>.5:errors.append(topic+' acquisition time and node clock disagree or data is stale')
        if self.frames.get('/odom',{}).get('frame')!='odom':errors.append('/odom parent frame must be odom')
        if self.frames.get('/odom',{}).get('child_frame')!=self.args.base_frame:errors.append('/odom child frame differs from configured base frame')
        if self.tf_ok['scans']<5:errors.append('Cannot resolve sensor/base/odom transforms at scan timestamps')
        if self.tf_errors:errors.append('Scan-time TF failures after discovery warmup')
        raw={round(row[0],6) for row in self.records['/scan_raw']}
        matched=sum(round(row[0],6) in raw for row in self.records['/scan']) if raw else None
        parameters={};mismatches=[]
        for name,client,future in self.parameter_requests:
            if future.done() and not future.exception():
                values=future.result().values
                if values and values[0].type==1:
                    parameters[name]=values[0].bool_value
                    if parameters[name]!=self.args.sim:mismatches.append(name)
        if mismatches:errors.append('use_sim_time mismatch: '+', '.join(mismatches))
        qos={topic:[{'node':e.node_name,'reliability':str(e.qos_profile.reliability)}
                    for e in self.get_publishers_info_by_topic(topic)] for topic in ['/scan','/odom']}
        command_types=sorted({e.topic_type for e in self.get_subscriptions_info_by_topic('/cmd_vel')})
        supported={'geometry_msgs/msg/Twist','geometry_msgs/msg/TwistStamped'}
        if len(command_types)!=1 or command_types[0] not in supported:
            errors.append('/cmd_vel requires one unambiguous Twist or TwistStamped driver input')
        return {'pass':not errors,'read_only':True,'motion_commands_sent':0,'simulation':self.args.sim,
            'base_frame':self.args.base_frame,'map_required':self.args.require_map,'topics':topics,
            'scans_with_exact_timestamp_tf':self.tf_ok['scans'],'tf_errors':self.tf_errors,
            'discovery_scans_skipped':self.discovery_scans_skipped,
            'raw_scan_timestamp_matches':matched,'scan_publisher_qos':qos,'use_sim_time':parameters,
            'cmd_vel_driver_types':command_types,
            'non_data_plane_nodes_excluded':self.ignored_parameter_nodes,'errors':errors,
            'limits':'Interface preflight only. Does not certify physical calibration, stopping distance, payload stability or obstacle avoidance.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--sim',action='store_true')
    parser.add_argument('--require-map',action='store_true');parser.add_argument('--base-frame',default='base_footprint')
    parser.add_argument('--seconds',type=float,default=15);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    rclpy.init();node=Audit(args);start=time.monotonic();requested=False
    try:
        while time.monotonic()-start<args.seconds:
            rclpy.spin_once(node,timeout_sec=.02);node.check_transforms()
            if not requested and time.monotonic()-start>3:node.request_parameters();requested=True
        result=node.result();args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
    finally:
        node.destroy_node()
        if rclpy.ok():rclpy.shutdown()
    if not result['pass']:raise SystemExit(1)


if __name__=='__main__':main()
