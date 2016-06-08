# sudo apt-get install python-dev libjpeg8-dev
#find /usr/lib -name libjpeg.so
#/usr/lib/arm-linux-gnueabihf/libjpeg.so
#sudo ln -s /usr/lib/arm-linux-gnueabihf/libjpeg.so /usr/lib/
#sudo pip install PIL


# install pip
sudo apt-get -y install python-dev python-pip


# libraries
# dropbox lib
sudo pip install dropbox
# qr lib
sudo pip install pyqrcode pypng


# create ramdisk
sudo mkdir /var/tmp
echo "tmpfs /var/tmp tmpfs nodev,nosuid,size=250M 0 0" | sudo tee --append /etc/fstab
sudo mount -a
