import json
import re
from os import system
import psycopg2 as postgres

class Pygres:
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

class Database:
    _pygres = None

    @classmethod
    def _error(cls):
        cls._pygres.rollback()

    @classmethod
    def _complete_action(cls):
        cls._pygres.commit()

    @classmethod
    def connect(cls, env_file):
        try:
            if cls._pygres is None:
                env = json.load(open(env_file, 'r'))
                cls._pygres = Pygres(*env.values())
        except:
            raise Exception()

    @classmethod
    def reset(cls):
        for table in ["finishes", "product_listing", "product_variations", "instock_listing", "instock_items", "salvage_listing", "salvage_items",
            "custom_items",
            "tag_categories", "tag", "product_variation__tag", "instock_listing__tag", "salvage_listing__tag", "custom_items__tag"]:
            cls._pygres(f"DROP TABLE {table} CASCADE;")

    @classmethod
    def initialize(cls):
        cls._pygres("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

        # Product Related Tables
        cls._pygres('''
            CREATE TABLE IF NOT EXISTS finishes(
                id VARCHAR(5),
                name VARCHAR(255),
                outdoor BOOL
            );
        ''')
        cls._pygres(f'''
            INSERT INTO finishes(id, name, outdoor)
            VALUES {", ".join([f"{value}" for value in [
                ("PB", "Polished Brass", "YES"),
                ("PN", "Polished Nickel", "YES"),
                ("GP", "Green Patina", "YES"),
                ("BP", "Brown Patina", "YES"),
                ("AB", "Antique Brass", "YES"),
                ("SN", "Satin Nickel", "YES"),
                ("LP", "Light Pewter", "YES"),
                ("STBR", "Statuary Brown", "NO"),
                ("STBL", "Statuary Black", "NO"),
                ("PC", "Polished Chrome", "YES"),
                ("BN", "Black Nickel", "YES")
            ]])};
        ''')

        cls._pygres('''
            CREATE TABLE IF NOT EXISTS product_listing(
                id VARCHAR(10) PRIMARY KEY,
                name VARCHAR(255),
                description TEXT
            );
        ''')
        cls._pygres("ALTER TABLE IF EXISTS product_listing ADD COLUMN IF NOT EXISTS index tsvector;")
        cls._pygres("CREATE INDEX IF NOT EXISTS product_listing_index ON product_listing USING GIN(index);")

        cls._pygres('''
            CREATE TABLE IF NOT EXISTS product_variation(
                extension VARCHAR(10),
                subname VARCHAR(255),
                featured BOOL,
                price INT,
                display BOOL,
                overview JSONB,
                listing_id VARCHAR(10) REFERENCES product_listing(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        cls._pygres("ALTER TABLE IF EXISTS product_variation ADD COLUMN IF NOT EXISTS index tsvector;")
        cls._pygres("CREATE INDEX IF NOT EXISTS product_variation_index ON product_variation USING GIN(index);")

        cls._pygres('''
            CREATE TABLE IF NOT EXISTS instock_listing(
                id SERIAL PRIMARY KEY,
                sale BOOL,
                price INT,
                listing_id VARCHAR(7) REFERENCES product_listing(id) ON DELETE CASCADE ON UPDATE CASCADE,
                variation_extension VARCHAR(10)
            );
        ''')
        cls._pygres('''
            CREATE TABLE IF NOT EXISTS instock_items(
                serial INT,
                display BOOL,
                overview JSONB,
                listing_id INT REFERENCES instock_listing(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')

        cls._pygres('''
            CREATE TABLE IF NOT EXISTS salvage_listing(
                id VARCHAR(10) PRIMARY KEY,
                name VARCHAR(255),
                description TEXT
            );
        ''')
        cls._pygres("ALTER TABLE IF EXISTS salvage_listing ADD COLUMN IF NOT EXISTS index tsvector;")
        cls._pygres("CREATE INDEX IF NOT EXISTS salvage_listing_index ON salvage_listing USING GIN(index);")

        cls._pygres('''
            CREATE TABLE IF NOT EXISTS salvage_item(
                serial INT,
                price INT,
                display BOOL,
                overview JSONB,
                listing_id VARCHAR(10) REFERENCES salvage_listing(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')

        # Gallery Related Tables
        cls._pygres('''
            CREATE TABLE IF NOT EXISTS custom_item(
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                description TEXT,
                customer VARCHAR(255),
                display BOOL,
                listing_id VARCHAR(10),
                variation_extension VARCHAR(10)
            );
        ''')
        cls._pygres("ALTER TABLE IF EXISTS custom_item ADD COLUMN IF NOT EXISTS index tsvector;")
        cls._pygres("CREATE INDEX IF NOT EXISTS custom_item_index ON custom_item USING GIN(index);")

        # Tag Related Tables
        cls._pygres('''
            CREATE TABLE IF NOT EXISTS tag_category(
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                description TEXT
            );
        ''')
        cls._pygres(f'''
            INSERT INTO tag_category(name, description)
            VALUES {", ".join([f"{value}" for value in [
                ("Class", "Whether the item is a(n) Lighting, Bathroom, Washstands, Furnishing, Mirrors, Cabinets, Display, Hardware, Tile"),
                ("Category", "The order of the classification, such as sconce, hanging, flushmount, etc."),
                ("Style", "The artistic period that the item is from."),
                ("Family", "The stuctural grouping of the item, such as \"torch\" for Loft Light, Urban Torch, etc."),
                ("Designer", "The name of the designer who created the piece."),
                ("Material", "The type of materials used to create the item, such as alabaster, marble, aluminum, brass, etc."),
                ("Distinction", "Specifically for lighting used to distinguish exterior and interior."),
                ("Environmental", "Specifies any environmental conditions the item can be used in, such as waterproof.")
            ]])};
        ''')

        cls._pygres('''
            CREATE TABLE IF NOT EXISTS tag(
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                category_id INT REFERENCES tag_category(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        cls._pygres("ALTER TABLE IF EXISTS tag ADD COLUMN IF NOT EXISTS index tsvector;")
        cls._pygres("CREATE INDEX IF NOT EXISTS tag_index ON tag USING GIN(index);")

        cls._pygres('''
            CREATE TABLE IF NOT EXISTS product_variation__tag(
                listing_id VARCHAR(10) REFERENCES product_listing(id) ON DELETE CASCADE ON UPDATE CASCADE,
                variation_extension VARCHAR(10),
                tag_id INT REFERENCES tag(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        cls._pygres('''
            CREATE TABLE IF NOT EXISTS instock_item__tag(
                listing_id INT REFERENCES instock_listing(id) ON DELETE CASCADE ON UPDATE CASCADE,
                item_serial INT,
                tag_id INT REFERENCES tag(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        cls._pygres('''
            CREATE TABLE IF NOT EXISTS salvage_item__tag(
                listing_id VARCHAR(10) REFERENCES salvage_listing(id) ON DELETE CASCADE ON UPDATE CASCADE,
                item_serial INT,
                tag_id INT REFERENCES tag(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        cls._pygres('''
            CREATE TABLE IF NOT EXISTS custom_item__tag(
                item_id INT REFERENCES custom_item(id) ON DELETE CASCADE ON UPDATE CASCADE,
                tag_id INT REFERENCES tag(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')

        cls._complete_action()

    @classmethod
    def get_metal_finishes_list(cls):
        try:
            cls._pygres("SELECT * FROM finishes;")
            results = cls._pygres.fetch()
            return [{key: value for key, value in zip(["id", "name", "outdoor"], result)} for result in results]
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    @classmethod
    def get_tag_category_list(cls):
        try:
            cls._pygres("SELECT * FROM tag_category;")
            results = cls._pygres.fetch()
            return [{key: value for key, value in zip(["id", "name", "description"], result)} for result in results]
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    # TAG METHODS
    @classmethod
    def get_filter_list(cls, of = "products", search: str = "", filters: dict = {}):
        try:
            cls._pygres(f'''
                {
                    f'''
                        WITH search_filtered AS (
                            SELECT DISTINCT product_variation.listing_id AS listing_id, product_variation.extension as variation_extension
                            FROM product_listing INNER JOIN product_variation ON product_variation.listing_id = product_listing.id
                            WHERE product_listing.index @@ to_tsquery('{search + ':*'}') OR product_variation.index @@ to_tsquery('{search + ':*'}')
                        ),
                    ''' if search != ""
                    else ""
                }
                {
                    f'''
                        {"WITH" if search == "" else ""} tag_filtered AS (
                            {" INTERSECT ".join([
                                f'''
                                    SELECT DISTINCT listing_id, variation_extension
                                    FROM product_variation__tag
                                    WHERE tag_id = ANY ARRAY[{", ".join([f"'{id}'" for id in ids])}]
                                '''
                            ] for ids in filters.values())}
                        ),
                    ''' if len(filters) != 0
                    else ""
                }
                {"WITH" if search == "" and len(filters) == 0 else ""} variations AS (
                    SELECT DISTINCT listing_id, variation_extension
                    FROM product_variation__tag
                        {"INNER JOIN search_filtered USING(listing_id, variation_extension)" if search != "" else ""}
                        {"INNER JOIN tag_filtered USING(listing_id, variation_extension)" if len(filters) != 0 else ""}
                )
                SELECT id, name, (
                    SELECT COALESCE(json_agg(json_build_object(
                        'id', CAST(tag.id AS TEXT),
                        'name', tag.name,
                        'category', tag_category.name
                    )), '[]') FROM tag
                    WHERE tag.category_id = tag_category.id AND (tag.id IN (
                        SELECT DISTINCT tag_id 
                        FROM product_variation__tag
                        WHERE (listing_id, variation_extension) IN (SELECT listing_id, variation_extension FROM variations)
                    ) OR tag_category.name = 'Class')
                ) AS tags
                FROM tag_category;
            ''')
            results = cls._pygres.fetch()
            return [{key: value for key, value in zip(["id", "name", "tags"], result)} for result in results]
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    @classmethod
    def get_tag_list(cls, search: str = ""):
        try:
            cls._pygres(f'''
                {
                    f'''
                        WITH search_filtered AS (
                            SELECT DISTINCT id FROM tag WHERE index @@ to_tsquery('{search + ':*'}')
                        )
                    ''' if search != ""
                    else ""
                }
                SELECT tag.id AS id, tag.name AS name, tag_category.name AS category
                FROM tag INNER JOIN tag_category ON tag.category_id = tag_category.id
                {"WHERE tag.id IN (SELECT * FROM search_filtered)" if search != "" else ""};
            ''')
            results = cls._pygres.fetch()
            return [{key: value for key, value in zip(["id", "name", "category"], result)} for result in results]
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    @classmethod
    def get_tag(cls, id):
        try:
            cls._pygres(f"SELECT * FROM tag WHERE id = '{id}';")
            result = cls._pygres.fetch()[0]
            return {key: value for key, value in zip(["id", "name", "category_id"], result)}
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    # REGIN f'''
    #   UPDATE {}} 
    #   SET index = to_tsvector('english', {" || ' ' || ".join([f"COALESCE({column}, '')" for column in []])})
    #   WHERE id = {};
    # '''
    @classmethod
    def create_tag(cls, data: dict):
        try:
            columns = ", ".join(data.keys())
            values = tuple(data.values())

            cls._pygres(f"INSERT INTO tag({columns}) VALUES {values} RETURNING id;")
            id = cls._pygres.fetch()[0][0]
            cls._pygres(f'''
                UPDATE tag
                SET index = to_tsvector('english', {" || ' ' || ".join([f"COALESCE({column}, '')" for column in ["name"]])})
                WHERE id = '{id}';
            ''')
            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    @classmethod
    def update_tag(cls, id, data):
        try: 
            cls._pygres(f'''
                UPDATE tag
                SET {", ".join([f"{key} = '{value}'" for key, value in data.items()])}
                WHERE id = '{id}' RETURNING id;
            ''')
            id = cls._pygres.fetch()[0][0]
            cls._pygres(f'''
                UPDATE tag
                SET index = to_tsvector('english', {" || ' ' || ".join([f"COALESCE({column}, '')" for column in ["name"]])})
                WHERE id = '{id}';
            ''')
            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    @classmethod
    def delete_tag(cls, id):
        try:
            cls._pygres(f"DELETE FROM tag WHERE id = '{id}';")
            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    # PRODUCT METHODS
    @classmethod
    def get_replacement_list(cls, search: str = ""):
        try:
            cls._pygres(f'''
                {
                    f'''
                        WITH search_filtered AS (
                            SELECT DISTINCT product_variation.listing_id AS id, product_variation.extension AS extension
                            FROM product_listing INNER JOIN product_variation ON product_variation.listing_id = product_listing.id
                            WHERE product_listing.index @@ to_tsquery('{search + ':*'}') OR product_variation.index @@ to_tsquery('{search + ':*'}')
                        )
                    ''' if search != "" 
                    else ""
                }
                SELECT DISTINCT json_build_object(
                    'id', product_variation.listing_id,
                    'extension', product_variation.extension
                ) AS id, product_listing.name AS name, product_variation.subname AS subname
                FROM product_listing INNER JOIN product_variation ON product_variation.listing_id = product_listing.id
                    INNER JOIN product_variation__tag ON product_variation__tag.listing_id = product_variation.listing_id
                        AND product_variation__tag.variation_extension = product_variation.extension
                    INNER JOIN tag ON tag.id = product_variation__tag.tag_id
                    {"INNER JOIN search_filtered USING(id, extension)" if search != "" else ""}
                WHERE tag.name = 'Replacement';
            ''')

            results = cls._pygres.fetch()
            return [{key: value for key, value in zip(["id", "name", "subname"], result)} for result in results]
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    @classmethod
    def get_replacement(cls, id, extension):
        try:
            cls._pygres(f'''
                SELECT json_build_object(
                    'id', product_variation.listing_id, 
                    'extension', product_variation.extension
                ) AS id, product_listing.name AS name
                FROM product_listing INNER JOIN product_variation ON product_listing.id = product_variation.listing_id
                WHERE product_listing.id = '{id}' AND product_variation.extension = '{extension}';
            ''')
            result = cls._pygres.fetch()[0]
            return {key: value for key, value in zip(["id", "name"], result)}
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    @classmethod
    def get_product_list(cls, search: str = "", filters: dict = {}):
        try:
            cls._pygres(f'''
                {
                    f'''
                        WITH search_filtered AS (
                            SELECT DISTINCT product_variation.listing_id AS id
                            FROM product_listing INNER JOIN product_variation ON product_variation.listing_id = product_listing.id
                            WHERE product_listing.index @@ to_tsquery('{search + ':*'}') OR product_variation.index @@ to_tsquery('{search + ':*'}')
                        ),
                    ''' if search != "" 
                    else ""
                }
                {
                    f'''
                        {"WITH" if search == "" else ""} tag_filtered AS (
                            {" INTERSECT ".join([
                                f'''
                                    SELECT DISTINCT product_variation__tag.listing_id AS id
                                    FROM product_variation__tag
                                    WHERE tag_id = ANY ARRAY[{", ".join([f"'{id}'" for id in ids])}]
                                ''' for ids in filters.values()
                            ])}
                        ),
                    ''' if len(filters) != 0
                    else ""
                }
                {"WITH" if search == "" and len(filters) == 0 else ""} results AS (
                    SELECT id, name, description
                    FROM product_listing
                        {"INNER JOIN search_filtered USING(id)" if search != "" else ""}
                        {"INNER JOIN tag_filtered USING(id)" if len(filters) != 0 else ""}
                )
                SELECT DISTINCT * FROM results;
            ''')
            results = cls._pygres.fetch()
            return [{key: value for key, value in zip(["id", "name", "category"], result)} for result in results]
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []


    @classmethod
    def get_product(cls, id):
        try:
            cls._pygres(f'''
                WITH variations AS (
                    SELECT extension, subname, featured, price, display, overview, (
                        SELECT COALESCE(ARRAY_AGG(tag.id), '{{}}')
                        FROM tag INNER JOIN tag_category ON tag.category_id = tag_category.id
                            INNER JOIN product_variation__tag ON product_variation__tag.tag_id = tag.id
                        WHERE product_variation__tag.listing_id = '{id}' AND product_variation__tag.variation_extension = extension
                    ) AS tags
                    FROM product_variation WHERE listing_id = '{id}'
                )
                SELECT id, name, description, (
                    SELECT COALESCE(json_agg(json_build_object(
                        'extension', extension,
                        'subname', subname,
                        'featured', featured,
                        'price', price,
                        'display', display,
                        'overview', overview,
                        'tags', tags
                    )), '[]') FROM variations
                ) as variations
                FROM product_listing WHERE id = '{id}';
            ''')

            result = cls._pygres.fetch()[0]
            return {key: value for key, value in zip(["id", "name", "description", "variations"], result)}
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    @classmethod
    def create_product(cls, data):
        try:
            variations = data.pop("variations")

            columns = ", ".join(data.keys())
            values = tuple(data.values())
            cls._pygres(f"INSERT INTO product_listing({columns}) VALUES {values} RETURNING id;")
            id = cls._pygres.fetch()[0][0]
            cls._pygres(f'''
                UPDATE product_listing
                SET index = to_tsvector('english', {" || ' ' || ".join([f"COALESCE({column}, '')" for column in ["id", "name", "description"]])})
                WHERE id = '{id}';
            ''')

            for variation in variations:
                tags = variation.pop("tags")

                variation['listing_id'] = id
                variation["overview"] = json.dumps(variation["overview"])

                columns = ", ".join(variation.keys())
                values = tuple(variation.values())
                cls._pygres(f"INSERT INTO product_variation({columns}) VALUES {values} RETURNING extension;")
                extension = cls._pygres.fetch()[0][0]
                cls._pygres(f'''
                    UPDATE product_variation
                    SET index = to_tsvector('english', {" || ' ' || ".join([f"COALESCE({column}, '')" for column in ["subname"]])})
                    WHERE listing_id = '{id}' AND extension = '{extension}';
                ''')

                for tag in tags:
                    cls._pygres(f'''
                        INSERT INTO product_variation__tag(listing_id, variation_extension, tag_id) 
                        VALUES {(id, variation['extension'], tag)};
                    ''')

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to create product: ", error)
            cls._error()
            return error

    @classmethod
    def update_product(cls, old_id, data):
        try:
            variations = data.pop("variations")

            cls._pygres(f'''
                UPDATE product_listing
                SET {", ".join([f"{key} = '{value}'" for key, value in data.items()])}
                WHERE id = '{old_id}' RETURNING id;
            ''')
            new_id = cls._pygres.fetch()[0][0]
            cls._pygres(f'''
                UPDATE product_listing
                SET index = to_tsvector('english', {" || ' ' || ".join([f"COALESCE({column}, '')" for column in ["id", "name", "description"]])})
                WHERE id = '{new_id}';
            ''')

            extensions = set()
            for variation in variations:
                tags = variation.pop("tags")
                extensions.add(variation["extension"])

                variation['listing_id'] = new_id
                variation["overview"] = json.dumps(variation["overview"])

                cls._pygres(f'''
                    SELECT * FROM product_variation 
                    WHERE listing_id = '{old_id}' AND extension = '{variation["extension"]}';
                ''')
                if len(cls._pygres.fetch()) > 0:
                    cls._pygres(f'''
                        UPDATE product_variation
                        SET {", ".join([f"{key} = '{value}'" for key, value in variation.items()])}
                        WHERE listing_id = '{old_id}' AND extension = '{variation["extension"]}'
                        RETURNING extension;
                    ''')
                else:
                    columns = ", ".join(variation.keys())
                    values = tuple(variation.values())
                    cls._pygres(f"INSERT INTO product_variation({columns}) VALUES {values} RETURNING extension;")

                extension =  cls._pygres.fetch()[0][0]
                cls._pygres(f'''
                    UPDATE product_variation
                    SET index = to_tsvector('english', {" || ' ' || ".join([f"COALESCE({column}, '')" for column in ["subname"]])})
                    WHERE listing_id = '{new_id}' AND extension = '{extension}';
                ''')

                for tag in tags:
                    cls._pygres(f'''
                        SELECT * FROM product_variation__tag
                        WHERE listing_id = '{old_id}' AND variation_extension = '{variation['extension']}' AND tag_id = '{tag}';
                    ''')
                    if len(cls._pygres.fetch()) == 0:
                        cls._pygres(f'''
                            INSERT INTO product_variation__tag(listing_id, variation_extension, tag_id) 
                            VALUES {(new_id, variation['extension'], tag)};
                        ''')
                cls._pygres(f'''
                    UPDATE product_variation__tag
                    SET listing_id = '{new_id}'
                    WHERE listing_id = '{old_id}';
                ''')
                cls._pygres(f'''
                    DELETE FROM product_variation__tag
                    WHERE listing_id = '{new_id}' AND variation_extension = '{extension}'
                        AND tag_id NOT IN ({", ".join([f"'{tag}'" for tag in tags])});
                ''')

            # clean up if extensions get updated
            # this wouldn't be required if rows have a unique identifier that could be used to update the row rather than accidentally inserting new data
            # but i like to make things hard i guess
            cls._pygres(f'''
                DELETE FROM product_variation
                WHERE listing_id = '{old_id}' AND NOT extension = ANY ARRAY[{", ".join([f"'{extension}'" for extension in extensions])}];
            ''')
            cls._pygres(f'''
                DELETE FROM product_variation__tag
                WHERE listing_id = '{new_id}' AND NOT variation_extension = ANY ARRAY[{", ".join([f"'{extension}'" for extension in extensions])}];
            ''')

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error

    @classmethod
    def delete_product(cls, id):
        try:
            cls._pygres(f"DELETE FROM product_listing WHERE id = '{id}';")
            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error

    # STOCK METHODS
    @classmethod
    def get_stock_list(cls):
        try:
            cls._pygres(f"SELECT listing_id, variation_extension, sale FROM instock_listing;")
            results = cls._pygres.fetch()
            return [{key: value for key, value in zip(["id", "extension", "sale"], result)} for result in results]
        except QueryError as error:
            print("Error while attempting to get stock list: ", error)
            cls._error()
            return error

    @classmethod
    def get_stock(cls, id):
        try:
            cls._pygres(f'''
                WITH items AS (
                    SELECT serial, display, overview, (
                        SELECT COALESCE(ARRAY_AGG(tag.id), '{{}}')
                        FROM tag INNER JOIN instock_item__tag ON instock_item__tag.tag_id = tag.id
                        WHERE instock_item__tag.listing_id = '{id}' AND instock_item__tag.item_serial = serial
                    ) AS tags
                    FROM instock_item WHERE listing_id = '{id}'
                )
                SELECT id, sale, price, listing_id, variation_extension, (
                    SELECT COALESCE(json_agg(json_build_object(
                        'serial',items.serial,
                        'display', items.display,
                        'overview', items.overview,
                        'tags', items.tags
                    )), '[]') FROM items
                ) AS items
                FROM instock_listing WHERE id = '{id}';
            ''')
            result = cls._pygres.fetch()
            return {key: value for key, value in zip(["id", "sale", "price", "listing_id", "variation_extension", "items"], result)}
        except QueryError as error:
            print("Error while attempting to get stock listing: ", error)
            cls._error()
            return error

    @classmethod
    def create_stock(cls, data):
        try:
            items = data.pop("items")

            columns = ", ".join(data.keys())
            values = tuple(data.values())
            cls._pygres(f"INSERT INTO instock_listing({columns}) VALUES {values} RETURNING id;")
            id = cls._pygres.fetch()[0][0]

            for item in items:
                tags = item.pop("tags")

                item['listing_id'] = id
                item["overview"] = json.dumps(item["overview"])

                columns = ', '.join(item.keys())
                values = tuple(item.values())
                cls._pygres(f"INSERT INTO instock_item({columns}) VALUES {values};")

                for tag in tags:
                    cls._pygres(f'''
                        INSERT INTO instock_item__tag(listing_id, item_serial, tag_id) 
                        VALUES {(id, item['serial'], tag)};
                    ''')

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to create instock listing: ", error)
            cls._error()
            return error

    @classmethod
    def update_stock(cls, id, data):
        try:
            items = data.pop("items")

            cls._pygres(f'''
                UPDATE instock_listing
                SET {", ".join([f"{key} = '{value}'" for key, value in data.items()])}
                WHERE id = '{id}';
            ''')

            serials = set()
            for item in items:
                tags = item.pop("tags")
                serials.add(item["serial"])

                item['listing_id'] = id
                item["overview"] = json.dumps(item["overview"])

                cls._pygres(f'''
                    SELECT * FROM instock_items
                    WHERE listing_id = '{id}' AND serial = '{item["serial"]};
                ''')
                if len(cls._pygres.fetch()) > 0:
                    cls._pygres(f'''
                        UPDATE instock_item
                        SET {", ".join([f"{key} = {value}" for key, value in item.items()])}
                        WHERE listing_id = '{item['listing_id']}' AND serial = '{item['serial']}';
                    ''')
                else:
                    columns = ", ".join(item.keys())
                    values = tuple(item.values())
                    cls._pygres(f"INSERT INTO instock_item({columns}) VALUES {values};")

                for tag in tags:
                    cls._pygres(f'''
                        SELECT * FROM instock_item__tag
                        WHERE listing_id = '{id}' AND item_serial = '{item['serial']}' AND tag_id = '{tag}';
                    ''')
                    if len(cls._pygres.fetch()) == 0:
                        cls._pygres(f'''
                            INSERT INTO instock_item__tag(listing_id, item_serial, tag_id) 
                            VALUES {(id, item['serial'], tag)};
                        ''')
                cls._pygres(f'''
                    DELETE FROM instock_item__tag
                    WHERE listing_id = '{id}' AND item_serial = '{item["serial"]}'
                        AND tag_id NOT IN ({", ".join([f"'{tag}'" for tag in tags])});
                ''')

            # clean up if extensions get updated
            # this wouldn't be required if rows have a unique identifier that could be used to update the row rather than accidentally inserting new data
            # but i like to make things hard i guess
            cls._pygres(f'''
                DELETE FROM instock_item
                WHERE listing_id = '{id}' AND serial != ANY ARRAY[{", ".join([f"'{serial}'" for serial in serials])}];
            ''')
            cls._pygres(f'''
                DELETE FROM instock_item__tag
                WHERE listing_id = '{id}' AND item_serial != ANY ARRAY[{", ".join([f"'{serial}'" for serial in serials])}];
            ''')

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to update instock listings: ", error)
            cls._error()
            return error

    @classmethod
    def delete_stock(cls, id):
        try:   
            cls._pygres(f"DELETE FROM instock_listing WHERE id = '{id}';")
            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to delete instock listings: ", error)
            cls._error()
            return error

    # SALVAGE METHODS
    @classmethod
    def get_salvage_list(cls):
        try:
            cls._pygres(f"SELECT id, name, description FROM salvage_listing;")
            results = cls._pygres.fetch()
            return [{key: value for key, value in zip(["id", "name", "description"], result)} for result in results]
        except QueryError as error:
            print("Error while attempting to get stock list: ", error)
            cls._error()
            return error

    @classmethod
    def get_salvage(cls, id):
        try:
            cls._pygres(f'''
                WITH items AS (
                    SELECT serial, price, display, overview, (
                        SELECT COALESCE(ARRAY_AGG(tag.id), '{{}}')
                        FROM tag INNER JOIN salvage_item__tag ON salvage_item__tag.tag_id = tag.id
                        WHERE salvage_item__tag.listing_id = '{id}' AND salvage_item__tag.item_serial = serial
                    ) AS tags
                    FROM salvage_item WHERE listing_id = '{id}'
                )
                SELECT id, name, description, (
                    SELECT COALESCE(json_agg(json_build_object(
                        'serial',items.serial,
                        'price', items.price,
                        'display', items.display,
                        'overview', items.overview,
                        'tags', items.tags
                    )), '[]') FROM items
                ) AS items
                FROM salvage_listing WHERE id = '{id}';
            ''')
            result = cls._pygres.fetch()[0]
            return {key: value for key, value in zip(["id", "name", "description", "items"], result)}
        except QueryError as error:
            print("Error while attempting to get stock listing: ", error)
            cls._error()
            return error

    @classmethod
    def create_salvage(cls, data):
        try:
            items = data.pop("items")

            columns = ", ".join(data.keys())
            values = tuple(data.values())
            cls._pygres(f"INSERT INTO salvage_listing({columns}) VALUES {values} RETURNING id;")
            id = cls._pygres.fetch()[0][0]
            cls._pygres(f'''
                UPDATE salvage_listing
                SET index = to_tsvector('english', {" || ' ' || ".join([f"COALESCE({column}, '')" for column in ["id", "name", "description"]])})
                WHERE id = '{id}';
            ''')

            for item in items:
                tags = item.pop("tags")

                item['listing_id'] = data['id']
                item["overview"] = json.dumps(item["overview"])
                
                columns = ", ".join(item.keys())
                values = tuple(item.values())
                cls._pygres(f"INSERT INTO salvage_item({columns}) VALUES {values};")

                for tag in tags:
                    cls._pygres(f'''
                        INSERT INTO salvage_item__tag(listing_id, item_serial, tag_id) 
                        VALUES {(data['id'], item['serial'], tag)};
                    ''')

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to create product: ", error)
            cls._error()
            return error

    @classmethod
    def update_salvage(cls, id, data):
        try:
            items = data.pop("items")

            cls._pygres(f'''
                UPDATE salvage_listing
                SET {", ".join([f"{key} = '{value}'" for key, value in data.items()])}
                WHERE id = '{id}' RETURNING id;
            ''')
            id = cls._pygres.fetch()[0][0]
            cls._pygres(f'''
                UPDATE salvage_listing
                SET index = to_tsvector('english', {" || ' ' || ".join([f"COALESCE({column}, '')" for column in ["id", "name", "description"]])})
                WHERE id = '{id}';
            ''')

            serials = set()
            for item in items:
                tags = item.pop("tags")
                serials.add(item["serial"])

                item['listing_id'] = data['id']
                item["overview"] = json.dumps(item["overview"])

                cls._pygres(f'''
                    SELECT * FROM salvage_item
                    WHERE listing_id = '{id}' AND serial = '{item["serial"]}';
                ''')
                if len(cls._pygres.fetch()) > 0:
                    cls._pygres(f'''
                        UPDATE salvage_item
                        SET {", ".join([f"{key} = '{value}'" for key, value in item.items()])}
                        WHERE listing_id = '{item['listing_id']}' AND serial = '{item['serial']}';
                    ''')
                else:
                    columns = ", ".join(item.keys())
                    values = tuple(item.values())
                    cls._pygres(f"INSERT INTO salvage_item({columns}) VALUES {values};")

                for tag in tags:
                    cls._pygres(f'''
                        SELECT * FROM salvage_item__tag
                        WHERE listing_id = '{id}' AND item_serial = '{item['serial']}' AND tag_id = '{tag}';
                    ''')
                    if len(cls._pygres.fetch()) == 0:
                        cls._pygres(f'''
                            INSERT INTO salvage_item__tag(listing_id, item_serial, tag_id) 
                            VALUES {(id, item['serial'], tag)};
                        ''')
                cls._pygres(f'''
                    DELETE FROM salvage_item__tag
                    WHERE listing_id = '{id}' AND item_serial = '{item["serial"]}'
                        AND tag_id NOT IN ({", ".join([f"'{tag}'" for tag in tags])});
                ''')

            # clean up if extensions get updated
            # this wouldn't be required if rows have a unique identifier that could be used to update the row rather than accidentally inserting new data
            # but i like to make things hard i guess
            cls._pygres(f'''
                DELETE FROM salvage_item
                WHERE listing_id = '{data["id"]}' AND serial != ANY ARRAY[{", ".join([f"'{serial}'" for serial in serials])}];
            ''')
            cls._pygres(f'''
                DELETE FROM salvage_item__tag
                WHERE listing_id = '{data["id"]}' AND item_serial != ANY ARRAY[{", ".join([f"'{serial}'" for serial in serials])}];
            ''')

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error

    @classmethod
    def delete_salvage(cls, id):
        try:
            cls._pygres(f"DELETE FROM salvage_listing WHERE id = {id};")
            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error

    # CUSTOM METHODS
    @classmethod
    def get_custom_list(cls):
        try:
            cls._pygres(f"SELECT id, listing_id, name, description FROM custom_item;")
            results = cls._pygres.fetch()
            return [{key: value for key, value in zip(["id", "listing_id", "name", "description"], result)} for result in results]
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error

    @classmethod
    def get_custom(cls, id):
        try:
            cls._pygres(f"SELECT id, listing_id, name, description, customer FROM custom_item WHERE id = {id};")
            result = cls._pygres.fetch()[0]
            return {key: value for key, value in zip(["id", "listing_id", "name", "description", "customer"], result)}
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error

    @classmethod
    def create_custom(cls, data):
        try:
            columns = ", ".join(data.keys())
            values = tuple(data.values())
            cls._pygres(f"INSERT INTO custom_item({columns}) VALUES {values} RETURNING id;")
            id = cls._pygres.fetch()[0][0]
            cls._pygres(f'''
                UPDATE custom_item
                SET index = to_tsvector('english', {" || ' ' || ".join([f"COALESCE({column}, '')" for column in ["listing_id", "name", "description", "customer"]])})
                WHERE id = '{id}';
            ''')
            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error
        

    @classmethod
    def update_custom(cls, id, data):
        try:
            cls._pygres(f'''
                UPDATE custom_item
                SET {", ".join([f"{key} = '{value}'" for key, value in data.items()])}
                WHERE id = '{id}' RETURNING id;
            ''')
            id = cls._pygres.fetch()[0][0]
            cls._pygres(f'''
                UPDATE custom_item
                SET index = to_tsvector('english', {" || ' ' || ".join([f"COALESCE({column}, '')" for column in ["listing_id", "name", "description", "customer"]])})
                WHERE id = '{id}';
            ''')
            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error

    @classmethod
    def delete_custom(cls, id):
        try:
            cls._pygres(f"DELETE FROM custom_item WHERE id = {id};")
            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error

    @classmethod
    def disconnect(cls):
        cls._pygres.close()

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
