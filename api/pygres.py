import psycopg2 as postgres

class PygreSQL:
    def __init__(self, database: str, user: str, password: str, host: str, port: str, ssl_mode: str):
        try:
            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode={ssl_mode}"
            self._connection = postgres.connect(connection_string)
            self._cursor = self._connection.cursor()
        except:
            raise Exception()

    def __call__(self, query: str):
        try:
            self._cursor.execute(query)
        except:
            raise Exception()

    def query(self, query: str):
        try:
            self._cursor.execute(query)
        except:
            raise Exception()
    
    def fetch(self):
        try:
            return self._cursor.fetchall()
        except:
            raise Exception()

    # this function creates a table if it does not exist
    # the function must have the columns lists as "<cloumn_name>: <data_type>"
    # contraints can be provided as needed using their name in lowecase
    # foreign key contraint values should be entered as table_name(column_name)
    def create(self, table: str, columns: dict, not_null: list = None, unique: list = None, primary_key: list = None, foreign_key: dict = None, default: dict = None, index: list = None):
        # the default lambda function for the dictionary comprehension
        check_default = lambda key, value: value + f" DEFAULT {default[key]}" if default is not None and key in default.keys() else value
        # the foreign key lambda function for the dictionary comprehension
        check_foreign_key = lambda key, value: value + f" REFERENCES {foreign_key[key]}" if foreign_key is not None and key in foreign_key.keys() else value

        # updating the values based on the lambda functions checks
        columns = {key: check_foreign_key(key, check_default(key, value)) for key, value in columns.items()}
        columns = [f"{key} {value}" for key, value in columns.items()] # creating the Postgres string from each pair
        # checking the other constraints
        if not_null is not None:
            not_null_columns = ", ".join([column for column in not_null])
            not_null = f"NOT NULL({not_null_columns})"
        if unique is not None:
            unique_columns =  ", ".join([column for column in unique])
            unique = f"UNIQUE({unique_columns})"
        if primary_key is not None:
            primary_key_columns = ", ".join([column for column in primary_key])
            primary_key = f"PRIMARY KEY({primary_key_columns})"

        # creating the parameter list for the query
        parameters = ", ".join([parameter for parameter in [*columns, not_null, unique, primary_key] if parameter is not None])

        if index is not None:
            index = ", ".join(index)

        # attempting to query the database
        try:
            self(f"CREATE TABLE IF NOT EXISTS {table}({parameters});")
            if index is not None:
                self(f"CREATE INDEX {table}_index ON {table}({index});")
        except:
            raise Exception()

    # this function is used to rename a table
    def rename(self, table: str, new_name: str):
        try:
            self(f"ALTER TABLE {table} RENAME TO {new_name};")
        except:
            raise Exception()

    # this function allows a user to drop a coulmn or constrain from a table by name
    def drop(self, table: str, cascade: bool = False):
        # attempting to query the database
        try:
            self._cursor.execute(f"DROP TABLE {table};" if not cascade else f"DROP TABLE {table} CASCADE;")
        except:
            raise Exception()

    # this function is used to add a column to the named table
    def add(self, table: str, column: str):
        try:
            self(f"ALTER TABLE IF EXISTS {table} ADD {column};")
        except:
            raise Exception()

    # this function is used to drop a column from the named table
    def remove(self, table: str, column: str):
        try:
            self(f"ALTER TABLE IF EXISTS {table} DROP {column};")
        except:
            raise Exception()

    # this function gets the column names associated with the named table
    # the function returns a list of the names
    def columns(self, table: str):
        try:
            self(f"SELECT * FROM information_schema.columns WHERE table_name = '{table}';")
            return [result[3] for result in self.fetch()]
        except:
            raise Exception()

    # this function allows the user to make selection queries
    # there are a number of filters the user can use based on PostgreSQL
    # this function returns python dict objects
    def select(self, table: str, columns: list = None, distinct: bool = False, where: str = None, having: str = None, group: str = None, order: str = None, limit: int = None, offset: int = None):
        # either the user names the columns they want from each row
        # or we use the wild card
        # the ids that are returned from this query are decided
        # by the user or the tables columns
        if columns is None:
            ids = self.columns(table)
            columns = '*'
        else:
            ids = columns
            columns = ", ".join(columns)

        if distinct is not None:
            columns = f"DISTINCT {columns}"

        # this section checks for every parameter
        if where is not None:
            where = f"WHERE {where}"
        if having is not None:
            having = f"HAVING {having}"
        if group is not None:
            group = f"GROUP BY {group}"
        if order is not None:
            order = f"ORDER BY {order}"
        if limit is not None:
            limit = f"LIMIT {limit}"
        if offset is not None:
            offset = f"OFFSET {offset}"
        # if any are not none, they are added to the parameter list
        parameters = [parameter for parameter in [where, having, group, order, limit, offset] if parameter is not None]
        parameters = ' '.join(parameters) if len(parameters) > 0 else None # joined
        # then the query is attempted
        try:
            self(f"SELECT {columns} FROM {table};" if parameters is None else f"SELECT {columns} FROM {table} {parameters};")
            results = self.fetch()
            return [{key: value for key, value in zip(ids, result)} for result in results]
        except:
            raise Exception()

    # insert a set of values into the database
    # this function takes either a list or a single item
    def insert(self, table: str, data: dict):
        keys = ", ".join(data.keys())
        values = tuple(data.values())
        # attempting to query the database
        try:
            self(f"INSERT INTO {table} ({keys}) VALUES {values};")
        except:
            raise Exception()

    # this function is used to update rows of a table with new information
    # the where clause is optional and can be used to filter results
    def update(self, table, set: dict, where: str = None):
        parameters = ", ".join([f"{key}='{value}'" for key, value in set.items()])
        try:
            self(f"UPDATE {table_name} SET {parameters};" if where is None else f"UPDATE {table_name} SET {parameters} WHERE {where};")
        except:
            raise Exception()

    # this function is used to delete data from the table
    # if no condition is provided, then all data is deleted
    def delete(self, table, where: str = None):
        try:
            self(f"DELETE FROM {table};" if where is None else f"DELETE FROM {table} WHERE {where};")
        except:
            raise Exception()

    def rollback(self):
        self._connection.rollback()

    # this function commits the changes to the 
    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()

