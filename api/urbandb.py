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

    def print_table(self, table_name):
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            for row in rows:
                print('\t\t'.join(row))
        except Exception as e:
            print(f"[{bold_bright_red}ERROR{default}  ] [Postgres     ] Could not print data from table ({table_name}).")
            print(f"[{bold_bright_red}ERROR{default}  ] [             ] {e}.")

if __name__ == "__main__":
    def menu():
        print("1. ADD PRODUCTS")
        print("2. DELETE PRODUCTS")
        print("3. UPDATE PRODUCT")
        print("4. RESET DATABASE")
        print("5. PRINT DATABASE")
        print("6. COMMIT TO DATABASE")
        print("Q. QUIT")
        return input("CHOICE: ")

    def keep_going():
        choice = input("Keep going? (Y / N): ")
        if choice.upper() == 'Y':
            return 0

    def confirm():
        choice = input("Are you sure? (Y / N): ")
        if choice.upper() == 'Y':
            return 0

    def commit():
        choice = input("Commit changes? (Y / N): ")
        if choice.upper() == 'Y':
            return 0

    urb = UrbanDB("sessions/database-env.json")

    quit = False
    while not quit:
        choice = menu()
        if choice == '1':
            while keep_going() is not None:
                prod_json = {}

                prod_json["id"] = input("Enter the product UA ID: ")
                prod_json["name"] = input("Enter the product name: ")
                prod_json["url"] = input("Enter the product URL: ")

                urb.insert("small_search", prod_json)
        elif choice == '2':
            while keep_going() is not None:
                id = input("Enter the product UA ID: ")
                urb.delete("small_search", id)
        elif choice == '3':
            prod_json = {}

            prod_json["id"] = input("Enter the product UA ID: ")
            prod_json["name"] = input("Enter the new product name: ")
            prod_json["url"] = input("Enter the new product URL: ")

            urb.update("small_search", prod_json["id"], name=prod_json["name"], url=prod_json["url"])

            keep_going()
        elif choice == '4' and confirm() is not None:
            urb.drop("small_search")
            urb.create("small_search", id="TEXT UNIQUE", name="TEXT", url="TEXT")
        elif choice == '5':
            urb.print_table("small_search")
            keep_going()
        elif choice == '6' and confirm is not None:
            urb.commit()
        elif choice.upper() == 'Q':
            if commit() is not None:
                urb.commit()
            urb.close()
            quit = True
        else:
            print(print(f"[{bold_bright_red}ERROR{default}  ] [UrbanDB      ] Option invalid please try again."))

        system("clear")