import logging
import os
from time import sleep
from typing import Callable, Optional

from Detection.PressureDatabase import PressureDatabase


class StormDetector:
    # Pressure drop thresholds in millibars that indicate a potential storm
    # Real storms typically show 3-5+ mb/hour drops, not gradual changes
    THREE_HOUR_PRESSURE_DROP_THRESHOLD = 6  # 2 mb/hour average
    ONE_HOUR_PRESSURE_DROP_THRESHOLD = 3    # 3 mb/hour
    # Minimum number of readings required before we can detect a storm
    MIN_READINGS_REQUIRED = 10  # Need more data for reliable trend analysis

    def __init__(self, storm_detected_callback: Optional[Callable[[str], None]] = None, db_path: str = "pressure_readings.db"):
        """
        Initialize StormDetector with an optional callback function.
        Args:
            storm_detected_callback: Optional function that takes a string message parameter
            db_path: Path to the SQLite database file
        """
        # Ensure the DB path is rooted at the project directory so it doesn't depend on cwd
        if not os.path.isabs(db_path):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, db_path)
        self._storm_detected_callback = storm_detected_callback
        self._db = PressureDatabase(db_path)
        self._sense_hat = None
        self._sense_hat_present: bool = self._initialize_sense_hat()
        self._last_pressure: int = 0
        self.logger = logging.getLogger(__name__)

    def _initialize_sense_hat(self) -> bool:
        """Initialize the Sense HAT or its emulator."""
        try:
            # Try to import the real Sense HAT library first
            from sense_hat import SenseHat
            self._sense_hat = SenseHat()
            logging.getLogger(__name__).info("SenseHat hardware initialized")
            return True
        except Exception:
            try:
                # Fall back to the emulator if the real one isn't available
                from sense_emu import SenseHat
                self._sense_hat = SenseHat()
                logging.getLogger(__name__).info("SenseHat emulator initialized")
                return True
            except Exception as e:
                logging.getLogger(__name__).warning(f"No SenseHat available: {e}")
                return False

    def sense_hat_present(self) -> bool:
        """Return True if the Sense HAT is detected, False otherwise."""
        return self._sense_hat_present

    def run(self):
        """
        Main loop that reads pressure data, stores it in the database,
        and checks for storm conditions.
        """
        self.logger.info("Storm detector thread started")
        while self._sense_hat_present:
            try:
                # Read current pressure from the Sense HAT
                current_pressure = int(self._sense_hat.get_pressure())

                # Store the reading in the database
                self._db.insert_reading(current_pressure)

                # Clean up old readings
                self._db.delete_old_readings()

                # Check for storm conditions
                self._check_for_storm()
            except Exception as e:
                self.logger.error(f"Error in storm detection loop: {e}", exc_info=True)

            # Wait before taking the next reading
            sleep(60)

    def _check_for_storm(self):
        """
        Check for storm conditions based on pressure readings.
        Detects both rapid pressure drops and accelerating pressure drops.
        """
        last_hour_readings = self._db.get_readings_last_hour()
        last_three_hour_readings = self._db.get_readings_last_three_hours()

        # Need sufficient readings to detect a reliable trend
        if len(last_hour_readings) < self.MIN_READINGS_REQUIRED:
            return
        
        if len(last_three_hour_readings) < self.MIN_READINGS_REQUIRED:
            return

        # Sort readings by timestamp (oldest first)
        last_hour_readings.sort(key=lambda x: x[1])
        last_three_hour_readings.sort(key=lambda x: x[1])

        # Get pressure values
        one_hour_oldest_reading = last_hour_readings[0][0]
        three_hour_oldest_reading = last_three_hour_readings[0][0]
        newest_reading = last_hour_readings[-1][0]

        one_hour_pressure_change = newest_reading - one_hour_oldest_reading
        three_hour_pressure_change = newest_reading - three_hour_oldest_reading

        # Check for rapid pressure drops (indicating possible storm)
        if one_hour_pressure_change < -self.ONE_HOUR_PRESSURE_DROP_THRESHOLD:
            self.notify_storm(one_hour_pressure_change, "1 hour")
            self._last_pressure = newest_reading
            return
        
        if three_hour_pressure_change < -self.THREE_HOUR_PRESSURE_DROP_THRESHOLD:
            # Also check if the drop is accelerating (recent drop faster than average)
            if self._is_accelerating_drop(last_three_hour_readings):
                self.notify_storm(three_hour_pressure_change, "3 hours (accelerating)")
                self._last_pressure = newest_reading
                return
            
            self.notify_storm(three_hour_pressure_change, "3 hours")
        
        self._last_pressure = newest_reading
    
    def _is_accelerating_drop(self, readings: list) -> bool:
        """
        Check if pressure drop is accelerating (recent rate faster than overall rate).
        This helps distinguish storms from gradual weather changes.
        
        Args:
            readings: List of (pressure, timestamp) tuples sorted by timestamp
            
        Returns:
            True if the pressure drop rate is accelerating
        """
        if len(readings) < 20:  # Need enough data points
            return False
        
        # Compare first hour rate vs last hour rate
        first_hour = readings[:len(readings)//3]
        last_hour = readings[-len(readings)//3:]
        
        if len(first_hour) < 2 or len(last_hour) < 2:
            return False
        
        # Calculate rate of change for each period
        first_hour_rate = (first_hour[-1][0] - first_hour[0][0]) / len(first_hour)
        last_hour_rate = (last_hour[-1][0] - last_hour[0][0]) / len(last_hour)
        
        # Accelerating if recent rate is at least 50% faster than early rate
        return last_hour_rate < first_hour_rate * 1.5

    def notify_storm(self, pressure_drop=None, time_period="unknown"):
        """
        Notify about a detected storm.

        Args:
            pressure_drop: Optional pressure drop value to include in the message
            time_period: Time period over which the drop occurred
        """
        if self._storm_detected_callback:
            message = "Storm detected."
            if pressure_drop is not None:
                message += f" Pressure dropped by {abs(pressure_drop)} millibars over {time_period}."
            self.logger.warning(f"Storm detected: pressure drop = {pressure_drop}mb over {time_period}")
            self._storm_detected_callback(message)
        
