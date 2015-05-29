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

if len(sys.argv) != 4:
    logger.info('Usage: "./convert_and_upload.py /Volumes/Server HD/Users/penguin /Volumes/Macintosh HD2/dpawasi s3://penguinsdpawwagovau/beach_return_cams_2/"')
    sys.exit()
else:
    ROOT_EXTERNAL = sys.argv[1]     # '/Volumes/Server HD/Users/penguin'
    ROOT_LOCAL = sys.argv[2]        # '/Volumes/Macintosh HD2/dpawasi'
    s3_target = sys.argv[3]         # s3://penguinsdpawwagovau/beach_return_cams_2/

source      = os.sep.join([ROOT_EXTERNAL,'Penguin Beach return cams'])
archive_mov = os.sep.join([ROOT_EXTERNAL,'Penguin Beach return cams-Processed'])
uploaded    = os.sep.join([ROOT_LOCAL,'s3_uploaded'])
target      = os.sep.join([ROOT_LOCAL,'s3_penguins'])
failed      = os.sep.join([ROOT_LOCAL,'s3_failed'])

def main():
    logger.info('In Main ...')
    if not path_exists():
        sys.exit()

    logger.info('Process ...')
    process_videos()
    logger.info('S3 Upload ...')
    confirm_s3_upload()
    delete_old_videos()


def path_exists():
    #import ipdb; ipdb.set_trace()
    if not os.path.exists(uploaded):
        logger.error('Folder Does not exist: {}'.format(uploaded))
        return False
    elif not os.path.exists(archive_mov):
        logger.error('Folder Does not exist: {}'.format(archive_mov))
        return False
    elif not os.path.exists(failed):
        logger.error('Folder Does not exist: {}'.format(failed))
        return False

    return True


def convert_video(filename, destination, clean_destination):
    cmd = ["ffmpeg", "-i", filename, "-y", "-b:v", OUTPUT_BITRATE, "-vf",
        OUTPUT_SIZE, "-movflags", "faststart", "-profile:v", "main",
        "-vcodec", "libx264", "-f", "mp4", destination]

    if os.uname()[1] == 'Penguins-Mac-mini.local':
        logger.info('Converting File: {}\n'.format(' '.join(cmd)))
        ret_conv = subprocess.call(cmd)
    else:
        # for testing
        logger.debug('IN TEST MODE')
        ret_conv = subprocess.call(['touch', destination])

    ret = -1
    if ret_conv == 0:
        # rename from .mov_mp4 to .mp4 if conversion successful
        ret = subprocess.call(["mv", "-v", destination, clean_destination])

    return ret


def archive_mov_videos(filename):
    # mv raw .mov file to archive dir
    file_mov = filename.split(source)[1].split('/')[-1]                 # '15-11-2013 05 TL SandBar.mov'
    sub_path = os.sep.join(filename.split(source)[1].split('/')[-3:-1]) # 'SandBar/2014-11-15'
    archive_dest = '/'.join([archive_mov, sub_path, file_mov])          # '/Volumes/Server HD/Users/penguin/Penguin Beach return cams-Processed/SandBar/2014-11-15/15-11-2013 05 TL SandBa>

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
            logger.info('Removed Date Folder {0}'.format(date_folder))
    else:
        logger.error('Failed to archive file {0} to {1}'.format(filename, archive_dest))
        return 1

    return 0

def delete_old_videos(ndays='+7'):
    """ Delete files older than ndays """
    filetypes = {'mov': ['*.mov', archive_mov], 'mp4': ['*.mp4', uploaded]}
    for i in filetypes:
        filetype = filetypes[i][0]
        folder = filetypes[i][1]
        cmd_delete = 'find "' +  folder + '" -name ' + filetype + ' -mtime ' + ndays + ' -exec rm {} \;'
        print cmd_delete
        ret_del = subprocess.call(cmd_delete, shell=True)

    # Remove empty directories
    cmd_rmdir = 'find "' + archive_mov + '" -type d -empty -exec rmdir {} \;'
    ret_rm = subprocess.call(cmd_rmdir, shell=True)

def process_videos():
    files = subprocess.check_output(["find", source, "-name", "*.mov"])
    files = files.strip().split("\n")
    files = [file_name for file_name in files if file_name] # strip empty strings in list
    for filename in files:
        destination = os.path.join(target, os.path.basename(filename).lower().replace(" ", "_") + "_mp4")

        # change name date fmt from %d-%m-%Y --> %Y-%m-%d
        name = destination.split('/')[-1]
        nameparts=name.split('_')
        new_datefmt = '-'.join(nameparts[0].split('-')[::-1])
        if len(new_datefmt.split('-')[0]) != 4:
            logger.debug('Date format incorrect: Not Processing File. {}'.format(destination))
            continue

        new_name=new_datefmt + '_' + '_'.join(nameparts[1:])
        destination = destination.replace(name, new_name)

        clean_destination = os.path.splitext(destination)[0] + ".mp4"
        logger.debug(' filename: {0}\n destination: {1}\n clean_destination: {2}\n'.format(filename, destination, clean_destination))

        uploaded_destination = os.sep.join([uploaded, clean_destination.split(os.sep)[-1]])
        failed_destination = os.sep.join([failed, clean_destination.split(os.sep)[-1]])
        if os.path.exists(clean_destination) or os.path.exists(uploaded_destination) or os.path.exists(failed_destination):
            logger.info('File Already Converted. Archiving ...')
            archive_mov_videos(filename)
            continue

        try:
            convert_video(filename, destination, clean_destination)
            if os.path.exists(clean_destination):
                # upload to s3
                cmd_s3 = [s3cmd, "put", clean_destination, s3_target]
                ret_s3 = subprocess.call(cmd_s3)

                if ret_s3 == 0:
                    # mv to s3_uploaded dir
                    cmd_done = ['mv', clean_destination, uploaded_destination]
                    ret_done = subprocess.call(cmd_done)
                    if ret_done != 0: logger.error('Failed to move file {0} to {1}'.format(clean_destination, uploaded_destination))

                    archive_mov_videos(filename)

                else:
                    # move file to failed folder
                    logger.debug('Failed to upload file {0} to S3 Server. Moving file to {1}'.format(target, failed))
                    ret_fail = subprocess.call(['mv', clean_destination, clean_destination.replace(target, failed)])
                    if ret_fail != 0: logger.debug('Failed to move file {0} to {1}'.format(target, failed))
            else:
                # will be re-attempted next time script runs
                logger.debug('Failed to convert file: {}'.format(filename))

        except Exception as e:
            logger.debug(e)

        logger.debug('______________________________________________________________________________________________\n')


def confirm_s3_upload():
    # check for failed uploads and re-attempt
    logger.debug('_____________________________ File Upload Re-Attempt_______________________________________\n')
    s3_files = subprocess.check_output([s3cmd, 'ls', s3_target])
    s3_files = s3_files.strip().split('\n')
    s3_files = [i.split('/')[-1] for i in s3_files if i.endswith('.mp4')]
    s3_files.remove('') if '' in s3_files else s3_files

    folders = [target, failed]
    for folder in folders:
        local_files = subprocess.check_output(['ls', folder])
        local_files = local_files.strip().split('\n')
        local_files.remove('') if '' in local_files else local_files

        for local_file in local_files:
            if local_file in s3_files:
                # move to uploaded dir
                logger.debug('MOVING FILE to uploaded dir: {}'.format(local_file))
                cmd_mov = ['mv', folder + os.sep + local_file, uploaded + os.sep + local_file]
                ret_mov = subprocess.call(cmd_mov)
                if ret_mov != 0:
                    logger.debug('File move failed: {0} to {1} '.format(folder + os.sep + local_file, uploaded + os.sep + local_file))
            else:
                # upload to s3
                cmd_s3 = [s3cmd, "put", folder + os.sep + local_file, s3_target]
                # logger.debug(cmd_s3)
                ret_s3 = subprocess.call(cmd_s3)

                if ret_s3 != 0:
                    logger.debug('Atempted Re-upload of file to S3 Server Failed: {}'.format(folder + os.sep + local_file))


if __name__ == '__main__':
    main()
