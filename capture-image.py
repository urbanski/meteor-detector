#!/usr/bin/env python3
import cv2
import os
import time
import json
import sys
import datetime

def get_sunrise_sunset():
    fptr = open('/etc/astronomy/sunrise-sunset.json', 'r')
    data = fptr.read()
    fptr.close()

    jobj = json.loads(data)
    sunrise = jobj['results']['astronomical_twilight_begin']
    sunset = jobj['results']['astronomical_twilight_end']

    # convert sunrise in RFC3339 format to a unix timestamp
    sunrise = datetime.datetime.strptime(sunrise, '%Y-%m-%dT%H:%M:%S%z')
    sunrise = int(sunrise.timestamp())

    sunset = datetime.datetime.strptime(sunset, '%Y-%m-%dT%H:%M:%S%z')
    sunset = int(sunset.timestamp())

    return sunrise, sunset


# set force=True if the --force command line arg has been passed
force = False
if len(sys.argv) > 1:
    if sys.argv[1] == "--force":
        force = True

# get the time
currentTime = time.time()
sunrise, sunset = get_sunrise_sunset()

if sunrise < currentTime < sunset:
    if not force:
        print("It's daytime. Exiting.")
        sys.exit(1)

video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    raise Exception("Could not open video device")

# setup grayscale capture in YUYV mode
fourcc = cv2.VideoWriter_fourcc(*'YUYV')
video_capture.set(cv2.CAP_PROP_FOURCC, fourcc)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Read picture. ret === True on success
ret, frame = video_capture.read()
video_capture.release()

# set outputPath to current working directory
outputPath = "/var/images"

# set currentTime to the current unix timestamp in UTC
currentTime = int(time.time())

gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

cv2.imwrite(os.path.join(outputPath, "skylab-gpi-%d.png" % currentTime), gray_frame)