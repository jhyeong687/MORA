#!/usr/bin/env python3
"""Derive the experiment from the imported SDF; keep the original untouched."""
import argparse
import copy
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent


def put(parent, name, value):
    element = parent.find(name)
    if element is None:
        element = ET.SubElement(parent, name)
    element.text = str(value)
    return element


def matrix(text):
    x, y, z, r, p, a = map(float, text.split())
    cr, sr, cp, sp, ca, sa = math.cos(r), math.sin(r), math.cos(p), math.sin(p), math.cos(a), math.sin(a)
    result = np.eye(4)
    result[:3, :3] = [[ca*cp, ca*sp*sr-sa*cr, ca*sp*cr+sa*sr],
                      [sa*cp, sa*sp*sr+ca*cr, sa*sp*cr-ca*sr],
                      [-sp, cp*sr, cp*cr]]
    result[:3, 3] = [x, y, z]
    return result


def origin(parent, transform):
    r = math.atan2(transform[2, 1], transform[2, 2])
    p = math.atan2(-transform[2, 0], math.hypot(transform[0, 0], transform[1, 0]))
    a = math.atan2(transform[1, 0], transform[0, 0])
    ET.SubElement(parent, 'origin', xyz=' '.join(map(str, transform[:3, 3])), rpy=f'{r} {p} {a}')


def box(world, name, xyz, size, color):
    model = ET.SubElement(world, 'model', name=name)
    put(model, 'static', 'true')
    link = ET.SubElement(model, 'link', name='link')
    put(link, 'pose', f'{xyz[0]} {xyz[1]} {xyz[2]} 0 0 0')
    for kind in ('collision', 'visual'):
        geom = ET.SubElement(ET.SubElement(link, kind, name=kind), 'geometry')
        put(ET.SubElement(geom, 'box'), 'size', ' '.join(map(str, size)))
    material = ET.SubElement(link.find('visual'), 'material')
    put(material, 'ambient', color)
    put(material, 'diffuse', color)


def add_pick_place(world, robot):
    task=yaml.safe_load((ROOT/'pick_place.yaml').read_text())
    contact=ET.SubElement(world,'plugin',filename='gz-sim-contact-system',name='gz::sim::systems::Contact')
    for table in task['tables']:
        x,y=table['center'];width,depth=table['size'];height=table['top_height']
        box(world,table['name'],(x,y,height-.015),(width,depth,.03),'.45 .28 .12 1')
        for i,dx in enumerate([-width/2+.035,width/2-.035]):
            for j,dy in enumerate([-depth/2+.035,depth/2-.035]):
                box(world,f"{table['name']}_leg_{i}{j}",(x+dx,y+dy,(height-.03)/2),(.035,.035,height-.03),'.30 .32 .34 1')
    cube=task['object'];box(world,cube['name'],cube['xyz'],cube['size'],' '.join(map(str,cube['color'])))
    obj=world.find(f"model[@name='{cube['name']}']");put(obj,'static','false')
    link=obj.find('link');mass=cube['mass'];sx,sy,sz=cube['size']
    inertial=ET.SubElement(link,'inertial');put(inertial,'mass',mass);inertia=ET.SubElement(inertial,'inertia')
    for key,value in {'ixx':mass*(sy*sy+sz*sz)/12,'iyy':mass*(sx*sx+sz*sz)/12,'izz':mass*(sx*sx+sy*sy)/12,'ixy':0,'ixz':0,'iyz':0}.items():put(inertia,key,value)
    surface=ET.SubElement(link.find('collision'),'surface');ode=ET.SubElement(ET.SubElement(surface,'friction'),'ode')
    put(ode,'mu',.8);put(ode,'mu2',.8)
    # The odometry publisher expects a model origin at the object's COM.
    put(obj,'pose',link.findtext('pose'));link.remove(link.find('pose'))
    truth=ET.SubElement(obj,'plugin',filename='gz-sim-odometry-publisher-system',name='gz::sim::systems::OdometryPublisher')
    for key,value in {'odom_frame':'world','robot_base_frame':'task_cube/link','odom_topic':'/evaluation/object_odom',
        'tf_topic':'/evaluation/object_tf_unused','odom_publish_frequency':30,'dimensions':3}.items():put(truth,key,value)
    camera=robot.find("link[@name='wrist_camera_link']/sensor[@name='wrist_cam']")
    put(camera,'gz_frame_id','wrist_camera_optical')
    # A single convex hull bridges the fixed jaw and hand body, filling the
    # grasp aperture. Split the collision geometry into a body and finger pads.
    # Visual meshes, masses and motor caps remain those of the imported arm.
    tip=matrix(robot.find("link[@name='gripper_frame_link']").findtext('pose'))
    for name,body_center,body_size,pad_center,pad_size in [
        ('gripper_link',[-.005,0,-.070],[.066,.050,.055],[.006,0,-.010],[.012,.013,.038]),
        ('moving_jaw_so101_v1_link',[-.022,0,-.062],[.024,.048,.043],[-.034,0,-.010],[.010,.013,.038])]:
        link=robot.find(f"link[@name='{name}']")
        for collision in list(link.findall('collision')):link.remove(collision)
        relative=np.linalg.inv(matrix(link.findtext('pose')))@tip
        for shape_name,center,size in [('hand_body',body_center,body_size),('finger_pad',pad_center,pad_size)]:
            t=relative.copy();t[:3,3]+=relative[:3,:3]@np.array(center)
            r=math.atan2(t[2,1],t[2,2]);p=math.atan2(-t[2,0],math.hypot(t[0,0],t[1,0]));a=math.atan2(t[1,0],t[0,0])
            collision=ET.SubElement(link,'collision',name=shape_name)
            put(collision,'pose',' '.join(map(str,[*t[:3,3],r,p,a])))
            put(ET.SubElement(ET.SubElement(collision,'geometry'),'box'),'size',' '.join(map(str,size)))
            ode=ET.SubElement(ET.SubElement(ET.SubElement(collision,'surface'),'friction'),'ode')
            put(ode,'mu',.8);put(ode,'mu2',.8)
            if shape_name=='finger_pad':
                visual=ET.SubElement(link,'visual',name='contact_pad')
                put(visual,'pose',collision.findtext('pose'))
                visual.append(copy.deepcopy(collision.find('geometry')))
                material=ET.SubElement(visual,'material');put(material,'ambient','.12 .12 .12 1');put(material,'diffuse','.12 .12 .12 1')
    task['grasp']['collision_model']='Split hand body and rectangular finger pads; approximation, not identified real contact geometry.'
    for name,collision,topic in [('gripper_link','finger_pad','/grasp/fixed_contacts'),
        ('moving_jaw_so101_v1_link','finger_pad','/grasp/moving_contacts')]:
        sensor=ET.SubElement(robot.find(f"link[@name='{name}']"),'sensor',name='finger_contacts',type='contact')
        put(sensor,'always_on','true');put(sensor,'update_rate',30);put(sensor,'topic',topic)
        contact=ET.SubElement(sensor,'contact');put(contact,'collision',collision);put(contact,'topic',topic)
    return task


def add_carried_payload(world,robot):
    scene=add_pick_place(world,robot)
    world.remove(world.find(f"model[@name='{scene['object']['name']}']"))
    task=yaml.safe_load((ROOT/'carry.yaml').read_text())
    task['tables']=scene['tables']
    payload=task['payload'];mass=payload['mass'];sx,sy,sz=payload['size']
    tool=matrix(robot.find("link[@name='gripper_frame_link']").findtext('pose'))
    point=tool[:3,:3]@np.array(payload['center_in_tool'])+tool[:3,3]
    link=ET.SubElement(robot,'link',name='held_payload')
    put(link,'pose',f'{point[0]} {point[1]} {point[2]} 0 0 0')
    inertial=ET.SubElement(link,'inertial');put(inertial,'mass',mass);inertia=ET.SubElement(inertial,'inertia')
    for key,value in {'ixx':mass*(sy*sy+sz*sz)/12,'iyy':mass*(sx*sx+sz*sz)/12,'izz':mass*(sx*sx+sy*sy)/12,'ixy':0,'ixz':0,'iyz':0}.items():put(inertia,key,value)
    for kind in ['collision','visual']:
        element=ET.SubElement(link,kind,name='payload_'+kind)
        put(ET.SubElement(ET.SubElement(element,'geometry'),'box'),'size',' '.join(map(str,payload['size'])))
        if kind=='visual':
            material=ET.SubElement(element,'material');put(material,'ambient','.95 .035 .025 1');put(material,'diffuse','.95 .035 .025 1')
    joint=ET.SubElement(robot,'joint',name='held_payload_fixture',type='fixed')
    put(joint,'parent','gripper_link');put(joint,'child','held_payload')
    task['grasp_tested']=False;task['placement_tested']=False
    return task


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', choices=['so101_7v4', 'imported_12v'])
    parser.add_argument('--friction', type=float)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--config', type=Path, default=ROOT/'experiment.yaml')
    parser.add_argument('--scenario',choices=['slam','pick_place','carry'],default='slam')
    parser.add_argument('--spawn',nargs=3,type=float,metavar=('X','Y','YAW'))
    parser.add_argument('--odom-calibration',type=Path)
    args = parser.parse_args()
    cfg = yaml.safe_load(args.config.read_text())
    calibration=args.odom_calibration
    if calibration is None and cfg.get('odometry_calibration'):
        calibration=ROOT/cfg['odometry_calibration']
    if calibration is None and args.scenario in cfg.get('simulation_odometry_calibrations',{}):
        calibration=ROOT/cfg['simulation_odometry_calibrations'][args.scenario]
    cfg['encoder_odometry']={'wheel_radius':cfg['base']['wheel_radius'],
        'wheel_separation':cfg['base']['wheel_separation'],'kind':'nominal','hardware_calibrated':False}
    if calibration is not None:
        data=yaml.safe_load(calibration.read_text())
        for key in ('wheel_radius','wheel_separation'):
            if not math.isfinite(data[key]) or data[key]<=0:raise ValueError('Invalid calibration '+key)
        if data.get('kind')!='simulation_identification':raise ValueError('Expected simulation identification')
        cfg['encoder_odometry']={**data,'file':str(calibration.resolve()),'hardware_calibrated':False}
    if args.spawn is not None:cfg['spawn']=args.spawn
    if args.profile:
        cfg['profile'] = args.profile
    if args.friction is not None:
        cfg['base']['tire_friction'] = args.friction
    if args.seed is not None:
        cfg['seed'] = args.seed
    if calibration is not None:
        if data['scenario']!=args.scenario or data['seed']!=cfg['seed'] or data['tire_friction']!=cfg['base']['tire_friction']:
            raise ValueError('Calibration condition mismatch: scenario, seed or tire friction')
        for key,current in [('profile',cfg['profile']),('nominal_wheel_radius',cfg['base']['wheel_radius']),
                            ('nominal_wheel_separation',cfg['base']['wheel_separation'])]:
            if key in data and data[key]!=current:raise ValueError('Calibration condition mismatch: '+key)
        if args.scenario=='carry':
            payload=yaml.safe_load((ROOT/'carry.yaml').read_text())['payload']
            if payload['mass']!=data['payload_mass_kg']:
                raise ValueError('Calibration payload mass mismatch; identify again')
    tree = ET.parse(ROOT.parent/'lab.sdf')
    world = tree.getroot().find('world')
    world.set('name', 'r4_slam')
    for model in list(world.findall('model')):
        if model.get('name') != 'r4':
            world.remove(model)
    physics = ET.SubElement(world, 'physics', name='r4_physics', type='ignored')
    put(physics, 'max_step_size', cfg['physics_step'])
    put(physics, 'real_time_factor', 1.0)
    box(world, 'floor', (0, 0, -.05), (6, 5, .1), '.72 .76 .78 1')
    walls = [('east', (2.55, 0, .5), (.1, 4.2, 1)),
             ('west', (-2.55, 0, .5), (.1, 4.2, 1)),
             ('north', (0, 2.05, .5), (5.2, .1, 1)),
             ('south', (0, -2.05, .5), (5.2, .1, 1)),
             ('partition', (.9, .65, .4), (.12, 1.1, .8)),
             ('cabinet', (-.9, 1.2, .35), (.65, .45, .7)),
             ('pillar', (1.7, -1.0, .4), (.3, .4, .8))]
    for name, xyz, size in walls:
        box(world, name, xyz, size, '.35 .50 .65 1' if name == 'partition' else '.82 .78 .66 1')
    robot = world.find("model[@name='r4']")
    sx, sy, yaw = cfg['spawn']
    put(robot, 'pose', f'{sx} {sy} 0 0 0 {yaw}')
    for plugin in list(robot.findall('plugin')):
        robot.remove(plugin)
    motors = ET.SubElement(robot, 'plugin', filename='libr4_motors.so', name='r4::MotorSystem')
    arm = cfg['arm']['profiles'][cfg['profile']]
    put(motors, 'arm_voltage', arm['voltage'])
    put(motors, 'rated_arm_cap', str(cfg['arm']['rated_torque_cap']).lower())
    put(motors, 'command_latency', cfg['base']['command_latency'])
    put(motors, 'wheel_radius', cfg['base']['wheel_radius'])
    put(motors, 'wheel_separation', cfg['base']['wheel_separation'])
    put(motors, 'odom_wheel_radius', cfg['encoder_odometry']['wheel_radius'])
    put(motors, 'odom_wheel_separation', cfg['encoder_odometry']['wheel_separation'])
    put(motors, 'encoder_step', 2*math.pi/cfg['base']['encoder_counts'])
    resolved = {}
    for name, values in cfg['motors'].items():
        values = dict(values)
        if not name.startswith('axle'):
            values = {**arm, **values}
            if not cfg['arm']['rated_torque_cap']:
                values['torque_cap'] = values['stall_torque']
        values['no_load_speed'] = values['no_load_rpm']*2*math.pi/60
        resolved[name] = values
        motor = ET.SubElement(motors, 'motor', name=name)
        for key in ('stall_torque', 'no_load_speed', 'torque_cap', 'kp', 'kd', 'deadband', 'coulomb_friction'):
            if key in values:
                put(motor, key, values[key])
        joint = robot.find(f"joint[@name='{name}']")
        limit = joint.find('axis/limit')
        if limit is None:
            limit = ET.SubElement(joint.find('axis'), 'limit')
            put(limit, 'lower', -1e16)
            put(limit, 'upper', 1e16)
        put(limit, 'effort', values['stall_torque'])
        put(limit, 'velocity', values['no_load_speed'])
        # Gazebo/DART has no MuJoCo joint armature equivalent in this model.
        # A stated, adjustable inertia proxy avoids an unstable massless rotor.
        child = robot.find(f"link[@name='{joint.findtext('child')}']")
        extra = cfg['base' if name.startswith('axle') else 'arm']['rotor_inertia_proxy']
        for key in ('ixx', 'iyy', 'izz'):
            inertia = child.find('inertial/inertia')
            put(inertia, key, float(inertia.findtext(key))+extra)
    for name in ('wheel_left', 'wheel_right'):
        for ode in robot.findall(f"link[@name='{name}']/collision/surface/friction/ode"):
            put(ode, 'mu', cfg['base']['tire_friction'])
            put(ode, 'mu2', cfg['base']['tire_friction'])
    lidar = robot.find("link[@name='lds']/sensor")
    put(lidar, 'topic', '/scan_raw')
    put(lidar, 'gz_frame_id', 'lds')
    put(lidar, 'update_rate', cfg['lidar']['hz'])
    put(lidar.find('lidar/scan/horizontal'), 'samples', cfg['lidar']['samples'])
    put(lidar.find('lidar/range'), 'min', cfg['lidar']['min_range'])
    put(lidar.find('lidar/range'), 'max', cfg['lidar']['max_range'])
    noise = ET.SubElement(lidar.find('lidar'), 'noise')
    put(noise, 'type', 'gaussian')
    put(noise, 'mean', 0)
    put(noise, 'stddev', cfg['lidar']['gaussian_stddev'])
    imu = robot.find("link[@name='burger']/sensor[@name='imu']")
    put(imu, 'gz_frame_id', 'burger')
    truth = ET.SubElement(robot, 'plugin', filename='gz-sim-odometry-publisher-system', name='gz::sim::systems::OdometryPublisher')
    for k, v in {'odom_frame':'world', 'robot_base_frame':'burger', 'odom_topic':'/ground_truth/odom',
                 'tf_topic':'/ground_truth/tf_unused', 'odom_publish_frequency':50, 'dimensions':3}.items():
        put(truth, k, v)
    cfg['scenario']=args.scenario
    if args.scenario=='pick_place':cfg['task']=add_pick_place(world,robot)
    if args.scenario=='carry':cfg['task']=add_carried_payload(world,robot)
    # Build a TF/visual description from the SAME zero-pose SDF.
    urdf = ET.Element('robot', name='r4')
    ET.SubElement(urdf, 'link', name='base_footprint')
    fixed = ET.SubElement(urdf, 'joint', name='base_to_burger', type='fixed')
    ET.SubElement(fixed, 'parent', link='base_footprint')
    ET.SubElement(fixed, 'child', link='burger')
    origin(fixed, matrix(robot.find("link[@name='burger']").findtext('pose')))
    poses = {}
    for link in robot.findall('link'):
        name = link.get('name')
        poses[name] = matrix(link.findtext('pose', '0 0 0 0 0 0'))
        out = ET.SubElement(urdf, 'link', name=name)
        for visual in link.findall('visual'):
            v = ET.SubElement(out, 'visual')
            origin(v, matrix(visual.findtext('pose', '0 0 0 0 0 0')))
            geometry = ET.SubElement(v, 'geometry')
            mesh = visual.find('geometry/mesh')
            if mesh is not None:
                path = ROOT.parent/mesh.findtext('uri').replace('model://', '')
                ET.SubElement(geometry, 'mesh', filename=f'file://{path}')
            else:
                for shape in visual.find('geometry'):
                    ET.SubElement(geometry, shape.tag, **{c.tag: c.text for c in shape})
            material = ET.SubElement(v, 'material', name=f'{name}_{len(out)}')
            ET.SubElement(material, 'color', rgba=visual.findtext('material/diffuse', '.6 .6 .6 1'))
    for joint in robot.findall('joint'):
        parent, child = joint.findtext('parent'), joint.findtext('child')
        jt = joint.get('type')
        jt = 'fixed' if jt == 'ball' else jt  # Spherical support orientation is immaterial to TF.
        if joint.get('name').startswith('axle'):
            jt = 'continuous'
        out = ET.SubElement(urdf, 'joint', name=joint.get('name'), type=jt)
        ET.SubElement(out, 'parent', link=parent)
        ET.SubElement(out, 'child', link=child)
        origin(out, np.linalg.inv(poses[parent])@poses[child])
        if jt != 'fixed':
            ET.SubElement(out, 'axis', xyz=joint.findtext('axis/xyz', '0 0 1'))
            ET.SubElement(out, 'limit', **{c.tag:c.text for c in joint.find('axis/limit')})
    if args.scenario in ['pick_place','carry']:
        ET.SubElement(urdf,'link',name='wrist_camera_optical')
        fixed=ET.SubElement(urdf,'joint',name='wrist_camera_optical_joint',type='fixed')
        ET.SubElement(fixed,'parent',link='wrist_camera_link');ET.SubElement(fixed,'child',link='wrist_camera_optical')
        optical=np.eye(4);optical[:3,:3]=[[0,0,1],[-1,0,0],[0,-1,0]]
        camera=robot.find("link[@name='wrist_camera_link']/sensor[@name='wrist_cam']")
        origin(fixed,matrix(camera.findtext('pose'))@optical)
    generated = ROOT/'generated'
    generated.mkdir(exist_ok=True)
    ET.indent(tree)
    tree.write(generated/'world.sdf', encoding='utf-8', xml_declaration=True)
    ET.indent(urdf)
    ET.ElementTree(urdf).write(generated/'r4.urdf', encoding='utf-8', xml_declaration=True)
    cfg['resolved_motors'] = resolved
    cfg['imported_mass_kg'] = sum(float(l.findtext('inertial/mass', '0')) for l in robot.findall('link'))
    cfg['walls'] = [{'name':n, 'xyz':x, 'size':s} for n,x,s in walls]
    (generated/'resolved.json').write_text(json.dumps(cfg, indent=2))
    slam = yaml.safe_load(Path('/opt/ros/jazzy/share/slam_toolbox/config/mapper_params_online_async.yaml').read_text())
    slam['slam_toolbox']['ros__parameters'].update({
        'use_sim_time': True, 'base_frame': 'base_footprint', 'resolution': .025,
        'min_laser_range': .18, 'max_laser_range': 8.0, 'map_update_interval': 1.0,
        **cfg.get('slam',{}),
        'minimum_time_interval': .15, 'transform_timeout': .5,
        'scan_buffer_size': 20, 'loop_match_minimum_chain_size': 5,
        'enable_interactive_mode': False})
    (generated/'slam.yaml').write_text(yaml.safe_dump(slam))
    print(f"Prepared {cfg['profile']}, {cfg['imported_mass_kg']:.3f} kg, 8 effort-controlled motors")


if __name__ == '__main__':
    main()
