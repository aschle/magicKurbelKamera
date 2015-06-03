# -*- coding: utf-8 -*-

import pygame
import picamera


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



def show_image(screen, clock, frame):
    image = '/var/tmp/NEUBR_28_%04d.jpg' % (frame,)
    # img = aspect_scale(pygame.image.load(image), (352,288))
    img = pygame.image.load(image)
    screen.blit(img,(0,0))

    pygame.display.flip()
    # pygame.display.update()

    clock.tick_busy_loop(100)
    ms_since_start = pygame.time.get_ticks()
    print(frame, 'FPS', int(clock.get_fps()), 'ms', ms_since_start)





def main():

    print('start')

    pygame.init()
    clock = pygame.time.Clock()

    pygame.display.set_caption('MagicKurbelKamera')

    screen = pygame.display.set_mode((352,244)) # pygame.FULLSCREEN  352,244

    background = pygame.Surface(screen.get_size())
    background.fill((255,255,255))
    background = background.convert()


    camera = picamera.PiCamera()
    camera.resolution = (352,244)
    camera.framerate = 60

    camera.preview_fullscreen = False
    camera.preview_window = (0, 0, 352, 244)


    frame = 1
    rec_frame = 1
    mainloop = True
    while mainloop:
        for event in pygame.event.get():

            # pygame window closed by user
            if event.type == pygame.QUIT: mainloop = False

            # key is released
            elif event.type == pygame.KEYUP:

                # left and right arrow
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    if event.key == pygame.K_LEFT:   frame -= 1
                    elif event.key == pygame.K_RIGHT: frame += 1

                    frame = (frame % 1048)
                    if frame == 0: frame = 1048

                    show_image(screen, clock, frame)

                # escape
                elif event.key == pygame.K_ESCAPE:
                    mainloop = False # user pressed ESC

                # r
                elif event.key == pygame.K_r:
                    image = '/var/tmp/rec/%04d.jpg' % (rec_frame,)
                    print('REC BUTTON ', image)
                    camera.capture(image, use_video_port=True)
                    rec_frame += 1


                # p
                elif event.key == pygame.K_p:
                    if camera.previewing:
                        camera.stop_preview()
                    else:
                        camera.start_preview()









main()
