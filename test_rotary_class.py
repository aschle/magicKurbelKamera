import sys
import time
from rotary_class import RotaryEncoder


# Define GPIO inputs
PIN_A = 14 	# Pin 8 
PIN_B = 15	# Pin 10
BUTTON = 4	# Pin 7



# This is the event callback routine to handle events
def showImage(event, frame):
	if event == RotaryEncoder.CLOCKWISE:
		print frame, "Clockwise", image

	elif event == RotaryEncoder.ANTICLOCKWISE:
		print frame, "Anticlockwise"
	
	return

# Define the switch

rswitch = RotaryEncoder(PIN_A,PIN_B,BUTTON,showImage)

while True:
	time.sleep(0.5)


