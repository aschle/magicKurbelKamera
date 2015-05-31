# https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=11990

import pygame

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN  )
done = False
image1 = pygame.image.load("video/frames/NEUBR_24_0001.jpg")
image2 = pygame.image.load("video/frames/NEUBR_24_0100.jpg")

clock = pygame.time.Clock()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    screen.fill((255,255,255))
    screen.blit(image1,(0,0))
    clock.tick(10)
    pygame.display.flip()   
    screen.fill((255,255,255))
    screen.blit(image2,(0,0))
    clock.tick(10)
    pygame.display.flip()