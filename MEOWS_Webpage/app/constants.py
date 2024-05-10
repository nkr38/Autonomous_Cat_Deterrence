DEVICE_TABLE = '''CREATE TABLE IF NOT EXISTS device (
                serial_number INTEGER PRIMARY KEY,
                device_name TEXT NOT NULL,
                active BOOLEAN NOT NULL
            )'''

DETECTION_TABLE = '''CREATE TABLE IF NOT EXISTS detection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial_number INTEGER NOT NULL,
                detection_datetime DATETIME NOT NULL
            )'''

AVAILABLE_SERIALS = [1225357956]

DETECTION_MOMENTS = []