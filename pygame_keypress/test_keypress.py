# -*- coding: utf-8 -*-

import pygame

import os, subprocess, time
import dropbox, pyqrcode

from multiprocessing import Manager, Process, Lock
from datetime import datetime


import ConfigParser
config = ConfigParser.ConfigParser()
config.readfp(open('magic.cfg'))

# only on raspi
if config.getboolean('System','camera'):
    import picamera
if config.getboolean('System','gpio'):
    import RPi.GPIO as GPIO
    # init GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.OUT)



# not sure alexa stole this code from the internets
def aspect_scale(img,(bx,by)):
    """ Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio """
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    return pygame.transform.scale(img, (int(sx),int(sy)))


# displays a single frame from the Neubronner Film
def show_image(screen, clock, frames, frame, width, height):
    image = frames[frame-1]
    img = aspect_scale(pygame.image.load(image), (width,height))
    # img = pygame.image.load(image)
    screen.blit(img,(0,0))

    # pygame.display.flip()
    pygame.display.update()

    # setting the max Framerate to 60 Hz according the the display (not sure which function is 'better')
    # clock.tick_busy_loop(60)
    clock.tick(60)
    # print(frame, 'FPS', int(clock.get_fps()), 'ms', ms_since_start)


def generateFilenamesForRecording(rec_duration, rec_fps):
    frame = 0
    timeout = False
    abort = False

    while not (timeout or abort):
        timeout = (frame >= (rec_duration * rec_fps))
        abort = os.path.exists('ABORT_RECORDING')
        filename = '/var/tmp/rec/%06d.jpg' % (1000 * frame / rec_fps,)
        yield filename
        frame += 1



def recordFrames(lock, width, height, rec_duration, rec_fps):
    # prevent processes from queueing up when the rec button is pressed while recording
    if os.path.exists('RECORD_LOCK'):
        print('{} - I\'m sorry Dave, I\'m afraid I can\'t start another recording…'.format(datetime.now()))
        return

    # only one recording
    lock.acquire()
    with open('RECORD_LOCK', 'a'): os.utime('RECORD_LOCK', None)

    if config.getboolean('System','gpio'):
        GPIO.output(7,True) # turn on led

    # cleanup recording directory
    filelist = [ f for f in os.listdir("/var/tmp/rec/") if f.endswith(".jpg") ]
    for f in filelist:
        os.remove('/var/tmp/rec/' + f)

    print('{} - record button pressed'.format(datetime.now()))

    # instantiate a camera object
    camera = picamera.PiCamera()
    # setting the camera up
    camera.resolution = (width,height)
    camera.framerate = rec_fps
    camera.hflip = True
    camera.vflip = True

    # record
    print('{} - start recording'.format(datetime.now()))

    camera.capture_sequence(
        generateFilenamesForRecording(rec_duration, rec_fps)
        ,use_video_port=True)

    camera.close() # gracefully shutdown the camera (freeing all resources)
    print('{} - finished recording'.format(datetime.now()))

    # release the lock and delete the lock file
    if config.getboolean('System','gpio'):
        GPIO.output(7,False) # turn off led
    os.remove('RECORD_LOCK')
    if os.path.exists('ABORT_RECORDING'): os.remove('ABORT_RECORDING')
    lock.release()



def buildVideo(folder, video_path, rec_timestamps, rec_fps):
    ms_per_frame = 1000/rec_fps

    rec_timestamps = [int(round(x/ms_per_frame))*(ms_per_frame) for x in rec_timestamps] # rounds each timestamp to closest 20
    rec_timestamps = [os.path.join(folder,'%06d.jpg' % x) for x in rec_timestamps] # create filenames from timestamps

    all_recorded_files = [os.path.join(folder,f) for f in sorted(os.listdir(folder))]

    # remove files that does not match the recorded ticks
    outputframes = []
    for f in all_recorded_files:
        if f in rec_timestamps:
            outputframes.append(f)
        else:
            os.remove(f)

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
def uploadToDropbox(local_path, app_key, app_secret, app_token):

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



if __name__ == '__main__':


    APP_KEY = config.get('Dropbox','app_key')
    APP_SECRET = config.get('Dropbox','app_secret')
    APP_TOKEN = config.get('Dropbox','app_token')

    WIDTH  = config.getint('Screen','width')
    HEIGHT = config.getint('Screen','height')
    FULLSCREEN = config.getboolean('Screen','fullscreen')

    ROOT_PATH = config.get('System', 'root_folder')
    RECORD_PATH = config.get('System', 'rec_folder')
    VIDEO_PATH = config.get('System','video_path')

    FRAMES_PATH = config.get('System','frames_folder')
    ALL_FRAMES = all_frames = [os.path.join(FRAMES_PATH,f) for f in sorted(os.listdir(FRAMES_PATH))]


    REC_DURATION = config.getint('Recorder','rec_duration') # seconds
    REC_FPS = config.getint('Recorder','rec_fps')

    rec_timestamps = [0]
    first_rec_timestamp = -1


    print('{} - start magicKurbelKamera\nresolution: {} x {}'.format(datetime.now(), WIDTH,HEIGHT))

    manager = Manager()

    # Lock Object for recording, only one recording should take place at once
    rec_lock = Lock()
    # remove an old lock-file (debris from a crash)
    if os.path.exists('RECORD_LOCK'): os.remove('RECORD_LOCK')
    if os.path.exists('ABORT_RECORDING'): os.remove('ABORT_RECORDING')


    # pygame setup
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption('MagicKurbelKamera') # set a window title
    if FULLSCREEN: screen = pygame.display.set_mode((WIDTH,HEIGHT), pygame.FULLSCREEN)
    else:          screen = pygame.display.set_mode((WIDTH,HEIGHT))

    background = pygame.Surface(screen.get_size()) # dunno
    background.fill((255,255,255)) # black background
    background = background.convert() # dunno
    # end of pygame setup

    # show init screen
    bg = pygame.image.load(os.path.join(ROOT_PATH,'img','initial.png'))
    screen.blit(bg,(0,0))
    pygame.display.update()
    clock.tick(60)


    frame = 1
    mainloop = True

    # magic ahead
    while mainloop:
        # global REC_TIMESTAMPS, FIRST_REC_TIMESTAMP

        for event in pygame.event.get():

            # pygame window closed by user
            if event.type == pygame.QUIT: mainloop = False

            # key is released
            elif event.type == pygame.KEYUP:

                # left and right arrow
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    # increment or decrement the actual frame number
                    if event.key == pygame.K_LEFT:   frame -= 1
                    elif event.key == pygame.K_RIGHT: frame += 1

                    frame = (frame % len(ALL_FRAMES))
                    if frame == 0: frame = len(ALL_FRAMES)

                    show_image(screen, clock, ALL_FRAMES, frame, WIDTH, HEIGHT)

                    # count ms since first tick
                    if first_rec_timestamp == -1:
                        first_rec_timestamp = pygame.time.get_ticks()
                        rec_timestamps = [0]
                    else:
                        rec_timestamps.append(pygame.time.get_ticks() - first_rec_timestamp)


                # escape
                elif event.key == pygame.K_ESCAPE:
                    mainloop = False # user pressed ESC

                # d
                elif event.key == pygame.K_d:

                    # show development screen
                    bg = pygame.image.load(os.path.join(ROOT_PATH,'img','development.png'))
                    screen.blit(bg,(0,0))
                    pygame.display.update()

                    print('{} - Start building video'.format(datetime.now()))
                    buildVideo(RECORD_PATH, VIDEO_PATH, rec_timestamps, REC_FPS)
                    print('{} - Finished building video'.format(datetime.now()))
                    print('{} - Start uploading'.format(datetime.now()))
                    url = uploadToDropbox(VIDEO_PATH, APP_KEY, APP_SECRET, APP_TOKEN)
                    print('{} - Finished uploading'.format(datetime.now()))

                    # generate qrcode and display it on background image
                    generateQrCode(url, os.path.join(ROOT_PATH,'img') )
                    bg = pygame.image.load(os.path.join(ROOT_PATH,'img','bg.png'))
                    screen.blit(bg,(0,0))
                    img = aspect_scale(pygame.image.load(qr_code_path), (111,111))
                    screen.blit(img,(310,163))
                    pygame.display.update()
                    clock.tick(60)


                # r
                elif config.getboolean('System','camera') and event.key == pygame.K_r:
                    first_rec_timestamp = pygame.time.get_ticks()
                    rec_timestamps = []

                    # print('r FIRST_REC_TIMESTAMP', FIRST_REC_TIMESTAMP)
                    RECORDER = Process(target=recordFrames, args=(rec_lock,WIDTH,HEIGHT,REC_DURATION,REC_FPS))
                    RECORDER.start()

                elif event.key == pygame.K_s:
                    print('{} - ABORT_RECORDING'.format(datetime.now()))
                    with open('ABORT_RECORDING', 'a'): os.utime('ABORT_RECORDING', None)

