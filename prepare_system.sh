sudo mkdir /var/tmp
echo "tmpfs /var/tmp tmpfs nodev,nosuid,size=250M 0 0" | sudo tee --append /etc/fstab
sudo mount -a