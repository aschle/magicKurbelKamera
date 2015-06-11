# -*- coding: utf-8 -*-

import pygame

import os
import time

from multiprocessing import Process, Lock, Event
from datetime import datetime


import ConfigParser
config = ConfigParser.ConfigParser()
config.readfp(open('magic.cfg'))


from post_production import clearRecFolder, buildVideo, uploadToDropbox as upload, generateQrCode
from recorder import recordFrames

# not sure alexa stole this code from the internets
def scale(img,(bx,by)):
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


if __name__ == '__main__':

    WIDTH  = config.getint('Screen','width')
    HEIGHT = config.getint('Screen','height')
    FULLSCREEN = config.getboolean('Screen','fullscreen')

    ROOT_PATH = config.get('System', 'root_folder')
    RECORD_PATH = config.get('System', 'rec_folder')
    VIDEO_PATH = config.get('System','video_path')

    FRAMES_PATH = config.get('System','frames_folder')
    ALL_FRAMES = all_frames = [os.path.join(FRAMES_PATH,f) for f in sorted(os.listdir(FRAMES_PATH))]

    REC_PATH = config.get('System','rec_folder')
    REC_DURATION = config.getint('Recorder','rec_duration') # seconds
    REC_FPS = config.getint('Recorder','rec_fps')

    rec_timestamps = [0]
    first_rec_timestamp = -1


    print('{} - start magicKurbelKamera\nresolution: {} x {}'.format(datetime.now(), WIDTH,HEIGHT))


    # Lock Object for recording, only one recording should take place at once
    rec_lock = Lock()
    stop_recording_event = Event()
    # remove an old lock-file (debris from a crash)
    if os.path.exists('RECORD_LOCK'): os.remove('RECORD_LOCK')


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
    ticks = 0
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

                    image = ALL_FRAMES[frame - 1]
                    img = scale(pygame.image.load(image), (WIDTH,HEIGHT))
                    screen.blit(img,(0,0))
                    pygame.display.update() # pygame.display.flip()
                    clock.tick(60)


                    # count ms since first tick
                    if first_rec_timestamp == -1:
                        first_rec_timestamp = pygame.time.get_ticks()
                        rec_timestamps = [0]
                    else:
                        rec_timestamps.append(pygame.time.get_ticks() - first_rec_timestamp)
                    ticks += 1
                    if ticks % 50 == 0:
                        clearRecFolder(REC_PATH, rec_timestamps, REC_FPS)





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
                    url = upload(VIDEO_PATH)
                    print('{} - Finished uploading'.format(datetime.now()))

                    # generate qrcode and display it on background image
                    qr_code_path = generateQrCode(url, os.path.join(ROOT_PATH,'img') )
                    bg = pygame.image.load(os.path.join(ROOT_PATH,'img','bg.png'))
                    screen.blit(bg,(0,0))
                    img = scale(pygame.image.load(qr_code_path), (111,111))
                    screen.blit(img,(310,163))
                    pygame.display.update()
                    clock.tick(60)


                # r
                elif config.getboolean('System','camera') and event.key == pygame.K_r:
                    first_rec_timestamp = pygame.time.get_ticks()
                    rec_timestamps = []

                    # print('r FIRST_REC_TIMESTAMP', FIRST_REC_TIMESTAMP)
                    recorder = Process(target=recordFrames,
                                       args=(rec_lock,
                                             WIDTH, HEIGHT,
                                             REC_DURATION,
                                             REC_FPS,
                                             stop_recording_event))
                    recorder.start()

                elif event.key == pygame.K_e:
                    pass

                elif event.key == pygame.K_s:
                    stop_recording_event.set()

