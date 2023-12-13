import mysql.connector
import os

from dotenv import load_dotenv

load_dotenv()


class Database:
    def init(self):
        """self.conn = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='flight_game',
            user='root',
            password='6661507',
            autocommit=True
        )"""

        self.conn = mysql.connector.connect(
            host=os.environ.get('HOST'),
            port=3306,
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            autocommit=True
        )

    def get_conn(self):
        return self.conn
