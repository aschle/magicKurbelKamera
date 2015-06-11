# -*- coding: utf-8 -*-


import os
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
    print('deleted', deleted, 'files of', len(all_recorded_files), 'remaining', (len(all_recorded_files) - deleted))



def buildVideo(folder, video_path, rec_timestamps, rec_fps=REC_FPS):
    clearRecFolder(folder, rec_timestamps)

    outputframes = [os.path.join(folder,f) for f in sorted(os.listdir(folder))]

    # rename outputframes
    for i in range(len(outputframes)):
        os.rename(outputframes[i], (os.path.join(folder,'%06d.jpg'%(i+1))))

    # create mp4
    os.chdir('/var/tmp/rec/')
    subprocess.call([
        '/usr/local/bin/ffmpeg',
        '-y',
        '-framerate', '16',
        '-i',         '%06d.jpg',
        '-c:v',       'libx264',
        '-pix_fmt',   'yuv420p',
        video_path])


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
