



## Supported Displays  

### Raspberry Pi SenseHat  

#### Install SenseHat support 
```
sudo apt install sense-hat
```

### Adafruit 2.13" eInk Bonnet
#### Install CircuitPython  
```
cd ~  
sudo apt install python3-venv  
python3 -m venv env --system-site-packages  
source env/bin/activate  
pip3 install adafruit-circuitpython-epd  
pip3 install Pillow
```
#### Install Blinka
```
cd ~  
pip3 install --upgrade adafruit-python-shell  
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py  
sudo -E env PATH=$PATH python3 raspi-blinka.py  
```
#### Disable SPI Chip Enable Lines
```
cd ~  
pip3 install --upgrade adafruit-python-shell click  
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/raspi-spi-reassign.py  
sudo -E env PATH=$PATH python3 raspi-spi-reassign.py --ce0=disabled --ce1=disabled  
```
