
mkdir /var/tmp/rec 2> /dev/null
mkdir /var/tmp/frames 2> /dev/null
cp /home/pi/Desktop/magicKurbelKamera/video/frames/*.jpg /var/tmp/frames

python /home/pi/Desktop/magicKurbelKamera/pygame_keypress/test_keypress.py