#!/usr/bin/env python
'''
Find's all videos in a source dir
Converts them to mp4's in target dir
Uploads them to s3 url in final target dir

And archives successful conversions
'''

import sys
import os
import subprocess
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S'
)
logger = logging.getLogger(__name__)

OUTPUT_SIZE = "scale=-1:540"
OUTPUT_BITRATE = "400K"
s3cmd = '/usr/local/bin/s3cmd'

# convert_and_upload.py "Penguin Beach return cams" dpawasi "/External HD/All Cams" s3://penguinsdpawwagovau/beach_return_cams/
source = os.path.abspath(sys.argv[1])       # "Penguin Beach return cams"
target = os.path.abspath(sys.argv[2])       # "dpawasi/s3_penguins"
archive_mov = os.path.abspath(sys.argv[3])  # "/Volumes/Penguin External/Penguins/Cams" or testing "/External HD/All Cams"
uploaded = target.replace(target.split('/')[-1], 's3_uploaded')
failed = target.replace(target.split('/')[-1], 's3_failed')

if not os.path.exists(uploaded):
    logger.debug('Folder Does not exist: {}'.format(uploaded))
    sys.exit()

if not os.path.exists(archive_mov):
    logger.debug('Folder Does not exist: {}'.format(archive_mov))
    sys.exit()

if not os.path.exists(failed):
    logger.debug('Folder Does not exist: {}'.format(failed))
    sys.exit()

if len(sys.argv) == 5:
    s3_target = sys.argv[4]                 # s3://penguinsdpawwagovau/beach_return_cams/

logger.debug('1: {}\n2: {}\n3: {}\n'.format(sys.argv[1], sys.argv[2], sys.argv[3]))

# filename:          /home/jawaidm/projects/penguins/dpawasi/Penguin Beach return cams/SandBar/2014-11-13/14-11-2013 05 TL SandBar.mov
# destination:       /home/jawaidm/projects/penguins/dpawasi/dpawasi/s3_penguins/14-11-2013_05_tl_sandbar.mov_mp4
# clean_destination: /home/jawaidm/projects/penguins/dpawasi/dpawasi/s3_penguins/14-11-2013_05_tl_sandbar.mp4

files = subprocess.check_output(["find", source, "-name", "*.mov"])
files = files.strip().split("\n")
files = [file_name for file_name in files if file_name] # strip empty strings in list
for filename in files:
    destination = os.path.join(target, os.path.basename(filename).lower().replace(" ", "_") + "_mp4")
    clean_destination = os.path.splitext(destination)[0] + ".mp4"

    logger.debug(' filename: {0}\n destination: {1}\n clean_destination: {2}\n'.format(filename, destination, clean_destination))

    #import ipdb; ipdb.set_trace()
    try:
        cmd = ["ffmpeg", "-i", filename, "-y", "-b:v", OUTPUT_BITRATE, "-vf",
            OUTPUT_SIZE, "-movflags", "faststart", "-profile:v", "main",
            "-vcodec", "libx264", "-f", "mp4", destination]

        if os.uname()[1] == 'Penguins-Mac-mini.local':
            logger.debug('Converting File: {}\n'.format(' '.join(cmd)))
            ret_conv = subprocess.call(cmd)
        else:
            # for testing
            logger.debug('IN TEST MODE')
            ret_conv = subprocess.call(['touch', destination])

        if ret_conv == 0:
            # rename from .mov_mp4 to .mp4 if conversion successful
            subprocess.check_call(["mv", "-v", destination, clean_destination])

        if os.path.exists(clean_destination):
            # upload to s3
            cmd_s3 = [s3cmd, "put", clean_destination, s3_target]
            ret_s3 = subprocess.call(cmd_s3)

            if ret_s3 == 0:
                # mv to s3_uploaded dir
                cmd_done = ['mv', clean_destination, clean_destination.replace(target, uploaded)]
                ret_done = subprocess.call(cmd_done)
                if ret_done != 0: logger.debug('Failed to move file {0} to {1}'.format(target, uploaded))

                # mv raw .mov file to archive dir
                file_mov = filename.split(source)[1].split('/')[-1]                 # '15-11-2013 05 TL SandBar.mov'
                sub_path = os.sep.join(filename.split(source)[1].split('/')[-3:-1]) # 'SandBar/2014-11-15'
                archive_dest = '/'.join([archive_mov, sub_path, file_mov])          # '/External HD/All Cams/SandBar/2014-11-15/15-11-2013 05 TL SandBar.mov'

                # create archive dir
                archive_path = '/'.join(archive_dest.split('/')[:-1])
                if not os.path.exists(archive_path):
                    ret_path = subprocess.call(['mkdir', '-p', archive_path])

                cmd_mov = ['mv', filename, archive_dest]
                ret_mov = subprocess.call(cmd_mov)
                if ret_mov == 0:
                    # check if source/../date_folder is now empty, if so rm the date_folder
                    date_folder = '/'.join(filename.split('/')[:-1])
                    ret_date = subprocess.check_output(['ls', date_folder])
                    if ret_date == '':
                        subprocess.call(['rm', '-rf', date_folder])
                        logger.debug('Removed Date Folder {0}'.format(date_folder))
                else:
                    logger.debug('Failed to archive file {0} to {1}'.format(target, uploaded))


            else:
                # move file to failed folder
                logger.debug('Failed to upload file {0} to S3 Server. Moving file to {1}'.format(target, failed))
                ret_fail = subprocess.call(['mv', clean_destination, clean_destination.replace(target, failed)])
                if ret_fail != 0: logger.debug('Failed to move file {0} to {1}'.format(target, failed))
        else:
            logger.debug('Failed to convert file: {}'.format(filename))

    except Exception as e:
        logger.debug(e)

    logger.debug('\n________________________________________________________________________________________________________\n')

