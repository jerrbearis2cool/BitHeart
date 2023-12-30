### Simple Postgresql database object ###

import psycopg2
import json


class Database:

    # initiate the database with given parameters
    def __init__(self, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT):
        self.DB_NAME = DB_NAME
        self.DB_USER = DB_USER
        self.DB_PASSWORD = DB_PASSWORD
        self.DB_HOST = DB_HOST
        self.DB_PORT = DB_PORT

        self.conn = psycopg2.connect(database=self.DB_NAME, user=self.DB_USER, password=self.DB_PASSWORD,
                                     host=self.DB_HOST, port=self.DB_PORT)

    # create a table if one does not exist
    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS user_data (
                    username VARCHAR PRIMARY KEY,
                    data JSONB
                )
            ''')
        self.conn.commit()

    # insert user data
    def insert_data(self, username, data):
        with self.conn.cursor() as cur:
            cur.execute('''
                INSERT INTO user_data (username, data) VALUES (%s, %s)
                ON CONFLICT (username) DO UPDATE SET data = %s
            ''', (username, json.dumps(data), json.dumps(data)))
        self.conn.commit()

    # export user data
    def get_data(self, username):
        with self.conn.cursor() as cur:
            cur.execute(
                'SELECT data FROM user_data WHERE username = %s', (username,))
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                return None
