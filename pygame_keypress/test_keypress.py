# -*- coding: utf-8 -*-

import pygame

import picamera

from multiprocessing import Process, Lock
import subprocess
import os
import time



global WIDTH
global HEIGHT

global REC_DURATION
global REC_FPS

WIDTH  = 450
HEIGHT = int(244 * WIDTH / 352)

REC_DURATION = 10 # seconds
REC_FPS = 50


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
    image = '/var/tmp/frames/NEUBR_28_%04d.jpg' % (frame,)
    img = aspect_scale(pygame.image.load(image), (WIDTH,HEIGHT))
    # img = pygame.image.load(image)
    screen.blit(img,(0,0))

    # pygame.display.flip()
    pygame.display.update()

    # setting the max Framerate to 60 Hz according the the display (not sure which function is 'better')
    # clock.tick_busy_loop(60)
    clock.tick(60)
    ms_since_start = pygame.time.get_ticks()

    # print(frame, 'FPS', int(clock.get_fps()), 'ms', ms_since_start)


# generator of filenames for the recording
def filenames():
    frame = 1
    while frame <= REC_DURATION * REC_FPS:
        yield '/var/tmp/rec/%04d.jpg' % (1000 * frame / REC_FPS,)
        frame += 1


def recordFrames(lock):
    # prevent processes from queueing up when the rec button is pressed while recording
    if os.path.exists('RECORD_LOCK'):
        print('I\'m sorry Dave, I\'m afraid I can\'t do that…')
        return

    # only one recording
    lock.acquire()
    with open('RECORD_LOCK', 'a'): os.utime('RECORD_LOCK', None)

    # cleanup recording directory
    filelist = [ f for f in os.listdir("/var/tmp/rec/") if f.endswith(".jpg") ]
    for f in filelist:
        os.remove('/var/tmp/rec/' + f)

    print('record button pressed')

    # instantiate a camera object
    camera = picamera.PiCamera()
    # setting the camera up
    camera.resolution = (352,244)
    camera.framerate = REC_FPS
    camera.hflip = True
    camera.vflip = True

    # record
    print('start recording')
    camera.capture_sequence(filenames(), use_video_port=True)
    camera.close() # gracefully shutdown the camera (freeing all resources)
    print('finished recording')

    # release the lock and delete the lock file
    os.remove('RECORD_LOCK')
    lock.release()



if __name__ == '__main__':
    print('start magicKurbelKamera\nresolution: {} x {}'.format(WIDTH,HEIGHT))

    # Lock Object for recording, only one recording should take place at once
    rec_lock = Lock()
    # remove an old lock-file (debris from a crash)
    if os.path.exists('RECORD_LOCK'): os.remove('RECORD_LOCK')


    # pygame setup
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption('MagicKurbelKamera') # set a window title
    screen = pygame.display.set_mode((WIDTH,HEIGHT)) # pygame.FULLSCREEN  352,244
    background = pygame.Surface(screen.get_size()) # dunno
    background.fill((255,255,255)) # black background
    background = background.convert() # dunno
    # end of pygame setup

    frame = 1
    mainloop = True

    # magic ahead
    while mainloop:
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

                    frame = (frame % 1048)
                    if frame == 0: frame = 1048

                    show_image(screen, clock, frame)

                # escape
                elif event.key == pygame.K_ESCAPE:
                    mainloop = False # user pressed ESC

                # r
                elif event.key == pygame.K_r:
                    Process(target=recordFrames, args=(rec_lock,)).start()


                # p
                elif event.key == pygame.K_p:
                    command = "sudo halt"
                    subprocess.call(command, shell = True)




# this stuff is just a reminder what has to be done before starting the magicKurbelKamera

# just once
# create ramdisk

# sudo mkdir /var/tmp
# echo "tmpfs /var/tmp tmpfs nodev,nosuid,size=250M 0 0" | sudo tee --append /etc/fstab
# sudo mount -a


# following stuff has to happen before starting the magic

# mkdir /var/tmp/rec
# mkdir /var/tmp/frames
# cp /home/pi/Desktop/magicKurbelKamera/video/frames/*.jpg /var/tmp/frames/