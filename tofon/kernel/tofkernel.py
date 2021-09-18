import sys #TODO pkg path in panel
packages_path = '/home/user/.local/lib/python3.9/site-packages/'
sys.path.insert(0, packages_path)

import numpy as np
from numba import jit
import math

# raw(x, y, rgb, event, color&depth)
# image(multip*x, multip*y, rgb)
# channel: 0, 1, 2
# frame >= 1
# multip >= 1
@jit(nopython=True)
def fill(raw, image, channel, frame, multip):
    for ix, col in enumerate(image):
        for iy, px in enumerate(col):
            rx, ry = ix // multip, iy // multip
            ex, ey = ix  % multip, iy  % multip
            multi_shift = ex * multip + ey
            frame_shift = (frame - 1) * multip ** 2 # frame starts with 1
            event_shift = frame_shift + multi_shift
            c = channel             # target color
            p, f = (c+1)%3, (c+2)%3 # path length and fall-off channels
            raw[ry, rx, c, event_shift, 0] = px[c]
            if px[f] != 0:
                raw[ry, rx, c, event_shift, 1] = px[p]/px[f]

@jit(nopython=True)
def raw_sort(raw):
    for x, col in enumerate(raw):
        for y, px in enumerate(col):
            for c, rgb in enumerate(px):
                raw[x,y,c,:] = rgb[rgb[:, 1].argsort()]

# bucket(t, x, y, rgb)
@jit(nopython=True, parallel=True)
def bucket_sort(bucket, raw, pspf):
    unit_length  = pspf * 1e-12 * 3e8
    for x, col in enumerate(raw):
        print(x, len(raw))
        for y, px in enumerate(col):
            for c, rgb in enumerate(px):
                for event in rgb:
                    if event[0] == 0.0:
                        continue
                    t = math.floor(event[1] / unit_length)
                    if 0 <= t < bucket.shape[0]:
                        bucket[t, x, y, c] += event[0]
