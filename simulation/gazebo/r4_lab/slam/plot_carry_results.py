#!/usr/bin/env python3
"""Draw carry-only navigation evidence from saved measurements."""
import argparse
import json
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np


def main():
    parser=argparse.ArgumentParser();parser.add_argument('trial',type=Path);args=parser.parse_args();root=args.trial
    config=json.loads((root/'configuration.json').read_text());metrics=json.loads((root/'metrics.json').read_text())
    rows=json.loads((root/'trajectory.json').read_text());truth=np.array([r['truth'] for r in rows]);slam=np.array([r['slam'] for r in rows])
    angle=truth[0,2]-slam[0,2];c,s=math.cos(angle),math.sin(angle);rotation=np.array([[c,-s],[s,c]])
    aligned=(slam[:,:2]-slam[0,:2])@rotation.T+truth[0,:2]
    fig,axs=plt.subplots(1,2,figsize=(12,5),constrained_layout=True)
    for item in config['walls']:
        x,y,_=item['xyz'];w,h,_=item['size'];axs[0].add_patch(Rectangle((x-w/2,y-h/2),w,h,color='#d6d0be'))
    for table in config['task']['tables']:
        x,y=table['center'];w,h=table['size'];axs[0].add_patch(Rectangle((x-w/2,y-h/2),w,h,color='#b98a59',alpha=.6))
    axs[0].plot(truth[:,0],truth[:,1],color='black',lw=1.8,label='Simulator truth')
    axs[0].plot(aligned[:,0],aligned[:,1],color='#168451',lw=1.1,label='SLAM, first-pose alignment')
    for i,waypoint in enumerate(config['task']['waypoints']):
        x,y,a=waypoint['world'];axs[0].scatter(x,y,color='#277bc0',s=40)
        axs[0].annotate(str(i+1),(x,y),xytext=(6,7),textcoords='offset points',color='#155488',fontweight='bold')
    axs[0].set(xlabel='World x [m]',ylabel='World y [m]',title='Measured path and assigned waypoints');axs[0].axis('equal');axs[0].legend(fontsize=8);axs[0].grid(alpha=.2)
    arrivals=metrics['waypoints'];names=[f'{i+1}: {r["name"]}' for i,r in enumerate(arrivals)]
    actual=[r['evaluation_position_error_m']*100 for r in arrivals];mapped=[r['map_position_error_m']*100 for r in arrivals]
    index=np.arange(len(arrivals));a=axs[1].bar(index-.18,mapped,width=.36,label='SLAM map error',color='#168451');b=axs[1].bar(index+.18,actual,width=.36,label='Actual position error',color='#277bc0')
    axs[1].bar_label(a,fmt='%.1f',padding=3,fontsize=8);axs[1].bar_label(b,fmt='%.1f',padding=3,fontsize=8)
    axs[1].axhline(config['task']['navigation']['evaluation_position_tolerance']*100,color='gray',ls='--',label='Actual position criterion')
    axs[1].set(xticks=index,xticklabels=names,ylabel='Arrival error [cm]',title='Waypoint arrival after stopping');axs[1].tick_params(axis='x',labelrotation=15);axs[1].legend(fontsize=8);axs[1].grid(axis='y',alpha=.2)
    result='PASS' if metrics['navigation_pass'] else 'NOT PASSED'
    fig.suptitle(f'Carry-only waypoint test | {result} | fixed 10 g payload\nAlready-held initial fixture; grasping and placement were not tested. One simulated trial.',fontsize=11)
    fig.savefig(root/'carry_result.png',dpi=200);fig.savefig(root/'carry_result.pdf')
    print(root/'carry_result.png')


if __name__=='__main__':main()
