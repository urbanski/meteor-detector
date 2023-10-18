#!/bin/bash

v4l2-ctl --set-ctrl=auto_exposure=1
v4l2-ctl --set-ctrl=gain=0
v4l2-ctl --set-ctrl=brightness=0
v4l2-ctl --set-ctrl=sharpness=6
v4l2-ctl --set-ctrl=exposure_time_absolute=5000
v4l2-ctl --device /dev/video0 --all