"""Forward/inverse kinematics derived from the generated R4 URDF."""
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parent
ARM_NAMES=['shoulder_pan','shoulder_lift','elbow_flex','wrist_flex','wrist_roll','gripper']


def transform(xyz=(0,0,0),rpy=(0,0,0)):
    out=np.eye(4);out[:3,:3]=Rotation.from_euler('xyz',rpy).as_matrix();out[:3,3]=xyz
    return out


class ArmKinematics:
    def __init__(self,path=ROOT/'generated/r4.urdf'):
        robot=ET.parse(path).getroot()
        self.joints=[];self.limits={}
        for joint in robot.findall('joint'):
            origin=joint.find('origin')
            pose=transform([float(v) for v in origin.get('xyz','0 0 0').split()],
                [float(v) for v in origin.get('rpy','0 0 0').split()]) if origin is not None else np.eye(4)
            axis=joint.find('axis')
            self.joints.append((joint.get('name'),joint.get('type'),joint.find('parent').get('link'),
                joint.find('child').get('link'),pose,np.array([float(v) for v in axis.get('xyz').split()]) if axis is not None else np.array([0,0,1])))
            limit=joint.find('limit')
            if limit is not None and joint.get('name') in ARM_NAMES:
                self.limits[joint.get('name')]=(float(limit.get('lower')),float(limit.get('upper')))

    def fk(self,q):
        if not isinstance(q,dict):q=dict(zip(ARM_NAMES,q))
        poses={'base_footprint':np.eye(4)}
        pending=list(self.joints)
        while pending:
            progress=False
            for item in pending[:]:
                name,kind,parent,child,origin,axis=item
                if parent not in poses:continue
                rotation=np.eye(4)
                if kind!='fixed':rotation[:3,:3]=Rotation.from_rotvec(axis*q.get(name,0)).as_matrix()
                poses[child]=poses[parent]@origin@rotation
                pending.remove(item);progress=True
            if not progress:raise RuntimeError('Disconnected URDF chain')
        return poses

    def solve(self,position,seed=None,tool_axis=None,axis_index=0,tcp_offset=None,tool_x=None):
        target=np.array(position)
        bounds=np.array([self.limits[n] for n in ARM_NAMES[:5]])
        seeds=[np.zeros(5) if seed is None else np.array(seed[:5])]
        rng=np.random.default_rng(42)
        seeds += [rng.uniform(bounds[:,0]+.03,bounds[:,1]-.03) for _ in range(18)]
        def residual(q):
            pose=self.fk(list(q)+[0])['gripper_frame_link']
            point=pose[:3,3] if tcp_offset is None else pose[:3,3]+pose[:3,:3]@np.array(tcp_offset)
            error=(point-target)*10
            if tool_axis is not None:error=np.r_[error,(pose[:3,axis_index]-tool_axis)*.35]
            if tool_x is not None:error=np.r_[error,(pose[:3,0]-tool_x)*.25]
            return error
        best=None
        for q in seeds:
            result=least_squares(residual,np.clip(q,bounds[:,0]+.01,bounds[:,1]-.01),
                bounds=(bounds[:,0]+.005,bounds[:,1]-.005),max_nfev=300)
            if best is None or np.linalg.norm(result.fun)<np.linalg.norm(best.fun):best=result
            if np.linalg.norm(best.fun)<.002 or (np.linalg.norm(best.fun[:3])<.005 and np.linalg.norm(best.fun[3:])<.03):break
        pose=self.fk(list(best.x)+[0])['gripper_frame_link']
        point=pose[:3,3] if tcp_offset is None else pose[:3,3]+pose[:3,:3]@np.array(tcp_offset)
        return {'q':best.x.tolist(),'position_error_m':float(np.linalg.norm(point-target)),
            'residual':float(np.linalg.norm(best.fun)),'pose':pose.tolist()}
