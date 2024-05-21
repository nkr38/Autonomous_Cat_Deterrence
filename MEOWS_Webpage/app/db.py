import sqlite3

class DataBase:
    def __init__(self, db_name = ':memory:'):
        self.db_name = db_name
        self.conn = None

    def connect_DB(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread = False)

    def disconnect_DB(self):
        if self.conn:
            self.conn.close()

    def create_table(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()

    def execute(self, query, parameters = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, parameters)
        self.conn.commit()

    def get_data(self, query, parameters = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, parameters)
        record = cursor.fetchall()
        return record
    
    def get_one(self, query, parameters = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, parameters)
        record = cursor.fetchone()
        return record

    def get_rows(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name}')
        return(cursor.fetchall())
    
    def get_device_info(self, table_name, serial):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name} WHERE serial_number = ?', [serial])
        record = cursor.fetchone()
        return record
    
    def add_rows(self, table_name, data):
        cols = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        query = f'INSERT INTO {table_name} ({cols}) VALUES ({placeholders})'
        cursor = self.execute(query, list(data.values()))
        self.conn.commit()

    