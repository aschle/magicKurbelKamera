# -*- coding: utf-8 -*-

import pygame

import os
import time

from multiprocessing import Process, Lock, Event
from datetime import datetime


import ConfigParser
config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

if config.getboolean('System','gpio'):
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(13, GPIO.OUT)
    GPIO.output(13, GPIO.HIGH)

    # GPIO.setup(15, GPIO.OUT)
    # GPIO.output(15, GPIO.HIGH)

    # GPIO.setup(29, GPIO.OUT)
    # GPIO.output(29, GPIO.HIGH)

    # GPIO.setup(31, GPIO.OUT)
    # GPIO.output(31, GPIO.HIGH)

    # GPIO.setup(33, GPIO.OUT)
    # GPIO.output(33, GPIO.HIGH)

    # GPIO.setup(35, GPIO.OUT)
    # GPIO.output(35, GPIO.HIGH)




from post_production import clearRecFolder, buildVideo, uploadToDropbox as upload, generateQrCode
from recorder import recordFrames

play_status_movie = True
frame = 1
stop_recording_event = Event()
rec_timestamps = [0]
first_rec_timestamp = -1

def postproduction(screen, stop_recording_event, rec_timeout_flag, rec_truly_started_event):
    stop_recording_event.set()
    rec_timeout_flag.clear()
    rec_truly_started_event.clear()

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
    show_qr_code = True

    return pygame.time.get_ticks()

def toggleRelais(pin):
    GPIO.output(pin, not GPIO.input(pin))

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

    TIMEOUT = config.getint('System', 'timeout')
    QR_TIMEOUT = config.getint('System', 'qr_timeout')


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
    recording_flag = Event()
    stop_recording_event = Event()
    rec_timeout_flag = Event()
    rec_truly_started_event = Event()

    reset_flag = Event()

    # Playing movie state
    play_status_movie = True
    show_qr_code = False

    # pygame setup
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption('MagicKurbelKamera') # set a window title
    if FULLSCREEN: screen = pygame.display.set_mode((WIDTH,HEIGHT), pygame.FULLSCREEN)
    else:          screen = pygame.display.set_mode((WIDTH,HEIGHT))

    background = pygame.Surface(screen.get_size()) # dunno
    background.fill((0,0,0)) # black background
    background = background.convert() # dunno
    # end of pygame setup

    # load init video
    movie = pygame.movie.Movie(os.path.join(ROOT_PATH,'img','magic.mp4'))
    movie_screen = pygame.Surface(movie.get_size()).convert()
    movie.set_display(movie_screen)
    movie.play()


    frame = 1
    ticks = 0
    mainloop = True
    last_event = pygame.time.get_ticks()

    # magic ahead
    while mainloop:
        diff = pygame.time.get_ticks() - last_event

        # Normal timeout after some time
        if diff > (TIMEOUT * 1000) and not show_qr_code and not play_status_movie:
            reset_flag.set()
            last_event = pygame.time.get_ticks()

        # Recoding is timed out
        elif rec_timeout_flag.is_set():
            last_event = postproduction(screen, stop_recording_event, rec_timeout_flag, rec_truly_started_event)

        # A little longer timeout so you have time to scan the qr code
        elif diff > (QR_TIMEOUT * 1000) and show_qr_code:
            print('TIMEOUT 2')
            reset_flag.set()
            last_event = pygame.time.get_ticks()



        if (reset_flag.is_set()):
            play_status_movie = True
            show_qr_code = False
            movie.stop()
            frame = 1
            stop_recording_event.set()
            rec_timestamps = []
            first_rec_timestamp = -1
            clearRecFolder(REC_PATH, rec_timestamps, REC_FPS)
            reset_flag.clear()

        # display video
        if play_status_movie:
            screen.blit(background,(0,0))
            screen.blit(movie_screen,(88,30))
            pygame.display.update()
            clock.tick(60)

            if movie.get_busy() == 0:
                movie.rewind()
                movie.play()


        for event in pygame.event.get():

            # pygame window closed by user
            if event.type == pygame.QUIT: mainloop = False

            # key is released
            elif event.type == pygame.KEYUP:
                last_event = pygame.time.get_ticks()

                # left and right arrow
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:

                    play_status_movie = False

                    toggleRelais(13) # klick klack

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
                        rec_truly_started_event.set()
                    else:
                        rec_timestamps.append(pygame.time.get_ticks() - first_rec_timestamp)
                    ticks += 1

                    if ticks % 50 == 5:
                        clearRecFolder(REC_PATH, rec_timestamps, REC_FPS)


                # escape
                elif event.key == pygame.K_ESCAPE:
                    mainloop = False # user pressed ESC


                # Record Button
                elif event.key == pygame.K_r and config.getboolean('System','camera'):
                    if not recording_flag.is_set():

                        play_status_movie = False
                        stop_recording_event.clear()

                        first_rec_timestamp = pygame.time.get_ticks()
                        rec_timestamps = []

                        # show pre_rec screen
                        bg = pygame.image.load(os.path.join(ROOT_PATH,'img','pre_rec.png'))
                        screen.blit(bg,(0,0))
                        pygame.display.update()
                        clock.tick(60)

                        rec_timeout_flag.clear()
                        recorder = Process(target=recordFrames,
                                           args=(rec_lock,
                                                 recording_flag,
                                                 WIDTH, HEIGHT,
                                                 REC_DURATION,
                                                 REC_FPS,
                                                 stop_recording_event,
                                                 rec_timeout_flag,
                                                 rec_truly_started_event))
                        recorder.start()

                    else:
                        # start postproduction
                        last_event = postproduction(screen, stop_recording_event, rec_timeout_flag, rec_truly_started_event)


                # this is the bin button
                elif event.key == pygame.K_e:
                    reset_flag.set()

    GPIO.cleanup()


