# -*- coding: utf-8 -*-


import os
import shutil
import subprocess
import dropbox
import pyqrcode

from datetime import datetime


import ConfigParser
config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

APP_KEY = config.get('Dropbox','app_key')
APP_SECRET = config.get('Dropbox','app_secret')
APP_TOKEN = config.get('Dropbox','app_token')

REC_FPS = config.getint('Recorder','rec_fps')

ROOT_FOLDER = config.get('System','root_folder')
REC_FOLDER = config.get('System','rec_folder')


def clearRecFolder(folder, rec_timestamps, rec_fps=REC_FPS):
    ms_per_frame = 1000/rec_fps

    rec_timestamps = [int(round(x/ms_per_frame))*(ms_per_frame) for x in rec_timestamps] # rounds each timestamp to closest 20
    rec_timestamps = [os.path.join(folder,'%06d.jpg' % x) for x in rec_timestamps] # create filenames from timestamps

    all_recorded_files = [os.path.join(folder,f) for f in sorted(os.listdir(folder))]

    deleted = 0
    for f in all_recorded_files:
        if f not in rec_timestamps:
            deleted += 1
            os.remove(f)
    # print('deleted', deleted, 'files of', len(all_recorded_files), 'remaining', (len(all_recorded_files) - deleted))
    print('{} deleted {} files of {}, remaining {}'.format(datetime.now(), deleted, len(all_recorded_files), (len(all_recorded_files) - deleted)))


def buildVideo(folder, video_path, rec_timestamps, rec_fps=REC_FPS):
    clearRecFolder(folder, rec_timestamps)

    outputframes = [os.path.join(folder,f) for f in sorted(os.listdir(folder))]

    # rename outputframes
    for i in range(len(outputframes)):
        os.rename(outputframes[i], (os.path.join(folder,'%06d.jpg'%(30+i+1))))

    # copy trailer frames
    trailer_folder = os.path.join(ROOT_FOLDER,'img', 'trailer')
    trailer_frames = [os.path.join(trailer_folder,f) for f in sorted(os.listdir(trailer_folder))]
    for f in trailer_frames:
        shutil.copy(f, REC_FOLDER)

    # create mp4
    subprocess.call([
        '/usr/local/bin/ffmpeg',
        '-v', '16',
        '-y',
        '-framerate', '24',
        '-i', '/var/tmp/rec/%06d.jpg',
        '-c:v', 'libx264',
        '-preset', 'faster',
        '-pix_fmt', 'yuv420p',
        video_path
    ])


# TODO: implement abstract upload class
def uploadToDropbox(local_path, app_key=APP_KEY, app_secret=APP_SECRET, app_token=APP_TOKEN):

    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
    client = dropbox.client.DropboxClient(app_token)

    f = open(local_path, 'rb')
    filename = 'videos/cdmkk_%s.mp4' % (datetime.now().strftime('%Y%m%d_%H%M%S'),)
    client.put_file(filename, f)
    response = client.share(filename)
    return response['url']

def generateQrCode(url, folder):
    # creating qrcode from url
    url = pyqrcode.create(url)
    qr_code_path = os.path.join(folder,'code.png')
    url.png(qr_code_path, scale=1) #scale=1 means: 1 little square is 1px
    return qr_code_path
