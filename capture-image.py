#!/usr/bin/env python3
import cv2
import os
import time
import json
import sys
import datetime
import numpy as np

def capture_frame(cap):
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Failed to capture frame.")
    return cv2.cvtColor(frame, cv2.IMREAD_GRAYSCALE)


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
        print(sunset - currentTime)
        sys.exit(1)

video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    raise Exception("Could not open video device")

# setup grayscale capture in YUYV mode
fourcc = cv2.VideoWriter_fourcc(*'YUYV')
video_capture.set(cv2.CAP_PROP_FOURCC, fourcc)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 3264)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 2448)
video_capture.set(cv2.CAP_PROP_EXPOSURE, 10000)
video_capture.set(cv2.CAP_PROP_GAIN, 0)
#video_capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1000)

num_frames = 5
sleep_seconds = 1
print(f"Capturing {num_frames} frames, sleeping {sleep_seconds} seconds between each.")

# List to store captured frames
frames = []
for _ in range(num_frames):
    frames.append(capture_frame(video_capture))
    time.sleep(sleep_seconds)

# Close webcam
video_capture.release()

# Calculate consistent brightness mask across frames
brightness_threshold = 30  # was: 63, 127 | Adjust based on your specific needs.
enhancement_factor = 100
print(f"Using brightness threshold of {brightness_threshold}, enhancement factor of {enhancement_factor}")

# Initialize the mask to all ones (true)
star_mask = np.ones_like(frames[0], dtype=np.uint8)

# Update the mask based on each frame
for frame in frames:
    star_mask &= (frame > brightness_threshold)

# Average all frames (you can use sum too for more intensity)
combined_frame = np.sum(frames, axis=0, dtype=np.uint8)

# Enhance the potential star pixels by a factor

combined_frame = np.where(star_mask, combined_frame * enhancement_factor, 0)

# Clip the pixel values to [0, 255] range
combined_frame = np.clip(combined_frame, 0, 255)

# set outputPath to current working directory
outputPath = "/var/images"

# set currentTime to the current unix timestamp in UTC
currentTime = int(time.time())

gray_frame = cv2.cvtColor(combined_frame, cv2.COLOR_BGR2GRAY)
inverted_frame = 255 - gray_frame

outputFile = os.path.join(outputPath, "skylab-gpi-%d.png" % currentTime)
cv2.imwrite(outputFile, gray_frame)

outputFileInverted = os.path.join(outputPath, "skylab-gpi-inverted-%d.png" % currentTime)
cv2.imwrite(outputFileInverted, inverted_frame)

print(f"Wrote {outputFile}")
print(f"Wrote {outputFileInverted}")