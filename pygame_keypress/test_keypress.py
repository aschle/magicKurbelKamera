# -*- coding: utf-8 -*-

import pygame

import os, subprocess, time, ConfigParser
import dropbox, pyqrcode

from multiprocessing import Manager, Process, Lock
from datetime import datetime


config = ConfigParser.ConfigParser()
config.readfp(open('magic.cfg'))

app_key = config.get('Dropbox','app_key')
app_secret = config.get('Dropbox','app_secret')
app_whatever = config.get('Dropbox','app_whatever')

fullscreen = config.getboolean('System','fullscreen')


# only on raspi
if config.getboolean('System','camera'):
    import picamera
if config.getboolean('System','gpio'):
    import RPi.GPIO as GPIO
    # init GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.OUT)



# global variables -- needs to be cleaned up (global is bad)

global FOLDER, ALL_FRAMES
FOLDER = os.path.join('/','var','tmp','frames')
ALL_FRAMES = all_frames = [os.path.join(FOLDER,f) for f in sorted(os.listdir(FOLDER))]

# print(len(os.listdir('/var/tmp/frames')))

global WIDTH, HEIGHT
WIDTH  = 450
HEIGHT = int(244 * WIDTH / 352)

global RECORDER, REC_DURATION, REC_FPS
REC_DURATION = 60 # seconds
REC_FPS = 50


global REC_TIMESTAMPS, FIRST_REC_TIMESTAMP
REC_TIMESTAMPS = [0]
FIRST_REC_TIMESTAMP = -1



def changeFolder(path):
    print('changeFolder', path)
    global FOLDER, ALL_FRAMES
    FOLDER = path
    ALL_FRAMES = [os.path.join(FOLDER,f) for f in sorted(os.listdir(FOLDER))]


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
def show_image(screen, clock, frame):
    # print(ALL_FRAMES[frame-1])
    # image = '/var/tmp/frames/NEUBR_28_%04d.jpg' % (frame,)
    image = ALL_FRAMES[frame-1]
    img = aspect_scale(pygame.image.load(image), (WIDTH,HEIGHT))
    # img = pygame.image.load(image)
    screen.blit(img,(0,0))

    # pygame.display.flip()
    pygame.display.update()

    # setting the max Framerate to 60 Hz according the the display (not sure which function is 'better')
    # clock.tick_busy_loop(60)
    clock.tick(60)
    # print(frame, 'FPS', int(clock.get_fps()), 'ms', ms_since_start)


def generateFilenamesForRecording():
    frame = 0
    timeout = False
    abort = False

    while not (timeout or abort):
        timeout = (frame >= (REC_DURATION * REC_FPS))
        abort = os.path.exists('ABORT_RECORDING')
        filename = '/var/tmp/rec/%06d.jpg' % (1000 * frame / REC_FPS,)
        yield filename
        frame += 1



def recordFrames(lock, ns):
    # prevent processes from queueing up when the rec button is pressed while recording
    if os.path.exists('RECORD_LOCK'):
        print('{} - I\'m sorry Dave, I\'m afraid I can\'t start another recording…'.format(datetime.now()))
        return
    print(ns)

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
    camera.resolution = (352,244)
    camera.framerate = REC_FPS
    camera.hflip = True
    camera.vflip = True

    # record
    print('{} - start recording'.format(datetime.now()))

    camera.capture_sequence(
        # [
        #     '/var/tmp/rec/%06d.jpg' % (1000 * frame / REC_FPS,)
        #     for frame in range(REC_DURATION * REC_FPS)
        # ]
        generateFilenamesForRecording()
        ,use_video_port=True)

    camera.close() # gracefully shutdown the camera (freeing all resources)
    print('{} - finished recording'.format(datetime.now()))

    # release the lock and delete the lock file
    if config.getboolean('System','gpio'):
        GPIO.output(7,False) # turn off led
    os.remove('RECORD_LOCK')
    if os.path.exists('ABORT_RECORDING'): os.remove('ABORT_RECORDING')
    lock.release()



def buildVideo(folder, video_path, timestamps=REC_TIMESTAMPS):
    ms_per_frame = 1000/REC_FPS

    timestamps = [int(round(x/ms_per_frame))*(ms_per_frame) for x in timestamps] # rounds each timestamp to closest 20
    timestamps = [os.path.join(folder,'%06d.jpg' % x) for x in timestamps] # create filenames from timestamps

    all_recorded_files = [os.path.join(folder,f) for f in sorted(os.listdir(folder))]

    # remove files that does not match the recorded ticks
    outputframes = []
    for f in all_recorded_files:
        if f in timestamps:
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


def uploadToDropbox(local_path, app_key, app_secret, app_whatever):

    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
    client = dropbox.client.DropboxClient(app_whatever)

    f = open(local_path, 'rb')
    filename = 'videos/cdmkk_%s.mp4' % (datetime.now().strftime('%Y%m%d_%H%M%S'),)
    client.put_file(filename, f)
    response = client.share(filename)
    return response['url']


def showQrCode(url, ns):
    # creating qrcode from url
    url = pyqrcode.create(url)
    qr_code_path = os.path.join(ns.root_folder,'pics','code.png')
    url.png(qr_code_path, scale=1) #scale=1 means: 1 little square is 1px

    # display qrcode and background image
    img = aspect_scale(pygame.image.load(qr_code_path), (111,111))
    bg = pygame.image.load(os.path.join(ns.root_folder,'pics','bg.png'))
    screen.blit(bg,(0,0))
    screen.blit(img,(310,163))
    pygame.display.update()
    clock.tick(60)



if __name__ == '__main__':

    print('{} - start magicKurbelKamera\nresolution: {} x {}'.format(datetime.now(), WIDTH,HEIGHT))

    manager = Manager()
    ns = manager.Namespace()

    ns.root_folder = config.get('System','root_folder')

    # Lock Object for recording, only one recording should take place at once
    rec_lock = Lock()
    # remove an old lock-file (debris from a crash)
    if os.path.exists('RECORD_LOCK'): os.remove('RECORD_LOCK')
    if os.path.exists('ABORT_RECORDING'): os.remove('ABORT_RECORDING')


    # pygame setup
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption('MagicKurbelKamera') # set a window title
    if fullscreen: screen = pygame.display.set_mode((WIDTH,HEIGHT), pygame.FULLSCREEN)
    else:          screen = pygame.display.set_mode((WIDTH,HEIGHT))

    background = pygame.Surface(screen.get_size()) # dunno
    background.fill((255,255,255)) # black background
    background = background.convert() # dunno
    # end of pygame setup

    # show init screen
    bg = pygame.image.load(os.path.join(ns.root_folder,'pics','initial.png'))
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

                    show_image(screen, clock, frame)

                    # count ms since first tick
                    if FIRST_REC_TIMESTAMP == -1:
                        FIRST_REC_TIMESTAMP = pygame.time.get_ticks()
                        REC_TIMESTAMPS = [0]
                    else:
                        REC_TIMESTAMPS.append(pygame.time.get_ticks() - FIRST_REC_TIMESTAMP)


                # escape
                elif event.key == pygame.K_ESCAPE:
                    mainloop = False # user pressed ESC

                # d
                elif event.key == pygame.K_d:

                    bg = pygame.image.load(os.path.join(ns.root_folder,'pics','development.png'))
                    screen.blit(bg,(0,0))
                    pygame.display.update()

                    buildVideo('/var/tmp/rec', config.get('System','video_path'), timestamps=REC_TIMESTAMPS)
                    print('{} - Start uploading'.format(datetime.now()))
                    db_url = uploadToDropbox(config.get('System','video_path'), app_key, app_secret, app_whatever)

                    print('{} - Finished uploading'.format(datetime.now()))
                    showQrCode(db_url, ns)


                # r
                elif config.getboolean('System','camera') and event.key == pygame.K_r:
                    FIRST_REC_TIMESTAMP = pygame.time.get_ticks()
                    REC_TIMESTAMPS = []

                    # print('r FIRST_REC_TIMESTAMP', FIRST_REC_TIMESTAMP)
                    RECORDER = Process(target=recordFrames, args=(rec_lock,ns,))
                    RECORDER.start()

                elif event.key == pygame.K_s:
                    print('{} - ABORT_RECORDING'.format(datetime.now()))
                    with open('ABORT_RECORDING', 'a'): os.utime('ABORT_RECORDING', None)



                # f for preview of recording
                elif event.key == pygame.K_f:
                    print(FOLDER)
                    if FOLDER == '/var/tmp/rec':
                        changeFolder('/var/tmp/frames')
                    else:
                        changeFolder('/var/tmp/rec')
