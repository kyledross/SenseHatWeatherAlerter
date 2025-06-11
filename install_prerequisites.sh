#!/bin/bash

# Sense Hat Weather Alerter prerequisite installer
#
# USE AT YOUR OWN RISK
#

# Basic requirements
sudo apt install python3-dev build-essential -y

# Create virtual environment -----------------------
sudo apt install python3-venv -y
python -m venv .venv
source .venv/bin/activate

# Install requirements -----------------------------
pip install -r requirements.txt

# Install SenseHat support -------------------------
sudo apt install sense-hat -y

# Install eInk Bonnet support ----------------------
# Install Circuit Python
pip3 install adafruit-circuitpython-epd
pip3 install Pillow

# Install GPIO support
pip3 install RPi.GPIO

# Install Blinka
pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
# todo See if this can exit without prompting for reboot
sudo -E env PATH=$PATH python3 raspi-blinka.py <<< 'n'

# Disable SPI Chip Enable Lines
pip3 install --upgrade adafruit-python-shell click
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/raspi-spi-reassign.py
# todo See if this can exit without prompting for reboot
sudo -E env PATH=$PATH python3 raspi-spi-reassign.py --ce0=disabled --ce1=disabled <<< 'n'

# Reboot
echo "Press Enter to reboot or Ctrl+C to cancel..."
read
if [ $? -eq 0 ]; then
    sudo reboot now
fi



