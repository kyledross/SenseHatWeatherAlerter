import sqlite3
import datetime
from typing import List, Tuple


class PressureDatabase:
    """
    A class to manage a SQLite database for storing pressure readings in millibars
    with timestamps.
    """

    def __init__(self, db_path: str = "pressure_readings.db"):
        """
        Initialize the database connection and create the table if it doesn't exist.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        """Create the pressure readings table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pressure_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pressure INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

    def insert_reading(self, pressure: int):
        """
        Insert a new pressure reading into the database.
        
        Args:
            pressure: Pressure reading in millibars
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO pressure_readings (pressure) VALUES (?)",
            (pressure,)
        )
        
        conn.commit()
        conn.close()

    def get_readings_last_hour(self) -> List[Tuple[int, datetime.datetime]]:
        """
        Get all pressure readings from the last hour.
        
        Returns:
            List of tuples containing (pressure, timestamp)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        
        cursor.execute(
            "SELECT pressure, timestamp FROM pressure_readings WHERE timestamp >= ? ORDER BY timestamp",
            (one_hour_ago.strftime("%Y-%m-%d %H:%M:%S"),)
        )
        
        results = [(row['pressure'], datetime.datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")) 
                  for row in cursor.fetchall()]
        
        conn.close()
        return results

    def delete_old_readings(self):
        """Delete all readings older than 5 hours."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        five_hours_ago = datetime.datetime.now() - datetime.timedelta(hours=5)
        
        cursor.execute(
            "DELETE FROM pressure_readings WHERE timestamp < ?",
            (five_hours_ago.strftime("%Y-%m-%d %H:%M:%S"),)
        )
        
        conn.commit()
        conn.close()