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
