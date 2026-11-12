#!/usr/bin/env python3
"""Export figures from saved experiment measurements; no invented samples."""
import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment', type=Path)
    args = parser.parse_args()
    directory = args.experiment
    samples = json.loads((directory/'trajectory.json').read_text())
    metrics = json.loads((directory/'metrics.json').read_text())
    truth = np.array([s['truth'] for s in samples])
    slam = np.array([s['slam'] for s in samples])
    odom = np.array([s['odom'] for s in samples])
    times = np.array([s['time'] for s in samples])
    times -= times[0]
    def align(poses):
        angle = truth[0,2]-poses[0,2]
        rotation = np.array([[math.cos(angle),-math.sin(angle)], [math.sin(angle),math.cos(angle)]])
        return (poses[:,:2]-poses[0,:2])@rotation.T+truth[0,:2]
    aligned, enc = align(slam), align(odom)
    fig, axes = plt.subplots(2,2,figsize=(12,9),constrained_layout=True)
    ax = axes[0,0]
    ax.plot(truth[:,0],truth[:,1],color='black',lw=2,label='Simulator truth')
    ax.plot(aligned[:,0],aligned[:,1],color='#14814b',lw=1.4,label='SLAM')
    ax.plot(enc[:,0],enc[:,1],color='#c36e16',lw=1.2,ls='--',label='Encoder odometry')
    ax.scatter(*truth[0,:2],s=50,marker='o',color='blue',label='Start')
    ax.scatter(*truth[-1,:2],s=60,marker='x',color='red',label='End')
    ax.set(title='Measured trajectories (first-pose alignment)',xlabel='World x [m]',ylabel='World y [m]')
    ax.axis('equal'); ax.legend(fontsize=8); ax.grid(alpha=.25)
    ax=axes[0,1]
    ax.plot(times,np.linalg.norm(aligned-truth[:,:2],axis=1)*100, label='SLAM',color='#14814b')
    ax.plot(times,np.linalg.norm(enc-truth[:,:2],axis=1)*100,label='Encoder odometry',color='#c36e16')
    ax.set(title='Position error',xlabel='Simulation time from start [s]',ylabel='Error [cm]')
    ax.legend(); ax.grid(alpha=.25)
    ax=axes[1,0]
    if (directory/'map.pgm').exists():
        config=yaml.safe_load((directory/'map.yaml').read_text())
        pixels=np.asarray(Image.open(directory/'map.pgm'))
        res=config['resolution']; x,y,_=config['origin']
        ax.imshow(pixels,cmap='gray',vmin=0,vmax=255,origin='upper',
            extent=[x,x+pixels.shape[1]*res,y,y+pixels.shape[0]*res],interpolation='nearest')
        ax.plot(slam[:,0],slam[:,1],color='#14814b',lw=1)
        ax.set(title='Saved SLAM occupancy map',xlabel='Map x [m]',ylabel='Map y [m]')
        ax.set_aspect('equal')
    else:
        ax.text(.5,.5,'No map file saved for this attempt',ha='center');ax.axis('off')
    ax=axes[1,1]
    names=list(metrics['max_motor_effort_nm'])
    efforts=[metrics['max_motor_effort_nm'][n] for n in names]
    ax.barh(names,efforts,color=['#c36e16' if n.startswith('axle') else '#2866a3' for n in names])
    ax.set(title='Maximum observed commanded motor effort',xlabel='Torque [N m]')
    ax.grid(axis='x',alpha=.25)
    outcome='COMPLETED' if metrics['completed'] else 'INCOMPLETE'
    fig.suptitle(f"R4 simulation | {directory.name} | {outcome}\n"
        f"SLAM ATE RMSE {metrics.get('slam_ate_rmse_m',float('nan'))*100:.2f} cm | "
        f"Return distance {metrics.get('truth_return_distance_m',float('nan'))*100:.1f} cm | "
        'Single simulated trial; hardware calibration and loop-closure event not verified',fontsize=11)
    for suffix in ('png','pdf','svg'):
        fig.savefig(directory/f'research_figure.{suffix}',dpi=220)
    np.savetxt(directory/'trajectory_aligned.csv',np.c_[times,truth,aligned,enc],delimiter=',',
        header='sim_time_s,truth_x_m,truth_y_m,truth_yaw_rad,slam_aligned_x_m,slam_aligned_y_m,odom_aligned_x_m,odom_aligned_y_m',comments='')
    print(directory/'research_figure.png')


if __name__=='__main__':
    main()
