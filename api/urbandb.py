import json
from os import system
import psycopg2 as postgres
from color import bold_bright_red, bold_bright_green, default

# "sessions/database-env.json"
class UrbanDB:
    def __init__(self, env_file):
        try:
            env = json.load(open(env_file, 'r'))
            self.connection = postgres.connect(env["DB_URL"])
            self.cursor = self.connection.cursor()

            # printing debug messages simiillar to kivy
            print(f"[{bold_bright_green}INFO{default}   ] [Postgres    ] Database connected successfully.")
        except json.JSONDecodeError:
            print(f"[{bold_bright_red}ERROR{default}  ] [JSON         ] Error Decoding the database JSON file.")
        except Exception as e:
            print(f"[{bold_bright_red}ERROR{default}  ] [Postgres     ] Database not connected successfully.")
            print(f"[{bold_bright_red}ERROR{default}  ] [             ] {e}.")

    def close(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()

    def create(self, table_name, **kwargs):
        try:
            columns = ", ".join([f"{key} {value}" for key, value in kwargs.items()])
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});")
        except Exception as e:
            print(f"[{bold_bright_red}ERROR{default}  ] [Postgres     ] Could not create table ({table_name}) in database.")
            print(f"[{bold_bright_red}ERROR{default}  ] [             ] {e}.")
    
    def drop(self, table_name):
        try:
            self.cursor.execute(f"DROP TABLE {table_name}")
        except Exception as e:
            print(f"[{bold_bright_red}ERROR{default}  ] [Postgres     ] Could not drop table ({table_name}) in database.")
            print(f"[{bold_bright_red}ERROR{default}  ] [             ] {e}.")

    def insert(self, table_name, data):
        try:
            column_keys = ", ".join([key for key in data.keys()])
            column_values = ", ".join([f"'{value}'" for value in data.values()])
            self.cursor.execute(f"INSERT INTO {table_name} ({column_keys}) VALUES ({column_values});")
        except Exception as e:
            print(f"[{bold_bright_red}ERROR{default}  ] [Postgres     ] Could not insert data into table ({table_name}).")
            print(f"[{bold_bright_red}ERROR{default}  ] [             ] {e}.")

    def delete(self, table_name, id):
        try:
            self.cursor.execute(f"DELETE FROM {table_name} WHERE id='{id}'")
        except Exception as e:
            print(f"[{bold_bright_red}ERROR{default}  ] [Postgres     ] Could not delete data from table ({table_name}).")
            print(f"[{bold_bright_red}ERROR{default}  ] [             ] {e}.")

    def update(self, table_name, id, **kwargs):
        try:
            parameters = ", ".join([f"{key}='{value}'" for key, value in kwargs.items()])
            self.cursor.execute(f"UPDATE {table_name} SET {parameters} WHERE id='{id}'")
        except Exception as e:
            print(f"[{bold_bright_red}ERROR{default}  ] [Postgres     ] Could not update data from table ({table_name}) for object {id}.")
            print(f"[{bold_bright_red}ERROR{default}  ] [             ] {e}.")
