# https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=11990

import pygame

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN  )

clock = pygame.time.Clock()

count = 1

#http://www.pygame.org/pcr/transform_scale/
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

while 1:
		image = 'video/frames/NEUBR_24_%04d.jpg' % (count,)
		img = pygame.image.load(image)
		screen.fill((255,255,255))
		scaled_image = aspect_scale(img, (1024, 768)); 
		screen.blit(scaled_image,(0,0))
		clock.tick(5)
		pygame.display.flip()
		count = count + 1
