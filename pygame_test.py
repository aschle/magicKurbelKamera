import pygame
from pygame.locals import *
pygame.init()
WIDTH = 1280
HEIGHT = 1080
windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)

frame = 14
image = 'karneval/test%04d.jpg' % (frame,)

img = pygame.image.load(image)
while True:
        events = pygame.event.get()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
