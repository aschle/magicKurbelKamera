# https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=11990

import pygame

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN  )

image1 = pygame.image.load("video/frames/NEUBR_24_0001.jpg")
image2 = pygame.image.load("video/frames/NEUBR_24_0100.jpg")

clock = pygame.time.Clock()

count = 1

while 1:

		for event in pygame.event.get():

				image = 'video/frames/NEUBR_24_%04d.jpg' % (count,)
				img = pygame.image.load(image)
				screen.fill((255,255,255))
				screen.blit(img,(0,0))
				clock.tick(1)
				pygame.display.flip()
				count = count + 1