#!/usr/bin/env python3
"""Drive an encoder-controlled loop, independently compare SLAM to simulator truth."""
import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import subprocess
import time
import traceback
import numpy as np
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, qos_profile_sensor_data
from rclpy.time import Time
from geometry_msgs.msg import Pose, PoseStamped, Twist
from nav_msgs.msg import OccupancyGrid, Odometry, Path as NavPath
from sensor_msgs.msg import JointState, LaserScan
from tf2_ros import Buffer, TransformListener, TransformException

ROOT = Path(__file__).resolve().parent


def yaw(q):
    return math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


class Experiment(Node):
    def __init__(self, out, capture=False, control_frame='odom'):
        super().__init__('r4_experiment', parameter_overrides=[rclpy.parameter.Parameter('use_sim_time', value=True)])
        self.out = out
        self.capture_enabled = capture
        self.control_frame = control_frame
        self.next_capture = time.monotonic()+20
        self.capture_jobs = []
        self.stage = 'initializing'
        self.cfg = json.loads((ROOT/'generated/resolved.json').read_text())
        self.data = {}
        self.samples = []
        self.max_torque = {}
        self.max_tilt = 0.0
        self.map = None
        self.scan_count = 0
        self.raw_scans = []
        self.start_sim = None
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.path_pub = self.create_publisher(NavPath, '/experiment/slam_path', 10)
        self.path = NavPath()
        self.path.header.frame_id = 'map'
        self.buffer = Buffer(cache_time=Duration(seconds=30))
        self.listener = TransformListener(self.buffer, self)
        self.subs = []
        for topic, typ in [('/odom', Odometry), ('/ground_truth/odom', Odometry),
                           ('/scan', LaserScan), ('/joint_states', JointState), ('/scan_raw', LaserScan)]:
            self.subs.append(self.create_subscription(typ, topic, lambda msg, t=topic: self.receive(t, msg), qos_profile_sensor_data))
        self.subs.append(self.create_subscription(OccupancyGrid, '/map', self.receive_map,
            QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)))

    def receive_map(self, msg):
        self.map = msg

    def receive(self, topic, msg):
        self.data[topic] = (msg, time.monotonic())
        if topic == '/scan':
            self.scan_count += 1
        if topic == '/scan_raw' and len(self.raw_scans) < 100:
            self.raw_scans.append({'time': msg.header.stamp.sec + msg.header.stamp.nanosec*1e-9,
                'frame': msg.header.frame_id, 'angle_min': msg.angle_min,
                'angle_increment': msg.angle_increment, 'range_min': msg.range_min,
                'range_max': msg.range_max,
                'ranges': [float(r) if math.isfinite(r) else None for r in msg.ranges]})
        if topic == '/joint_states':
            for name, value in zip(msg.name, msg.effort):
                self.max_torque[name] = max(self.max_torque.get(name, 0), abs(value))
        if topic == '/ground_truth/odom':
            q = msg.pose.pose.orientation
            self.max_tilt = max(self.max_tilt, math.acos(max(-1, min(1, 1-2*(q.x*q.x+q.y*q.y)))))

    def command(self, v=0.0, w=0.0):
        msg = Twist()
        msg.linear.x, msg.angular.z = float(v), float(w)
        self.publisher.publish(msg)

    def sample(self):
        if '/ground_truth/odom' not in self.data or '/odom' not in self.data:
            return
        try:
            # Use the timestamp of truth, rather than pairing latest transforms
            # with a moving robot at a different time.
            truth = self.data['/ground_truth/odom'][0]
            tf = self.buffer.lookup_transform('map', 'base_footprint', Time.from_msg(truth.header.stamp))
        except TransformException:
            return
        p, q = truth.pose.pose.position, truth.pose.pose.orientation
        t = tf.transform.translation
        stamp = truth.header.stamp.sec+truth.header.stamp.nanosec*1e-9
        if self.samples and stamp <= self.samples[-1]['time']+.09:
            return
        odom = self.data['/odom'][0].pose.pose
        self.samples.append({'time': stamp, 'truth':[p.x,p.y,yaw(q)],
                             'slam':[t.x,t.y,yaw(tf.transform.rotation)],
                             'odom':[odom.position.x,odom.position.y,yaw(odom.orientation)]})
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = truth.header.stamp
        pose.pose.position.x, pose.pose.position.y = t.x, t.y
        pose.pose.orientation = tf.transform.rotation
        self.path.poses.append(pose)
        self.path.header.stamp = truth.header.stamp
        self.path_pub.publish(self.path)

    def spin(self):
        rclpy.spin_once(self, timeout_sec=.02)
        self.sample()
        if self.capture_enabled and time.monotonic() >= self.next_capture:
            self.capture(self.stage)
            self.next_capture = time.monotonic()+20

    def capture(self, label):
        if not self.capture_enabled:
            return
        destination = self.out/'captures'/f'{datetime.now():%Y%m%d_%H%M%S}_{label}'
        log = (self.out/'captures.log').open('a')
        self.capture_jobs.append(subprocess.Popen(['/usr/bin/python3', str(ROOT/'capture_visuals.py'),
            label, '--output', str(destination), '--note', f'Experiment {self.out.name}; stage {label}'],
            stdout=log, stderr=subprocess.STDOUT))
        log.close()

    def check_feedback(self):
        now = time.monotonic()
        if any(now-self.data[t][1] > 3 for t in ('/scan', '/odom', '/joint_states', '/ground_truth/odom')):
            raise RuntimeError('A required feedback topic stopped.')
        if self.max_tilt > math.radians(15):
            raise RuntimeError('Robot tilt exceeded 15 degrees.')

    def ready(self):
        deadline = time.monotonic()+90
        while time.monotonic() < deadline:
            self.spin()
            if {'/odom', '/ground_truth/odom', '/scan', '/joint_states'} <= self.data.keys() and self.map is not None and len(self.samples) >= 5:
                names = set(self.data['/joint_states'][0].name)
                if set(self.cfg['resolved_motors']) <= names:
                    return
        raise RuntimeError('Missing clock / scan / odom / motor states / map / TF; inspect launch output.')

    def drive(self, length):
        current = self.control_pose()
        ox, oy, a0 = current.position.x, current.position.y, yaw(current.orientation)
        c, s = math.cos(a0), math.sin(a0)
        points = [(length,0), (length,length), (0,length), (0,0)]
        deadline = time.monotonic()+600
        sim_start = self.get_clock().now().nanoseconds/1e9
        for index, (gx, gy) in enumerate(points):
            self.stage = f'waypoint_{index+1}'
            self.capture(self.stage)
            target_x, target_y = ox+c*gx-s*gy, oy+s*gx+c*gy
            print(f'Waypoint {index+1}/4: {self.control_frame} ({target_x:.2f}, {target_y:.2f})', flush=True)
            while True:
                self.spin()
                now = time.monotonic()
                if now > deadline or self.get_clock().now().nanoseconds/1e9-sim_start > 240:
                    raise RuntimeError('Loop timed out; robot may be blocked or unstable.')
                self.check_feedback()
                pose = self.control_pose()
                dx, dy = target_x-pose.position.x, target_y-pose.position.y
                distance = math.hypot(dx,dy)
                if distance < .045:
                    break
                error = wrap(math.atan2(dy,dx)-yaw(pose.orientation))
                forward = min(.12, .7*distance) if abs(error) < .30 else 0.0
                scan = self.data['/scan'][0]
                front = [r for i,r in enumerate(scan.ranges)
                         if abs(wrap(scan.angle_min+i*scan.angle_increment)) < .35 and math.isfinite(r)]
                if forward and front and min(front) < .28:
                    raise RuntimeError('Obstacle within 0.28m; stopped before collision.')
                self.command(forward, max(-.60,min(.60,1.6*error)))
        # Restore heading so the final scan can match the initial view.
        turn_deadline = time.monotonic()+60
        self.stage = 'restore_heading'
        while time.monotonic() < turn_deadline:
            self.spin()
            self.check_feedback()
            error = wrap(a0-yaw(self.control_pose().orientation))
            if abs(error) < .03:
                break
            self.command(0, max(-.5,min(.5,1.5*error)))
        else:
            raise RuntimeError('Final heading restoration timed out.')
        self.command()
        stop = self.get_clock().now().nanoseconds/1e9+5
        while self.get_clock().now().nanoseconds/1e9 < stop:
            self.command()
            self.spin()
            self.check_feedback()

    def control_pose(self):
        if self.control_frame == 'odom':
            return self.data['/odom'][0].pose.pose
        try:
            tf = self.buffer.lookup_transform('map', 'base_footprint', Time())
        except TransformException as exc:
            raise RuntimeError(f'SLAM feedback unavailable: {exc}') from exc
        age = (self.get_clock().now()-Time.from_msg(tf.header.stamp)).nanoseconds/1e9
        if age > 1.0:
            raise RuntimeError(f'SLAM feedback is stale ({age:.2f} simulation seconds).')
        pose = Pose()
        pose.position.x = tf.transform.translation.x
        pose.position.y = tf.transform.translation.y
        pose.position.z = tf.transform.translation.z
        pose.orientation = tf.transform.rotation
        return pose

    def report(self, completed, error, driving=False, side=None, emit=True):
        result = {'completed':completed, 'error':error, 'profile':self.cfg['profile'],
                  'test_kind':'square_loop' if driving else 'stationary_observation',
                  'requested_side_m': side if driving else None, 'acceptance_version': 2,
                  'controller_feedback_frame': self.control_frame,
                  'scan_messages':self.scan_count, 'trajectory_samples':len(self.samples),
                  'max_tilt_deg':math.degrees(self.max_tilt), 'max_motor_effort_nm':self.max_torque,
                  'hardware_calibrated':False, 'loop_closure_event_verified':False}
        (self.out/'trajectory.json').write_text(json.dumps(self.samples,indent=2))
        (self.out/'configuration.json').write_text(json.dumps(self.cfg,indent=2))
        (self.out/'raw_scans.json').write_text(json.dumps(self.raw_scans, indent=2))
        if self.raw_scans:
            values = np.array([[np.nan if r is None else r for r in s['ranges']] for s in self.raw_scans])
            print('Raw lidar:', json.dumps({'scans': len(values), 'rays': values.shape[1],
                'valid_fraction': float(np.mean(np.isfinite(values))),
                'min_range_fraction': float(np.mean(values <= self.raw_scans[0]['range_min']+.015)),
                'ranges_first_scan': self.raw_scans[0]['ranges'][::15]}), flush=True)
        if len(self.samples) > 1:
            truth = np.array([s['truth'] for s in self.samples])
            slam = np.array([s['slam'] for s in self.samples])
            angle = truth[0,2]-slam[0,2]
            rotation = np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
            aligned = (slam[:,:2]-slam[0,:2])@rotation.T+truth[0,:2]
            errors = np.linalg.norm(aligned-truth[:,:2],axis=1)
            heading_errors = np.arctan2(np.sin(slam[:,2]+angle-truth[:,2]), np.cos(slam[:,2]+angle-truth[:,2]))
            result.update({'slam_ate_rmse_m':float(np.sqrt(np.mean(errors**2))),
                           'slam_position_error_max_m':float(errors.max()),
                           'slam_final_position_error_m':float(errors[-1]),
                           'truth_return_distance_m':float(np.linalg.norm(truth[-1,:2]-truth[0,:2])),
                           'truth_path_length_m':float(np.linalg.norm(np.diff(truth[:,:2],axis=0),axis=1).sum()),
                           'truth_final_heading_change_deg':math.degrees(wrap(truth[-1,2]-truth[0,2])),
                           'slam_heading_rmse_deg':math.degrees(float(np.sqrt(np.mean(heading_errors**2))))})
            if self.map is not None:
                m = self.map
                cells = np.array(m.data).reshape(m.info.height,m.info.width)
                rows, cols = np.where(cells >= 65)
                points = np.c_[m.info.origin.position.x+(cols+.5)*m.info.resolution,
                               m.info.origin.position.y+(rows+.5)*m.info.resolution]
                # OccupancyGrid origin may carry a rotation.
                ma = yaw(m.info.origin.orientation)
                rm = np.array([[math.cos(ma),-math.sin(ma)],[math.sin(ma),math.cos(ma)]])
                local = points-np.array([m.info.origin.position.x,m.info.origin.position.y])
                points = local@rm.T+np.array([m.info.origin.position.x,m.info.origin.position.y])
                points = (points-slam[0,:2])@rotation.T+truth[0,:2]
                distances = []
                for wall in self.cfg['walls']:
                    center = np.array(wall['xyz'][:2]); half=np.array(wall['size'][:2])*.5
                    delta = np.abs(points-center)-half
                    outside = np.linalg.norm(np.maximum(delta,0),axis=1)
                    inside = np.minimum(np.max(delta,axis=1),0)
                    distances.append(np.abs(outside+inside))
                if len(points):
                    d = np.min(distances,axis=0)
                    result['occupied_cell_wall_distance_mean_m'] = float(d.mean())
                    result['occupied_cells_within_10cm_of_wall_fraction'] = float(np.mean(d<.1))
                result.update({'map_width':m.info.width, 'map_height':m.info.height,
                    'known_map_area_m2':float(np.sum(cells>=0)*m.info.resolution**2),
                    'occupied_map_cells':int(len(rows))})
        result['baseline_pass'] = bool(driving and completed and result.get('slam_ate_rmse_m',1e9)<.15
            and result.get('truth_return_distance_m',1e9)<.20
            and abs(result.get('truth_final_heading_change_deg',1e9))<15
            and result.get('occupied_cells_within_10cm_of_wall_fraction',0)>.85
            and result.get('known_map_area_m2',0)>5 and len(self.max_torque)==8)
        if emit:
            (self.out/'metrics.json').write_text(json.dumps(result,indent=2))
            print(json.dumps(result,indent=2),flush=True)
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--side',type=float,default=1.2)
    parser.add_argument('--observe-only',action='store_true')
    parser.add_argument('--seconds',type=float,default=15)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--capture',action='store_true',help='Save actual GUI screenshots at each waypoint and every 20 wall seconds.')
    parser.add_argument('--control-frame',choices=['odom','map'],default='odom',help='Use encoder odometry or SLAM TF for control. Simulator truth is evaluation-only.')
    args=parser.parse_args()
    out=args.output or ROOT/'results'/datetime.now().strftime('%Y%m%d_%H%M%S')
    out.mkdir(parents=True,exist_ok=True)
    rclpy.init()
    node=Experiment(out,capture=args.capture,control_frame=args.control_frame)
    completed=False
    error=None
    try:
        node.ready()
        print('Ready: 8 motors, lidar, encoder odometry, ground truth, map and TF.',flush=True)
        node.capture('ready')
        if args.observe_only:
            end=time.monotonic()+args.seconds
            while time.monotonic()<end:
                node.spin()
        else:
            node.drive(args.side)
        completed=True
    except (Exception,KeyboardInterrupt) as exc:
        error=str(exc) or 'Interrupted'
        print(error,flush=True)
        (out/'error.txt').write_text(traceback.format_exc())
    finally:
        if rclpy.ok():
            node.command()
        result=node.report(completed,error,driving=not args.observe_only,side=args.side)
        node.capture('completed' if completed else 'stopped')
        for job in node.capture_jobs:
            try:
                job.wait(timeout=8)
            except subprocess.TimeoutExpired:
                job.terminate()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    if completed:
        subprocess.run(['ros2','run','nav2_map_server','map_saver_cli','-f',str(out/'map'),
                        '--ros-args','-p','use_sim_time:=true','-p','save_map_timeout:=10.0'],check=False,timeout=30)
    print(f'Results: {out}',flush=True)
    if not completed or (not args.observe_only and not result['baseline_pass']):
        raise SystemExit(1)


if __name__=='__main__':
    main()
