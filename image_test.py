import cv2

frame = 14
image = 'karneval/test%04d.jpg' % (frame,)

img = cv2.imread(image,0)
cv2.imshow('image',img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
