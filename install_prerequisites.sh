#!/bin/bash

# Sense Hat Weather Alerter prerequisite installer
#
# USE AT YOUR OWN RISK
#


# Create virtual environment -----------------------
python -m venv .venv
source .venv/bin/activate

# Install requirements -----------------------------
pip install -r requirements.txt

# Install SenseHat support -------------------------
sudo apt install sense-hat

# Install eInk Bonnet support ----------------------
# Install Circuit Python
sudo apt install python3-venv
source .venv/bin/activate
pip3 install adafruit-circuitpython-epd
pip3 install Pillow

# Install Blinka
pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo -E env PATH=$PATH python3 raspi-blinka.py

# Disable SPI Chip Enable Lines
pip3 install --upgrade adafruit-python-shell click
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/raspi-spi-reassign.py
sudo -E env PATH=$PATH python3 raspi-spi-reassign.py --ce0=disabled --ce1=disabled

# Reboot
echo "Press Enter to reboot or Ctrl+C to cancel..."
read
if [ $? -eq 0 ]; then
    sudo reboot now
fi



