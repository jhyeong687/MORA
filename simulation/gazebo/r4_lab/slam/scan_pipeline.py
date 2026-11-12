#!/usr/bin/env python3
"""Explicit sensor delay / error variants; the raw scan remains inspectable."""
from collections import deque
import copy
import json
import math
from pathlib import Path
import random
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener, TransformException


class ScanPipeline(Node):
    def __init__(self):
        super().__init__('r4_scan_pipeline')
        cfg = json.loads((Path(__file__).resolve().parent/'generated/resolved.json').read_text())
        self.cfg = cfg['lidar']
        self.rng = random.Random(cfg['seed'])
        self.declare_parameter('stress', False)
        self.pending = deque()
        self.tf_buffer=Buffer();self.tf_listener=TransformListener(self.tf_buffer,self)
        self.startup_drops=0
        # A reliable writer can serve both reliable and best-effort readers.
        self.pub = self.create_publisher(LaserScan, '/scan',
            QoSProfile(depth=5,reliability=ReliabilityPolicy.RELIABLE))
        self.sub = self.create_subscription(LaserScan, '/scan_raw', self.receive, qos_profile_sensor_data)
        self.timer = self.create_timer(.005, self.flush)

    def receive(self, msg):
        msg = copy.deepcopy(msg)
        if self.get_parameter('stress').value:
            output = []
            for value in msg.ranges:
                if self.rng.random() < self.cfg['stress_dropout_probability']:
                    value = math.inf
                elif math.isfinite(value):
                    value += self.rng.gauss(0, self.cfg['stress_relative_stddev']*value)
                    if not msg.range_min <= value <= msg.range_max:
                        value = math.inf
                output.append(value)
            msg.ranges = output
        # Keep acquisition timestamp; delay delivery, never restamp an old scan.
        self.pending.append((self.get_clock().now().nanoseconds/1e9+self.cfg['transport_delay'], msg))

    def flush(self):
        now = self.get_clock().now().nanoseconds/1e9
        while self.pending and self.pending[0][0] <= now:
            due,msg=self.pending[0]
            try:
                self.tf_buffer.lookup_transform('odom',msg.header.frame_id,Time.from_msg(msg.header.stamp))
            except TransformException:
                if now-due<.5:return
                self.pending.popleft();self.startup_drops+=1
                self.get_logger().info('Discarded scan without acquisition-time odom TF (startup/stale data).')
                continue
            self.pub.publish(self.pending.popleft()[1])


def main():
    rclpy.init()
    node = ScanPipeline()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
