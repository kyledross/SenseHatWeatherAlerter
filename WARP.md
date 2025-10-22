# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

SenseHatWeatherAlerter is a Python application designed to run on a Raspberry Pi to display weather alerts and detect local storms. It retrieves weather alerts from the WeatherBox API and displays them on various output devices including Raspberry Pi SenseHat, Adafruit 2.13" eInk Bonnet, or console output.

**Key Features:**
- Displays weather alerts from WeatherBox API on multiple display types
- Local storm detection using atmospheric pressure monitoring via SenseHat sensors
- Automatic display device fallback (SenseHat → eInk → Console)
- Configurable alert severity color coding and refresh intervals
- SQLite-based pressure data storage for storm trend analysis

**Technology Stack:**
- Python 3 with virtual environment
- Raspberry Pi OS
- SenseHat hardware or emulator
- SQLite database for pressure readings
- REST API integration with WeatherBox

## Development Commands

### Initial Setup
```bash
# Install system prerequisites and create virtual environment
chmod +x ./install_prerequisites.sh
./install_prerequisites.sh
# System will prompt for reboot after installation
```

### Configuration
```bash
# Edit config file with your WeatherBox API server and location
nano config.txt
# Format: WeatherBoxAPI Server URL, State, Municipality (each on separate lines)
```

### Running the Application
```bash
# Run in virtual environment
./.venv/bin/python3 main.py

# For development/testing with console output
PYTHONPATH=. python3 -c "from main import *; display = DisplayFactory.create_display(DisplayType.CONSOLE); alerter = Alerter(display); alerter.run()"
```

### Production Deployment
```bash
# Add to crontab for automatic startup
crontab -e
# Add: @reboot /absolute/path/to/.venv/bin/python3 /absolute/path/to/main.py
```

## Architecture Overview

### Core Components

**Main Application (`main.py`)**
- `Alerter` class: Main orchestrator that polls weather API and manages display updates
- `WeatherAlert` dataclass: Structured weather alert data from API
- 5-minute polling cycle with dynamic adjustment based on alert severity

**Display Layer (`Display/`)**
- `IDisplay` interface: Abstract base for all display implementations
- `DisplayFactory`: Auto-detection and instantiation of available display hardware
- Three implementations: `SenseHatDisplay`, `Adafruit213eInkBonnet`, `ConsoleDisplay`
- Fallback hierarchy: SenseHat → eInk → Console

**Storm Detection (`Detection/`)**
- `StormDetector`: Monitors atmospheric pressure via SenseHat sensors
- `PressureDatabase`: SQLite storage for pressure readings with automatic cleanup
- Storm detection thresholds: 2mb/hour or 3mb/3hours pressure drop
- 30-minute storm alert duration with automatic expiry

### Data Flow
1. Configuration loaded from `config.txt` (API server, state, municipality)
2. Display device auto-detected and initialized
3. Storm detector thread started (if SenseHat available)
4. Main loop: API polling → Alert processing → Display update → Sleep cycle
5. Pressure readings stored continuously, analyzed for storm patterns

### Alert Priority System
- **Extreme/Immediate**: Red display, 15-second refresh
- **Severe**: Red (immediate/expected) or Yellow, 15-60 second refresh  
- **Local Storm**: Purple override (when no NWS red alert), 60-second refresh
- **Moderate**: Yellow display, 5-minute refresh
- **Minor**: Green display, 5-minute refresh

## Configuration

### Required Configuration (`config.txt`)
```
http://your-weatherbox-server:8080
your-state-abbreviation
your-municipality
```

### WeatherBox API Dependency
This application requires a separate WeatherBox API server (https://github.com/kyledross/WeatherBox) running to provide weather alert data. The WeatherBox server acts as a proxy to National Weather Service APIs.

### Hardware Requirements
- Raspberry Pi with Raspberry Pi OS
- One of: SenseHat, SenseHat Emulator, or Adafruit 2.13" eInk Bonnet
- Network connectivity to reach WeatherBox API server

### Display Device Detection
The application automatically detects available display hardware in this order:
1. Real SenseHat hardware
2. SenseHat emulator
3. Adafruit eInk Bonnet
4. Console fallback (development)

## Development Notes

### Adding New Display Types
1. Create new class implementing `IDisplay` interface
2. Add enum entry to `DisplayType` in `DisplayFactory.py`
3. Add factory method in `DisplayFactory.create_display()`
4. Update auto-detection logic in `create_display_automatically()`

### Storm Detection Customization
- Pressure thresholds: Modify `THREE_HOUR_PRESSURE_DROP_THRESHOLD` and `ONE_HOUR_PRESSURE_DROP_THRESHOLD` in `StormDetector.py`
- Detection sensitivity: Adjust `MIN_READINGS_REQUIRED`
- Data retention: Modify cleanup interval in `PressureDatabase.delete_old_readings()`

### Alert Severity Mapping
Alert colors and refresh intervals are determined in `Alerter.get_alert_color()`. The system uses NWS severity and urgency fields to determine appropriate visual indicators and polling frequency.

### Database Schema
Pressure readings stored in SQLite with schema:
```sql
CREATE TABLE pressure_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pressure INTEGER NOT NULL,  -- millibars
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Logging

The application logs all events, errors, and debug information to `weather_alerter.log` in the project directory. This file is created automatically on first run and appends new log entries on each execution.

**Log Levels:**
- **INFO**: Normal operations (startup, display initialization, configuration changes)
- **WARNING**: Storm detections and non-critical issues
- **ERROR**: Recoverable errors (API failures, sensor read errors)
- **CRITICAL**: Fatal errors that cause application shutdown

**Log File Location:** `weather_alerter.log` in the project root directory

**Viewing Recent Logs:**
```bash
# View last 50 lines
tail -n 50 weather_alerter.log

# Follow log in real-time
tail -f weather_alerter.log

# Search for errors
grep -i error weather_alerter.log
```

## Troubleshooting

### SenseHat Connection Issues
- Verify SenseHat is properly seated on GPIO pins
- Check that `sense-hat` package is installed system-wide
- For emulator: Install `sense-emu` package
- GPIO permissions may require running as sudo or adding user to gpio group

### API Connectivity Problems
- Verify WeatherBox server is running and accessible
- Check network connectivity: `curl http://your-server:8080/health`
- Verify municipality name matches WeatherBox geocoding (try county names if city fails)
- Monitor application output for HTTP error messages

### Display Issues
- eInk display: Verify SPI is enabled and CE lines are properly configured
- Console display: Check terminal encoding supports Unicode characters
- Check display initialization errors in application startup output

### Performance Optimization
- Adjust `recheck_seconds` based on alert severity requirements
- Modify pressure reading interval (default 60 seconds) in `StormDetector.run()`
- Consider database vacuum operations for long-running deployments

## Dependencies and External Services

### Python Requirements
- `requests`: HTTP client for WeatherBox API
- System packages: `sense-hat`, `adafruit-circuitpython-epd`, `RPi.GPIO`, `Pillow`

### External Services
- WeatherBox API server (required) - provides weather alert data
- National Weather Service (via WeatherBox) - ultimate data source
- Local SenseHat sensors - atmospheric pressure readings
