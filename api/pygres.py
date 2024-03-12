import psycopg2 as postgres

class PygreSQL:
    def __init__(self, database: str, user: str, password: str, host: str, port: str, ssl_mode: str):
        try:
            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode={ssl_mode}"
            self._connection = postgres.connect(connection_string)
            self._cursor = self._connection.cursor()
        except Exception as error:
            raise ConnectionError("Error while connecting to database: " + str(error))

    def __call__(self, query: str):
        try:
            self._cursor.execute(query)
        except Exception as error:
            raise QueryError("Error while executing query: " + str(error))
    
    def fetch(self):
        try:
            return self._cursor.fetchall()
        except Exception as error:
            raise FetchError("Error while attempting to fetch from cursor: " + str(error))

    def extend(self, extension: str):
        self(f"CREATE EXTENSION IF NOT EXISTS {extension};")

    def trigger(self, trigger):
        pass

    def function(self, name: str, definition: str):
        pass

    def index(self, table: str, columns: list):
        index = ", ".join(columns)
        self(f"CREATE INDEX IF NOT EXISTS {table}_index ON {table}({index});")

    def gin(self, table: str, columns: list):
        index = " || ' ' || ".join([f"coalesce({column}, '')" for column in columns])
        
        self(f"ALTER TABLE IF EXISTS {table} ADD COLUMN IF NOT EXISTS index tsvector;")
        self(f"UPDATE {table} SET index = to_tsvector('english', {index});")
        self(f"CREATE INDEX IF NOT EXISTS {table}_index ON {table} USING GIN(index);")

    def regin(self, table, columns: list):
        index = " || ' ' || ".join([f"coalesce({column}, '')" for column in columns])
        self(f"UPDATE {table} SET index = to_tsvector('english', {index});")

    # this function creates a table if it does not exist
    # the function must have the columns lists as "<cloumn_name>: <data_type>"
    # contraints can be provided as needed using their name in lowecase
    # foreign key contraint values should be entered as table_name(column_name)
    def create(self, table: str, columns: dict, not_null: list = None, unique: list = None, primary_key: list = None, foreign_key: dict = None, default: dict = None):
        # the default lambda function for the dictionary comprehension
        check_default = lambda key, value: value + f" DEFAULT {default[key]}" if default is not None and key in default.keys() else value
        # the foreign key lambda function for the dictionary comprehension
        check_foreign_key = lambda key, value: value + f" REFERENCES {foreign_key[key]} ON DELETE CASCADE ON UPDATE CASCADE" if foreign_key is not None and key in foreign_key.keys() else value

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

        # attempting to query the database
        self(f"CREATE TABLE IF NOT EXISTS {table}({parameters});")

    # this function is used to rename a table
    def rename(self, table: str, new_name: str):
        self(f"ALTER TABLE IF EXISTS {table} RENAME TO {new_name};")

    # this function allows a user to drop a coulmn or constrain from a table by name
    def drop(self, table: str, cascade: bool = False):
        # attempting to query the database
        self._cursor.execute(f"DROP TABLE IF EXISTS {table};" if not cascade else f"DROP TABLE IF EXISTS {table} CASCADE;")

    # this function is used to add a column to the named table
    def add(self, table: str, column: tuple):
        name, data_type = column
        self(f"ALTER TABLE IF EXISTS {table} ADD COLUMN IF NOT EXISTS {name} {data_type};")

    # this function is used to drop a column from the named table
    def remove(self, table: str, column: str):
        self(f"ALTER TABLE IF EXISTS {table} DROP COLUMN IF EXISTS {column};")

    # this function gets the column names associated with the named table
    # the function returns a list of the names
    def columns(self, table: str):
        self(f"SELECT * FROM information_schema.columns WHERE table_name = '{table}';")
        return [result[3] for result in self.fetch()]

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
        elif "*" in columns:
            ids = self.columns(table)
            columns = ", ".join(columns)
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
        self(f"SELECT {columns} FROM {table};" if parameters is None else f"SELECT {columns} FROM {table} {parameters};")
        results = self.fetch()
        return [{key: value for key, value in zip(ids, result)} for result in results]

    # insert a set of values into the database
    # this function takes either a list or a single item
    def insert(self, table: str, data: dict):
        keys = ", ".join(data.keys())
        values = tuple(data.values())
        # attempting to query the database
        self(f"INSERT INTO {table} ({keys}) VALUES {values};")

    # this function is used to update rows of a table with new information
    # the where clause is optional and can be used to filter results
    def update(self, table, set: dict, where: str = None):
        parameters = ", ".join([f"{key}='{value}'" for key, value in set.items()])
        self(f"UPDATE {table} SET {parameters};" if where is None else f"UPDATE {table} SET {parameters} WHERE {where};")

    # this function is used to delete data from the table
    # if no condition is provided, then all data is deleted
    def delete(self, table, where: str = None):
        self(f"DELETE FROM {table};" if where is None else f"DELETE FROM {table} WHERE {where};")

    def rollback(self):
        try:
            self._connection.rollback()
        except Exception as error:
            raise RollbackError("Error when attempting to rollback database: " + str(error))

    # this function commits the changes to the 
    def commit(self):
        try:
            self._connection.commit()
        except Exception as error:
            raise CommitError("Error while attempting to commit: " + str(error))

    def close(self):
        self._connection.close()

class ConnectionError(Exception):
    pass

class QueryError(Exception):
    pass

class FetchError(Exception):
    pass

class RollbackError(Exception):
    pass

class CommitError(Exception):
    pass

