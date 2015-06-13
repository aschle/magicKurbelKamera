# -*- coding: utf-8 -*-

import os
from datetime import datetime

import ConfigParser
config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

GPIO_ACTIVE = config.getboolean('System','gpio')
RECORD_PATH = config.get('System','rec_folder')
HFLIP = config.getboolean('Recorder', 'hflip')
VFLIP = config.getboolean('Recorder', 'vflip')

# only on raspi
if config.getboolean('System','camera'):
    import picamera
if config.getboolean('System','gpio'):
    import RPi.GPIO as GPIO
    # init GPIO
    GPIO.setmode(GPIO.BOARD)

    # # Leuchtkasten
    # GPIO.setup( 7, GPIO.OUT)
    # GPIO.setup( 7, GPIO.HIGH)

    # # Rec-Lampe
    # GPIO.setup(11, GPIO.OUT)
    # GPIO.setup(11, GPIO.HIGH)


def generateFilenamesForRecording(rec_duration, rec_fps, stop_recording_event):
    frame = 0
    timeout = False

    while not (timeout or stop_recording_event.is_set()):
        timeout = (frame >= (rec_duration * rec_fps))
        filename = os.path.join(RECORD_PATH, '%06d.jpg' % (1000 * frame / rec_fps,))
        yield filename
        frame += 1


def recordFrames(lock, recording_flag, width, height, rec_duration, rec_fps, stop_recording_event):
    # prevent processes from queueing up when the rec button is pressed while recording
    if recording_flag.is_set():
        print('{} - I\'m sorry Dave, I\'m afraid I can\'t start another recording…'.format(datetime.now()))
        return

    # only one recording
    lock.acquire()
    recording_flag.set()

    if GPIO_ACTIVE:
        GPIO.setup( 7, GPIO.OUT)
        GPIO.setup( 11, GPIO.OUT)

        GPIO.output(7,GPIO.LOW) # turn on led
        GPIO.output(11,GPIO.LOW) # turn on led

    # cleanup recording directory
    filelist = [ f for f in os.listdir(RECORD_PATH) if f.endswith(".jpg") ]
    for f in filelist:
        os.remove(os.path.join(RECORD_PATH, f))

    print('{} - record button pressed'.format(datetime.now()))

    # instantiate a camera object
    camera = picamera.PiCamera()
    # setting the camera up
    camera.resolution = (width, height)
    camera.framerate = rec_fps
    camera.hflip = HFLIP
    camera.vflip = VFLIP

    # record
    print('{} - start recording'.format(datetime.now()))

    camera.capture_sequence(
        generateFilenamesForRecording(rec_duration, rec_fps, stop_recording_event)
        ,use_video_port=True)

    camera.close() # gracefully shutdown the camera (freeing all resources)
    print('{} - finished recording'.format(datetime.now()))


    # release the lock and delete the lock file
    if GPIO_ACTIVE:
        GPIO.output(7,GPIO.HIGH) # turn off led
        GPIO.output(11,GPIO.HIGH) # turn off led

    recording_flag.clear()
    lock.release()

