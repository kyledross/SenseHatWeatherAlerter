# SenseHat Weather Alerter

### Important

This code is intended for educational and demonstration purposes only.
It must not be used in life- or property-threatening situations.
Always use a reliable source for weather information, such as a weather radio,
local radio, or local television.

_**Use this code at your own risk.**_  

### Purpose

This is a Python program intended to run on a Raspberry Pi to display weather alerts from the WeatherBox API (see [https://github.com/kyledross/WeatherBox](https://github.com/kyledross/WeatherBox)).  

### Requirements  

Raspberry Pi  
Raspberry Pi OS  
Raspberry Pi SenseHat, or  
Raspberry Pi SenseHat Emulator, or  
Adafruit 2.13" eInk Bonnet

(Yes, the project is named Sense Hat Weather Alerter. Yes, it supports both a SenseHat and an eInk Bonnet. You got the bonus plan.)  

The program will try to locate a SenseHat.  If it can't find one, it will try to locate a SenseHat Emnulator.  If it can't find that, it will attempt to find an Adafruit 2.13" eInk Bonnet.  And, at last, if that fails, it will display an error.  The display code is extensible, so add your favorite display method.

### What It Does

The program will periodically retrieve any active weather alerts from the API and display them on the attached display.  

In addition to weather alerts, if a Raspberry Pi SenseHat is attached, the air pressure is also tracked, and an alert about a nearby storm will be displayed, as appropriate.  


## Config file

The config file is a simple text file named config.txt.  It consists of three lines.  They are, in order:  

WeatherBoxAPI Server  
State  
Municipality  

For example:  
``` text
http://rpi02w.local:8080  
tn  
knoxville
```
WeatherBoxAPI uses third-party location resolution, so you may have to adjust the municipality.  Try city names or counties/parishes.  If using a county or parish, use the full name, such as  

`Shreveport`  
or  
`Caddo Parish `  
or  
`Shelby County  `



## Supported Displays  

### Raspberry Pi SenseHat  

#### Install SenseHat support 
``` bash
sudo apt install sense-hat
```

### Adafruit 2.13" eInk Bonnet
_Note: There are a few different versions of this bonnet.  Please consult the pages for your device for any changes below._
#### Install CircuitPython  
``` bash
cd ~  
sudo apt install python3-venv  
python3 -m venv env --system-site-packages  
source env/bin/activate  
pip3 install adafruit-circuitpython-epd  
pip3 install Pillow
```
#### Install Blinka
``` bash
cd ~  
pip3 install --upgrade adafruit-python-shell  
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py  
sudo -E env PATH=$PATH python3 raspi-blinka.py  
```
#### Disable SPI Chip Enable Lines
``` bash
cd ~  
pip3 install --upgrade adafruit-python-shell click  
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/raspi-spi-reassign.py  
sudo -E env PATH=$PATH python3 raspi-spi-reassign.py --ce0=disabled --ce1=disabled  
```
