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


## Quick Start
To get all requirements installed automatically, change directory into where the source was cloned, and run  
```bash
chmod +x ./install_prerequisites.py
./install_prerequisites
```
After pre-requisites are installed, reboot.
Once the system is back running, change directory to the source and make appropriate changes to config.txt.
Then, run:
```bash
./.venv/bin/python3 main.py
```

To schedule the alerter to start at boot:  
1. Change directory into where the program is located
2. Run ```pwd``` to get the absolute path to the program.
3. Run ```crontab -e```
4. Create this line, substituting the path from step 1 where appropriate:
```@reboot /home/yourusername/SenseHatWeatherAlerter/.venv/bin/python3 /home/yourusername/SenseHatWeatherAlerter/main.py```
5. Save and exit
6. Reboot

## Checking the current alert and muting it
When using the Raspberry Pi SenseHat, you can check the current alert and get more details by pressing the center joystick button.  This will also mute the current alert, though the colored indicator will remain illuminated for the duration of the alert.  You can press the button again at any time to get the details of the alert.
