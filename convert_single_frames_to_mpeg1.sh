ffmpeg -y -framerate 25 -i frames/Start_%5d.png -vcodec mpeg1video -mbd rd -trellis 2 -cmp 2 -subcmp 2 -g 100 -pass 1 magic.mp4

# convert init video mp4 to mpeg1
#ffmpeg -y -i init_not_coded.mp4 -vcodec mpeg1video -mbd rd -trellis 2 -cmp 2 -subcmp 2 -g 100 -pass 1 init.mp4