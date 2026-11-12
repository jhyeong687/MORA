#!/usr/bin/env python3
"""Capture the actual X11 simulation windows with UTC-stamped provenance."""
import argparse
import ctypes as C
import ctypes.util
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys

os.environ['QT_QPA_PLATFORM'] = 'xcb'
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage, QPixmap


def composite_capture(window):
    # On GNOME/Xwayland the on-screen drawable can be black; read the
    # compositor's backing pixmap instead, without modifying the pixels.
    class XImage(C.Structure):
        _fields_ = [('width', C.c_int), ('height', C.c_int), ('xoffset', C.c_int),
                    ('format', C.c_int), ('data', C.c_void_p), ('byte_order', C.c_int),
                    ('bitmap_unit', C.c_int), ('bitmap_bit_order', C.c_int),
                    ('bitmap_pad', C.c_int), ('depth', C.c_int),
                    ('bytes_per_line', C.c_int), ('bits_per_pixel', C.c_int),
                    ('red_mask', C.c_ulong), ('green_mask', C.c_ulong), ('blue_mask', C.c_ulong)]
    x = C.CDLL(ctypes.util.find_library('X11'))
    comp = C.CDLL(ctypes.util.find_library('Xcomposite'))
    x.XOpenDisplay.argtypes = [C.c_char_p]
    x.XOpenDisplay.restype = C.c_void_p
    display = x.XOpenDisplay(None)
    comp.XCompositeNameWindowPixmap.argtypes = [C.c_void_p, C.c_ulong]
    comp.XCompositeNameWindowPixmap.restype = C.c_ulong
    pix = comp.XCompositeNameWindowPixmap(display, window)
    x.XGetGeometry.argtypes = [C.c_void_p, C.c_ulong, C.POINTER(C.c_ulong),
        C.POINTER(C.c_int), C.POINTER(C.c_int), C.POINTER(C.c_uint),
        C.POINTER(C.c_uint), C.POINTER(C.c_uint), C.POINTER(C.c_uint)]
    root, px, py = C.c_ulong(), C.c_int(), C.c_int()
    width, height, border, depth = (C.c_uint() for _ in range(4))
    x.XGetGeometry(display, pix, C.byref(root), C.byref(px), C.byref(py),
        C.byref(width), C.byref(height), C.byref(border), C.byref(depth))
    x.XGetImage.argtypes = [C.c_void_p, C.c_ulong, C.c_int, C.c_int, C.c_uint, C.c_uint, C.c_ulong, C.c_int]
    x.XGetImage.restype = C.POINTER(XImage)
    raw = x.XGetImage(display, pix, 0, 0, width.value, height.value, C.c_ulong(-1).value, 2)
    result = QPixmap()
    if raw and raw.contents.bits_per_pixel == 32:
        data = raw.contents
        pixels = C.string_at(data.data, data.bytes_per_line*data.height)
        result = QPixmap.fromImage(QImage(pixels, data.width, data.height,
            data.bytes_per_line, QImage.Format_RGB32).copy())
    if raw:
        x.XDestroyImage.argtypes = [C.POINTER(XImage)]
        x.XDestroyImage(raw)
    x.XFreePixmap.argtypes = [C.c_void_p, C.c_ulong]
    x.XFreePixmap(display, pix)
    x.XCloseDisplay.argtypes = [C.c_void_p]
    x.XCloseDisplay(display)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('label')
    parser.add_argument('--note', default='')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    stamp = datetime.now(timezone.utc)
    output = args.output or root/'results'/f'research_{stamp.astimezone():%Y%m%d}'/'captures'/f'{stamp:%Y%m%dT%H%M%SZ}_{args.label}'
    output.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv[:1])
    screen = app.primaryScreen()
    tree = subprocess.check_output(['xwininfo', '-root', '-tree'], text=True)
    (output/'windows.txt').write_text(tree)
    captures = []
    for key, pattern in [('gazebo', r'(0x[0-9a-f]+) "Gazebo Sim": \("gz-sim-gui"'),
                         ('rviz', r'(0x[0-9a-f]+) "[^"\n]*RViz": \("rviz2"')]:
        match = re.search(pattern, tree)
        if not match:
            captures.append({'window': key, 'error': 'window not found'})
            continue
        pixmap = composite_capture(int(match.group(1), 16))
        path = output/f'{key}.png'
        ok = not pixmap.isNull() and pixmap.save(str(path))
        nonblank = False
        if ok:
            pixels = pixmap.toImage()
            colors = {pixels.pixelColor(px, py).rgb() for px in range(0,pixels.width(),max(1,pixels.width()//20))
                      for py in range(0,pixels.height(),max(1,pixels.height()//20))}
            nonblank = len(colors)>3
        captures.append({'window': key, 'window_id': match.group(1), 'file': path.name,
                         'saved': ok, 'usable_nonblank': nonblank,
                         'width': pixmap.width(), 'height': pixmap.height()})
    config = root/'generated/resolved.json'
    if config.exists():
        (output/'configuration.json').write_text(config.read_text())
    record = {'captured_at_utc': stamp.isoformat(), 'label': args.label,
              'note': args.note, 'source': 'actual application window pixels, unedited',
              'captures': captures}
    (output/'capture.json').write_text(json.dumps(record, indent=2))
    print(json.dumps({'directory': str(output), **record}, indent=2))


if __name__ == '__main__':
    main()
