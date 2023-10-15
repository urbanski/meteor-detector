#!/bin/bash

v4l2-ctl --set-ctrl=auto_exposure=1
v4l2-ctl --set-ctrl=exposure_time_absolute=2500
v4l2-ctl --device /dev/video0 --all