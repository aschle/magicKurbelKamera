cd /home/pi/magicKurbelKamera

mkdir /var/tmp/rec
mkdir /var/tmp/frames
cp video/frames/*.jpg /var/tmp/frames

python pygame_keypress/test_keypress.py