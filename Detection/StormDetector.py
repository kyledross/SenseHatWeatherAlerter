from time import sleep
from typing import Callable, Optional

from Detection.PressureDatabase import PressureDatabase


class StormDetector:
    # Pressure drop threshold in millibars that indicates a potential storm
    THREE_HOUR_PRESSURE_DROP_THRESHOLD = 3
    ONE_HOUR_PRESSURE_DROP_THRESHOLD = 2
    # Minimum number of readings required before we can detect a storm
    MIN_READINGS_REQUIRED = 3

    def __init__(self, storm_detected_callback: Optional[Callable[[str], None]] = None, db_path: str = "pressure_readings.db"):
        """
        Initialize StormDetector with an optional callback function.
        Args:
            storm_detected_callback: Optional function that takes a string message parameter
            db_path: Path to the SQLite database file
        """
        self._storm_detected_callback = storm_detected_callback
        self._db = PressureDatabase(db_path)
        self._sense_hat = None
        self._sense_hat_present: bool = self._initialize_sense_hat()
        self._last_pressure: int = 0

    def _initialize_sense_hat(self) -> bool:
        """Initialize the Sense HAT or its emulator."""
        try:
            # Try to import the real Sense HAT library first
            from sense_hat import SenseHat
            self._sense_hat = SenseHat()
            return True
        except Exception:
            try:
                # Fall back to the emulator if the real one isn't available
                from sense_emu import SenseHat
                self._sense_hat = SenseHat()
                return True
            except Exception:
                return False

    def sense_hat_present(self) -> bool:
        """Return True if the Sense HAT is detected, False otherwise."""
        return self._sense_hat_present

    def run(self):
        """
        Main loop that reads pressure data, stores it in the database,
        and checks for storm conditions.
        """
        while self._sense_hat_present:
            # Read current pressure from the Sense HAT
            current_pressure = int(self._sense_hat.get_pressure())

            # Store the reading in the database
            self._db.insert_reading(current_pressure)

            # Clean up old readings
            self._db.delete_old_readings()

            # Check for storm conditions
            self._check_for_storm()

            # Wait before taking the next reading
            sleep(60)

    def _check_for_storm(self):
        """
        Check for storm conditions based on pressure readings from the last hour.
        A rapid drop in pressure can indicate an approaching storm.
        """
        last_hour_readings = self._db.get_readings_last_hour()
        last_three_hour_readings = self._db.get_readings_last_three_hours()

        # Need at least a few readings to detect a trend
        if len(last_hour_readings) < self.MIN_READINGS_REQUIRED:
            return

        # Sort readings by timestamp (oldest first)
        last_hour_readings.sort(key=lambda x: x[1])
        last_three_hour_readings.sort(key=lambda x: x[1])

        # Check if there's been a significant drop in pressure
        one_hour_oldest_reading = last_hour_readings[0][0]
        three_hour_oldest_reading = last_three_hour_readings[0][0]
        newest_reading = last_hour_readings[-1][0]

        one_hour_pressure_change = newest_reading - one_hour_oldest_reading
        three_hour_pressure_change = newest_reading - three_hour_oldest_reading

        # A significant drop in pressure may indicate a storm
        if newest_reading < self._last_pressure: # only alert if pressure keeps dropping
            if one_hour_pressure_change <= -self.ONE_HOUR_PRESSURE_DROP_THRESHOLD:
                self.notify_storm(one_hour_pressure_change)
            elif three_hour_pressure_change <= -self.THREE_HOUR_PRESSURE_DROP_THRESHOLD:
                self.notify_storm(three_hour_pressure_change)
        self._last_pressure = newest_reading

    def notify_storm(self, pressure_drop=None):
        """
        Notify about a detected storm.

        Args:
            pressure_drop: Optional pressure drop value to include in the message
        """
        if self._storm_detected_callback:
            message = "Storm detected."
            if pressure_drop is not None:
                message += f" Pressure dropped by {abs(pressure_drop)} millibars in the last hour."
            self._storm_detected_callback(message)
