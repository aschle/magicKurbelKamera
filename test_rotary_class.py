import sys
import time
from rotary_class import RotaryEncoder
import cv2


# Define GPIO inputs
PIN_A = 14 	# Pin 8 
PIN_B = 15	# Pin 10
BUTTON = 4	# Pin 7



# This is the event callback routine to handle events
def showImage(event, frame):
	if event == RotaryEncoder.CLOCKWISE:
		image = 'karneval/test%04d.jpg' % (frame,)
		print frame, "Clockwise", image

		img = cv2.imread(image,0)
		cv2.imshow('image',img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
	elif event == RotaryEncoder.ANTICLOCKWISE:
		print frame, "Anticlockwise"
	
	return

# Define the switch

rswitch = RotaryEncoder(PIN_A,PIN_B,BUTTON,showImage)

while True:
	time.sleep(0.5)


