# https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=11990

import pygame

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN  )

clock = pygame.time.Clock()

count = 1

while 1:

		image = 'video/frames/NEUBR_24_%04d.jpg' % (count,)
		img = pygame.image.load(image)
		screen.fill((255,255,255))
		screen.blit(img,(0,0))
		clock.tick(10)
		pygame.display.flip()
		count = count + 1