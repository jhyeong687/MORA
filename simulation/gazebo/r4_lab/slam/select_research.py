#!/usr/bin/env python3
"""Select a small evidence set and timestamp-preserving video excerpts."""
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def excerpt(source, target, intervals):
    reader = Gst.parse_launch(f'filesrc location="{source}" ! qtdemux ! avdec_h264 ! '
        'videoconvert ! video/x-raw,format=RGB ! appsink name=decoded sync=false max-buffers=2')
    sink = reader.get_by_name('decoded')
    writer = Gst.parse_launch('appsrc name=frames block=true format=time ! queue ! videoconvert ! '
        'x264enc tune=zerolatency speed-preset=ultrafast bitrate=3500 ! '
        f'video/x-h264,stream-format=avc,alignment=au ! mp4mux ! filesink location="{target}"')
    appsrc = writer.get_by_name('frames')
    reader.set_state(Gst.State.PLAYING)
    started = False
    count = 0
    try:
        while True:
            sample = sink.emit('try-pull-sample', 10*Gst.SECOND)
            if sample is None:
                if not sink.get_property('eos'):
                    raise RuntimeError('Decoder timed out before EOS')
                break
            buf = sample.get_buffer()
            seconds = buf.pts/Gst.SECOND
            offset = 0.0
            for start, end in intervals:
                if start <= seconds < end:
                    if not started:
                        appsrc.set_property('caps', sample.get_caps())
                        writer.set_state(Gst.State.PLAYING)
                        started = True
                    new = buf.copy_deep()
                    new.pts = int((offset+seconds-start)*Gst.SECOND)
                    new.dts = Gst.CLOCK_TIME_NONE
                    if appsrc.emit('push-buffer', new) != Gst.FlowReturn.OK:
                        raise RuntimeError('Excerpt encoder rejected frame')
                    count += 1
                    break
                offset += end-start
        if not started:
            raise RuntimeError('No frames in selected intervals')
        appsrc.emit('end-of-stream')
        msg=writer.get_bus().timed_pop_filtered(20*Gst.SECOND,Gst.MessageType.EOS|Gst.MessageType.ERROR)
        if not msg or msg.type != Gst.MessageType.EOS:
            raise RuntimeError('Excerpt encoder did not finish successfully')
    finally:
        reader.set_state(Gst.State.NULL)
        writer.set_state(Gst.State.NULL)
    return count


def main():
    root = Path(sys.argv[1])
    output = root/'selected'
    output.mkdir(exist_ok=True)
    Gst.init(None)
    trials = [('baseline_12m_fresh','fresh_square_12m','Encoder feedback','#b65b16'),
              ('slam_feedback_12m','slam_feedback_12m','SLAM feedback','#14814b')]
    manifest = {'selection': 'Four key images and two short video excerpts; original data retained separately.',
                'video_edits': 'First 12 and last 24 seconds around each recorded trial, joined chronologically. Middle omitted; original UTC labels and playback speed preserved.',
                'assets': []}
    for trial,label,title,color in trials:
        captures=root/trial/'captures'
        final=sorted(captures.glob('*_completed/capture.json'))[-1]
        final_meta=json.loads(final.read_text())
        target_name='02_encoder_drift.png' if trial.startswith('baseline') else '03_slam_return.png'
        shutil.copy2(final.parent/'rviz.png', output/target_name)
        manifest['assets'].append({'file':target_name,'source':str((final.parent/'rviz.png').relative_to(root)),'utc':final_meta['captured_at_utc']})
        if trial=='slam_feedback_12m':
            setup=sorted((root/'captures').glob('*_smoke_complete/capture.json'))[-1]
            shutil.copy2(setup.parent/'gazebo.png',output/'01_robot_setup.png')
            manifest['assets'].append({'file':'01_robot_setup.png','source':str((setup.parent/'gazebo.png').relative_to(root)),
                'note':'Closer robot view at smoke-test completion; same imported robot geometry.'})
        recording=sorted((root/'videos').glob('*_'+label+'/recording.json'))[-1]
        video=json.loads(recording.read_text())
        ready=json.loads(sorted(captures.glob('*_ready/capture.json'))[0].read_text())
        beginning=(datetime.fromisoformat(ready['captured_at_utc'])-datetime.fromisoformat(video['started_at_utc'])).total_seconds()
        ending=(datetime.fromisoformat(final_meta['captured_at_utc'])-datetime.fromisoformat(video['started_at_utc'])).total_seconds()
        intervals=[[max(0,beginning-1),beginning+11],[max(beginning+11,ending-22),ending+2]]
        name='05_encoder_highlights.mp4' if trial.startswith('baseline') else '06_slam_highlights.mp4'
        count=excerpt(recording.parent/'gazebo_rviz.mp4',output/name,intervals)
        manifest['assets'].append({'file':name,'source':str((recording.parent/'gazebo_rviz.mp4').relative_to(root)),
            'source_wall_time_intervals_seconds':intervals,'frames':count,'encoded_eos_verified':True})
        print(name,count,'frames',flush=True)
    fig,axs=plt.subplots(1,2,figsize=(11,4.8),constrained_layout=True)
    returns=[]
    for trial,label,title,color in trials:
        rows=json.loads((root/trial/'trajectory.json').read_text())
        truth=np.array([v['truth'] for v in rows]);truth[:,:2]-=truth[0,:2].copy()
        m=json.loads((root/trial/'metrics.json').read_text());returns.append(m['truth_return_distance_m']*100)
        axs[0].plot(truth[:,0],truth[:,1],color=color,lw=2,label=title)
        axs[0].scatter(truth[-1,0],truth[-1,1],color=color,marker='x',s=65)
    axs[0].plot([0,1.2,1.2,0,0],[0,0,1.2,1.2,0],ls='--',color='gray',lw=1,label='Commanded square')
    axs[0].scatter(0,0,color='black',s=30,label='Start')
    axs[0].set(title='Actual simulated paths',xlabel='Relative world x [m]',ylabel='Relative world y [m]');axs[0].axis('equal');axs[0].legend(fontsize=8);axs[0].grid(alpha=.2)
    bars=axs[1].bar(['Encoder feedback','SLAM feedback'],returns,color=[t[3] for t in trials],width=.55)
    axs[1].bar_label(bars,labels=[f'{x:.1f} cm' for x in returns],padding=4)
    axs[1].set(title='Actual distance from start after loop',ylabel='Return distance [cm]',ylim=(0,max(returns)*1.2));axs[1].grid(axis='y',alpha=.2)
    fig.suptitle('R4 1.2 m square comparison | one simulated trial per condition\nSame physical parameters; changed control feedback only. Mass causality untested.',fontsize=11)
    fig.savefig(output/'04_comparison.png',dpi=220)
    manifest['assets'].append({'file':'04_comparison.png','source':'Measured trajectory.json and metrics.json for both trials','derived_figure':True})
    (output/'selection.json').write_text(json.dumps(manifest,indent=2))
    print(output,flush=True)


if __name__=='__main__':
    main()
