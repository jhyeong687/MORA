#!/usr/bin/env python3
"""Record actual Gazebo/RViz windows as H.264 MP4 with frame timestamps."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import signal
import subprocess
import time

from capture_visuals import composite_capture
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPainter, QColor, QFont
from PyQt5.QtWidgets import QApplication
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('label')
    parser.add_argument('--fps', type=int, default=8)
    parser.add_argument('--seconds', type=float, default=1800)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    started = datetime.now(timezone.utc)
    output = root/'results'/f'research_{started.astimezone():%Y%m%d}'/'videos'/f'{started:%Y%m%dT%H%M%SZ}_{args.label}'
    output.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    Gst.init(None)
    width, height, header = 1600, 960, 36
    pipeline = Gst.parse_launch(f'appsrc name=frames is-live=false block=true format=time '
        f'caps=video/x-raw,format=RGB,width={width},height={height},framerate={args.fps}/1 '
        '! queue max-size-buffers=3 ! videoconvert '
        '! x264enc tune=zerolatency speed-preset=ultrafast bitrate=3500 '
        '! video/x-h264,stream-format=avc,alignment=au ! mp4mux '
        f'! filesink location="{output}/gazebo_rviz.mp4"')
    source = pipeline.get_by_name('frames')
    pipeline.set_state(Gst.State.PLAYING)
    active = True
    def stop(*_):
        nonlocal active
        active = False
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    start = time.monotonic()
    frames = 0
    windows = {}
    index = (output/'frames.jsonl').open('w')
    metadata = {'label': args.label, 'started_at_utc': started.isoformat(),
        'source': 'Actual Xwayland compositor window pixels; aspect-preserving resize into two labeled panels.',
        'clock': 'Wall time; per-frame UTC and monotonic times in frames.jsonl. Simulation may run slower.',
        'fps_target': args.fps, 'size': [width, height], 'audio': False, 'status': 'recording'}
    (output/'recording.json').write_text(json.dumps(metadata, indent=2))
    cfg = root/'generated/resolved.json'
    if cfg.exists():
        (output/'configuration_at_start.json').write_text(cfg.read_text())
    print(f'Recording: {output}/gazebo_rviz.mp4', flush=True)
    try:
        while active and time.monotonic()-start < args.seconds:
            if frames % args.fps == 0:
                tree = subprocess.check_output(['xwininfo', '-root', '-tree'], text=True)
                windows = {}
                for key, pattern in [('Gazebo', r'(0x[0-9a-f]+) "Gazebo Sim": \("gz-sim-gui"'),
                                     ('RViz', r'(0x[0-9a-f]+) "[^"\n]*RViz": \("rviz2"')]:
                    match = re.search(pattern, tree)
                    if match:
                        windows[key] = int(match.group(1), 16)
            frame_time = time.monotonic()-start
            utc = datetime.now(timezone.utc).isoformat()
            frame = QImage(width, height, QImage.Format_RGB888)
            frame.fill(QColor('#161a20'))
            painter = QPainter(frame)
            painter.setPen(Qt.white)
            painter.setFont(QFont('Sans', 11))
            painter.drawText(12, 24, f'Gazebo | {args.label} | UTC {utc}')
            painter.drawText(width//2+12, 24, 'RViz | SLAM map and trajectory')
            for column, key in enumerate(('Gazebo', 'RViz')):
                if key not in windows:
                    painter.drawText(column*width//2+20, 75, 'Waiting for application window')
                    continue
                pixmap = composite_capture(windows[key])
                if pixmap.isNull():
                    continue
                pixmap = pixmap.scaled(width//2-8, height-header, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(column*width//2+(width//2-pixmap.width())//2,
                    header+(height-header-pixmap.height())//2, pixmap)
            painter.end()
            bits = frame.bits()
            bits.setsize(frame.sizeInBytes())
            data = bytes(bits)
            buf = Gst.Buffer.new_allocate(None, len(data), None)
            buf.fill(0, data)
            buf.pts = int(frame_time*Gst.SECOND)
            buf.duration = Gst.SECOND//args.fps
            if source.emit('push-buffer', buf) != Gst.FlowReturn.OK:
                raise RuntimeError('Video encoder stopped accepting frames')
            if frames == 0:
                frame.save(str(output/'preview.png'))
            index.write(json.dumps({'frame': frames, 'wall_seconds': frame_time, 'utc': utc,
                'windows': windows})+'\n')
            index.flush()
            frames += 1
            app.processEvents()
            time.sleep(max(0, min(1/args.fps, (frames/args.fps)-(time.monotonic()-start))))
    finally:
        source.emit('end-of-stream')
        msg = pipeline.get_bus().timed_pop_filtered(20*Gst.SECOND, Gst.MessageType.EOS | Gst.MessageType.ERROR)
        metadata.update({'status': 'complete' if msg and msg.type == Gst.MessageType.EOS else 'encoder_error',
            'frames': frames, 'duration_wall_seconds': time.monotonic()-start,
            'ended_at_utc': datetime.now(timezone.utc).isoformat()})
        if msg and msg.type == Gst.MessageType.ERROR:
            metadata['encoder_error'] = str(msg.parse_error())
        pipeline.set_state(Gst.State.NULL)
        index.close()
        (output/'recording.json').write_text(json.dumps(metadata, indent=2))
        print(json.dumps({'directory': str(output), **metadata}, indent=2), flush=True)


if __name__ == '__main__':
    main()
