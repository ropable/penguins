#!/usr/bin/env python
'''
Find's all videos in a source dir
Converts them to mp4's in target dir
Uploads them to s3 url in final target dir
'''

import sys
import os
import subprocess

OUTPUT_SIZE = "scale=-1:540"
OUTPUT_BITRATE = "400K"

source = os.path.abspath(sys.argv[1])
target = os.path.abspath(sys.argv[2])
if len(sys.argv) == 4:
    s3_target = sys.argv[3]

files = subprocess.check_output(["find", source, "-name", "*.mov"])
files = files.strip().split("\n")
for filename in files:
    destination = os.path.join(target, os.path.basename(filename).lower().replace(" ", "_") + "_mp4")
    clean_destination = os.path.splitext(destination)[0] + ".mp4"
    if os.path.exists(clean_destination):
        continue
    try:
        subprocess.check_call(["ffmpeg", "-i", filename, "-y", "-b:v", OUTPUT_BITRATE, "-vf",
                               OUTPUT_SIZE, "-movflags", "faststart", "-profile:v", "main",
                               "-vcodec", "libx264", "-f", "mp4", destination])
    except Exception as e:
        print(e)
    else:
        subprocess.check_call(["mv", "-v", destination, clean_destination])
        subprocess.check_call(["s3cmd", "sync", target + os.path.sep, s3_target])
