from images2gif import writeGif
from PIL import Image
import os

file_names = sorted((fn for fn in os.listdir('gif') if fn.endswith('.jpg')))

images = [Image.open(fn) for fn in file_names]

size = (352,244)
for im in images:
    im.thumbnail(size, Image.ANTIALIAS)

#print writeGif.__doc__

filename = "test.gif"
writeGif(filename, images, duration=0.5, repeat=True)