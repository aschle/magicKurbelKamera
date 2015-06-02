import sys
import time
from rotary_class import RotaryEncoder
import pygame


# Define GPIO inputs
PIN_A = 14 	# Pin 8
PIN_B = 15	# Pin 10
BUTTON = 4	# Pin 7



pygame.init()
screen = pygame.display.set_mode((1024, 768)  )
clock = pygame.time.Clock()


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



# This is the event callback routine to handle events
def showImage(event, tick):

	frame = ((tick) % 1048) + 1



	if event == RotaryEncoder.CLOCKWISE:
		print 'tick:', tick, 'frame:' , frame, "Clockwise"

	elif event == RotaryEncoder.ANTICLOCKWISE:
		print tick, frame, "Anticlockwise"

	image = 'video/frames/NEUBR_28_%04d.jpg' % (frame,)
	img = pygame.image.load(image)
	screen.fill((255,255,255))
	scaled_image = aspect_scale(img, (1024, 768));
	screen.blit(scaled_image,(0,0))
	clock.tick()
	pygame.display.flip()


	return

# Define the switch

rswitch = RotaryEncoder(PIN_A,PIN_B,BUTTON,showImage)

while True:
	time.sleep(0.5)


