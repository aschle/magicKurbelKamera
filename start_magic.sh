cd /home/pi/magicKurbelKamera

mkdir /var/tmp/rec
mkdir /var/tmp/frames
cp video/frames/normalize_median-3/*_28_*.jpg /var/tmp/frames

# ifconfig 
# sleep 30

python pygame_keypress/magic_kk.py

