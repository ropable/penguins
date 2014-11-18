#!/usr/bin/env python
'''
Find's all videos in a source dir
compare these against those already uploaded to S3
and archive those that have already been uploaded

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

# ./dpawasi/penguins/utils/archive_uploaded.py dpawasi/s3_penguins

target = os.path.abspath(sys.argv[1])       # "s3_penguins"
uploaded = target.replace(target.split('/')[-1], 's3_uploaded')

s3cmd = '/usr/local/bin/s3cmd'
s3path = 's3://penguinsdpawwagovau/beach_return_cams/'


def compare_single():
    local_files = subprocess.check_output(['ls', target])
    local_files = local_files.strip().split('\n')

    for local_file in local_files:
        ret_file = subprocess.check_output([s3cmd, 'ls', s3path + local_file])
        s3_file = ret_file.strip().split('/')[-1]
        if local_file == s3_file:
            # move to uploaded dir
            logger.debug('MOVING FILE to uploaded dir: {}'.format(local_file))
            cmd_mov = ['mv', target + os.sep + local_file, uploaded + os.sep + local_file]
            ret_mov = subprocess.call(cmd_mov)
            if ret_mov != 0:
                logger.debug('File move failed: {0} to {1} '.format(target + os.sep + local_file, uploaded + os.sep + local_file))
        else:
            logger.debug('File not on S3 Server {}. FILE NOT MOVED.'.format(local_file))


def compare_all():
    s3_files = subprocess.check_output([s3cmd, 'ls', s3path])
    s3_files = s3_files.strip().split('\n')
    s3_files = [i.split('/')[-1] for i in s3_files if i.endswith('.mp4')]

    local_files = subprocess.check_output(['ls', target])
    local_files = local_files.strip().split('\n')

    for local_file in local_files:
        if local_file in s3_files:
            # move to uploaded dir
            logger.debug('MOVING FILE to uploaded dir: {}'.format(local_file))
            cmd_mov = ['mv', target + os.sep + local_file, uploaded + os.sep + local_file]
            ret_mov = subprocess.call(cmd_mov)
            if ret_mov != 0:
                logger.debug('File move failed: {0} to {1} '.format(target + os.sep + local_file, uploaded + os.sep + local_file))
        else:
            logger.debug('File not on S3 Server {}. FILE NOT MOVED.'.format(local_file))


if os.path.exists(uploaded):
    #compare_single()
    compare_all()
else:
    logger.debug('Folder Does not exist: {}'.format(uploaded))


