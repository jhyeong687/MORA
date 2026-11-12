import time, math
import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan,Image,Imu
from rclpy.qos import qos_profile_sensor_data
rclpy.init()
node=rclpy.create_node('r4_smoke')
data={}
subscriptions=[]
for topic,typ in [('odom',Odometry),('scan',LaserScan),('imu',Imu),('wrist_cam/image',Image),('belly_cam/image',Image)]:
 subscriptions.append(node.create_subscription(typ,'/'+topic,lambda msg,t=topic:data.update({t:msg}),qos_profile_sensor_data))
pub=node.create_publisher(Twist,'/cmd_vel',10)
end=time.monotonic()+70
while len(data)<5 and time.monotonic()<end:rclpy.spin_once(node,timeout_sec=.25)
print('received',list(data),flush=True)
assert len(data)==5
assert len(data['scan'].ranges)==360 and any(math.isfinite(x) for x in data['scan'].ranges)
for t in ['wrist_cam/image','belly_cam/image']:assert len(data[t].data)>=320*240
x0=data['odom'].pose.pose.position.x
msg=Twist();msg.linear.x=.10
end=time.monotonic()+15
try:
 while abs(data['odom'].pose.pose.position.x-x0)<.035 and time.monotonic()<end:
  pub.publish(msg);rclpy.spin_once(node,timeout_sec=.05);time.sleep(.02)
finally:pub.publish(Twist())
dx=data['odom'].pose.pose.position.x-x0
print('odometry dx',dx,'lidar rays',len(data['scan'].ranges),flush=True)
assert dx>.03
node.destroy_node();rclpy.shutdown()
