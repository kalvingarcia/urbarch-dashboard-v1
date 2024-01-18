import json
import psycopg2 as postgres

# Matching the info color of Kivy loading
green_text = '\033[1;92m'
default_text = '\033[0m'

# "sessions/database-env.json"
class UrbanDB:
    def __init__(self, env_file):
        try:
            self.env = json.load(open(env_file, 'r'))
            self.connection = postgres.connect(self.env["DB_URL"])
            print(f"[{green_text}INFO{default_text}   ] [Postgres    ] Database connected successfully.")
        except json.JSONDecodeError:
            print(f"[{green_text}INFO{default_text}   ] [JSON        ] Error Decoding the database JSON file.")
        except:
            print(f"[{green_text}INFO{default_text}   ] [Postgres     ] Database not connected successfully.")

    def create(self):
        pass