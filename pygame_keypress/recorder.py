# -*- coding: utf-8 -*-

import os
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

