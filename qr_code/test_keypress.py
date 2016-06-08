# -*- coding: utf-8 -*-

import pygame

# from multiprocessing import Manager, Process, Lock
import subprocess
import os
import time
from datetime import datetime

import pyqrcode


global WIDTH
global HEIGHT
WIDTH  = 352
HEIGHT = int(244 * WIDTH / 352)

global RECORDER
global REC_DURATION
global REC_FPS
REC_DURATION = 10 # seconds
REC_FPS = 50


global REC_TIMESTAMPS
global FIRST_REC_TIMESTAMP
REC_TIMESTAMPS = [0]
FIRST_REC_TIMESTAMP = -1


global STATE
STATE = 'init'


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
    # print(frame, 'FPS', int(clock.get_fps()), 'ms', ms_since_start)



def buildGif(folder='/var/tmp/rec', timestamps=REC_TIMESTAMPS):
    ms_per_frame = 1000/REC_FPS
    timestamps = [int(round(x/ms_per_frame))*(ms_per_frame) for x in timestamps] # rounds each timestamp to closest 20
    print(timestamps)
    # TODO: implement gif building


def showQrCode(url = 'http://google.com'):
    # creating qrcode from url
    url = pyqrcode.create(url)
    url.png('code.png', scale=1) #scale=1 means: 1 little square is 1px
    code = 'code.png'

    # display qrcode and background image
    y_offset = 50 #padding-top to have have space for whatever
    x_offset = (WIDTH-(HEIGHT-y_offset))/2 #centering the qr-code
    img = aspect_scale(pygame.image.load(code), (WIDTH-y_offset,HEIGHT-y_offset))
    bg = pygame.image.load("bg.png")
    screen.blit(bg,(0,0))
    screen.blit(img,(x_offset,y_offset))
    pygame.display.update()
    clock.tick(60)

if __name__ == '__main__':

    print('{} - start magicKurbelKamera\nresolution: {} x {}'.format(datetime.now(), WIDTH,HEIGHT))

    print('ESC        --> quit')
    print('ARROW_KEYS --> show prev/next image')
    print('Q          --> show QR-Screen')
    print('H          --> print rec_timestamps')
    print('R          --> start recording for 60s')
    print('P          --> shutdown raspi')


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

                    # count ms since first tick
                    if FIRST_REC_TIMESTAMP == -1:
                        FIRST_REC_TIMESTAMP = pygame.time.get_ticks()
                    else:
                        REC_TIMESTAMPS.append(pygame.time.get_ticks() - FIRST_REC_TIMESTAMP)



                # escape
                elif event.key == pygame.K_ESCAPE:
                    mainloop = False # user pressed ESC

                # h
                elif event.key == pygame.K_h:
                    buildGif()

                # r
                elif event.key == pygame.K_r:
                    print('record!')

                # p
                elif event.key == pygame.K_p:
                    command = "sudo halt"
                    subprocess.call(command, shell = True)

                elif event.key == pygame.K_q:
                    print('QR-Code')
                    showQrCode('http://google.com')





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