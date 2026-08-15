import sqlite3

class SQLiteService:

    def __init__(self, db_path):
        self.db_path = db_path

    def execute(self, query):
        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

        cursor.execute(query)

        columns = [c[0] for c in cursor.description]

        rows = cursor.fetchall()

        conn.close()

        return columns, rows
    
    def get_schema(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        schema = {}

        for (table_name,) in tables:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            schema[table_name] = [
                {
                    "name": column[1],
                    "type": column[2]
                }
                for column in columns
            ]
        conn.close()
        return schema