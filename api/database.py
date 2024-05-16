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
                cls._pygres = PygreSQL(*env.values())
        except:
            raise Exception()

    @classmethod
    def reset(cls):
        for table in ["finishes", "product_listing", "product_variations", "instock_listing", "instock_items", "salvage_listing", "salvage_items",
            "custom_items",
            "tag_categories", "tag", "product_variation__tag", "instock_listing__tag", "salvage_listing__tag", "custom_items__tag"]:
            cls._pygres.drop(table, cascade = True)

    @classmethod
    def initialize(cls):
        cls._pygres("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

        # Product Related Tables
        cls._pygres.create('''
            CREATE TABLE IF NOT EXISTS finishes(
                id VARCHAR(5),
                name VARCHAR(255),
                outdoor BOOL
            );
        ''')
        cls._pygres(f'''
            INSERT INTO finishes(id, name, outdoor)
            VALUES {", ".join([
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
            ])};
        ''')

        cls._pygres('''
            CREATE TABLE IF NOT EXISTS product_listing(
                id VARCHAR(10) PRIMARY KEY,
                name VARCHAR(255),
                description TEXT
            );
        ''')
        cls._pygres("ALTER TABLE IF EXISTS product_listing ADD COLUMN IF NOT EXISTS index tsvector;")
        cls._pygres(f'''
            UPDATE product_listing SET index = to_tsvector('english', {" || ' ' || ".join([f"coalesce({column}, '')" for column in ["id", "name", "description"]])});
        ''')
        cls._pygres("CREATE INDEX IF NOT EXISTS product_listing_index ON product_listing USING GIN(index);")

        cls._pygres('''
            CREATE TABLE IF NOT EXISTS product_variation(
                extension VARCHAR(10),
                subname VARCHAR(255),
                price INT,
                display BOOL,
                overview JSONB,
                listing_id VARCHAR(10) REFERENCES product_listing(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        cls._pygres("ALTER TABLE IF EXISTS product_variation ADD COLUMN IF NOT EXISTS index tsvector;")
        cls._pygres(f'''
            UPDATE product_variation SET index = to_tsvector('english', {" || ' ' || ".join([f"coalesce({column}, '')" for column in ["subname"]])});
        ''')
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
        cls._pygres(f'''
            UPDATE salvage_listing SET index = to_tsvector('english', {" || ' ' || ".join([f"coalesce({column}, '')" for column in ["id", "name", "description"]])});
        ''')
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
                listing_id VARCHAR(10) REFERENCES product_listing(id) ON DELETE CASCADE ON UPDATE CASCADE,
                variation_extension VARCHAR(10)
            );
        ''')
        cls._pygres("ALTER TABLE IF EXISTS custom_item ADD COLUMN IF NOT EXISTS index tsvector;")
        cls._pygres(f'''
            UPDATE custom_item SET index = to_tsvector('english', {" || ' ' || ".join([f"coalesce({column}, '')" for column in ["name", "description", "customer", "product_id"]])});
        ''')
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
            VALUES {", ".join([
                ("Class", "Whether the item is a(n) Lighting, Bathroom, Washstands, Furnishing, Mirrors, Cabinets, Display, Hardware, Tile"),
                ("Category", "The order of the classification, such as sconce, hanging, flushmount, etc."),
                ("Style", "The artistic period that the item is from."),
                ("Family", "The stuctural grouping of the item, such as \"torch\" for Loft Light, Urban Torch, etc."),
                ("Designer", "The name of the designer who created the piece."),
                ("Material", "The type of materials used to create the item, such as alabaster, marble, aluminum, brass, etc."),
                ("Distinction", "Specifically for lighting used to distinguish exterior and interior."),
                ("Environmental", "Specifies any environmental conditions the item can be used in, such as waterproof.")
            ])};
        ''')

        cls._pygres('''
            CREATE TABLE IF NOT EXISTS tag(
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                category_id INT REFERENCES tag_category(id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        cls._pygres("ALTER TABLE IF EXISTS tag ADD COLUMN IF NOT EXISTS index tsvector;")
        cls._pygres(f'''
            UPDATE tag SET index = to_tsvector('english', {" || ' ' || ".join([f"coalesce({column}, '')" for column in ["name"]])});
        ''')
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

        # REGIN f'''
        #   UPDATE {}} 
        #   SET index = to_tsvector('english', {" || ' ' || ".join([f"coalesce({column}, '')" for column in []])})
        #   WHERE id = {};
        # '''

    @classmethod
    def get_metal_finishes_list(cls):
        return []

    @classmethod
    def get_tag_category_list(cls):
        return []

    # TAG METHODS
    @classmethod
    def get_tag_list(cls):
        return []

    @classmethod
    def get_tag(cls, id):
        return []

    @classmethod
    def create_tag(cls, data):
        cls._pygres.insert("tag", data)
        cls._pygres.regin("tag", columns = ["name"])
        cls._complete_action()

    @classmethod
    def update_tag(cls, id, data):
        cls._pygres.update("tag", data, where = f"id = '{id}'")
        cls._pygres.regin("tag", columns = ["name"])
        cls._complete_action()

    @classmethod
    def delete_tag(cls, id):
        cls._pygres.delete("tag", where = f"id = '{id}'")
        cls._complete_action()

    # PRODUCT METHODS
    @classmethod
    def get_product_list(cls, search: str = "", filters: dict = {}):
        try:
            cls._pygres(f'''
                {
                    f'''
                        WITH search_filtered AS (
                            SELECT DISTINCT product_variation.listing_id AS id, product_variation.extension AS extension
                            FROM product_listing INNER JOIN product_variation ON product_variation.listing_id = product_listing.id
                            WHERE product_listing.index @@ to_tsquery({search + ':*'}) OR product_variation.index @@ to_tsquery({search + ':*'})
                        ),
                    ''' if search != "" 
                    else ""
                }
                {
                    f'''
                        {"WITH" if search == "" else ""} tag_filtered AS (
                            {" INTERSECT ".join([
                                f'''
                                    SELECT DISTINCT product_variation__tag.listing_id AS id, product_variation__tag.variation_extension AS extension
                                    FROM product_variation__tag
                                    WHERE tag_id = ANY ARRAY[{", ".join([f"'{id}'" for id in ids])}]
                                ''' for ids in filters.values()
                            ])}
                        ),
                    '''
                }
                {"WITH" if search == "" and len(filters) == 0 else ""} categories AS (
                    /* Create a table with the tag name and listing id */
                    SELECT DISTINCT listing_id AS id, tag.name AS category
                    FROM tag INNER JOIN tag_category ON tag.category_id = tag_category.id  /* First we combine the tag and tag category information */
                        INNER JOIN product_variation__tag ON product_variation__tag.tag_id = tag.id /* Then we combine the tags specific to the variations we have */
                    WHERE tag_category.name = 'Class'
                ), results AS (
                    SELECT id, extension, name, subname, category, price, featured
                    FROM product_listing INNER JOIN product_variation ON product_listing.id = product_variation.listing_id
                        INNER JOIN categories USING(id)
                        {"INNER JOIN search_filtered USING(id, extension)" if search != "" else ""}
                        {"INNER JOIN tag_filtered USING(id, extension)" if len(filters) != 0 else ""}
                    WHERE display = TRUE
                )
                SELECT DISTINCT id, name, category
                FROM results;
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
                    SELECT extension, subname, price, overview, (
                        SELECT json_agg(json_build_object(
                            'id', tag.id,
                            'name', tag.name,
                            'category_id', tag_category.name,
                            'listing_id', product_variation__tag.listing_id
                        )) FROM tag INNER JOIN tag_category ON tag.category_id = tag_category.id
                            INNER JOIN product_variation__tag ON product_variation__tag.tag_id = tag.id
                        WHERE product_variation__tag.listing_id = '0' AND product_variation__tag.variation_extension = extension
                    ) AS tags, (
                        SELECT json_agg(json_build_object(
                            'id', product_listing.id,
                            'extension', product_variation.extension,
                            'name', product_listing.name,
                            'subname', product_variation.subname,
                            'price', product_variation.price
                        )) FROM product_listing INNER JOIN product_variation ON product_listing.id = product_variation.listing_id
                        WHERE (product_listing.id, product_variation.extension) IN (
                            SELECT id, extension
                            FROM json_populate_recordset('{{"id": TEXT, "extension": TEXT}}', overview->'replacement_ids')
                        )
                    ) AS replacements
                    FROM product_variations WHERE listing_id = '{id}' AND display = TRUE
                )
                SELECT id, name, description, (
                    SELECT json_agg(json_build_object(
                        'extension', extension,
                        'subname', subname,
                        'price', price,
                        'overview', overview,
                        'tags', tags
                    )) FROM variations
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

            cls._pygres.insert("product_listing", data)
            cls._pygres.regin("product_listing", columns = ["id", "name", "description"])

            for variation in variations:
                tags = variation.pop("tags")

                variation['listing_id'] = data['id']
                variation["overview"] = json.dumps(variation["overview"])
                cls._pygres.insert("product_variations", variation)
                cls._pygres.regin("product_variations", columns = ["subname"])

                for tag in tags:
                    cls._pygres.insert("product_variation__tag", {
                        "listing_id": data['id'],
                        "variation_extension": variation['extension'],
                        "tag_id": tag
                    })

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to create product: ", error)
            cls._error()
            return error

    @classmethod
    def update_product(cls, id, data):
        try:
            variations = data.pop("variations")

            cls._pygres.update("product_listing", data, where = f"id = '{id}'")
            cls._pygres.regin("product_listing", columns = ["id", "name", "description"])

            extensions = set()
            for variation in variations:
                tags = variation.pop("tags")
                extensions.add(variation["extension"])

                variation['listing_id'] = data['id']
                variation["overview"] = json.dumps(variation["overview"])

                where = f"listing_id = '{data["id"]}' AND extension = '{variation["extension"]}'"
                if len(cls._pygres.select("product_variations", where = where)) == 0:
                    cls._pygres.insert("product_variations", variation)
                else:
                    cls._pygres.update("product_variations", variation, where = where)

                cls._pygres.regin("product_variations", columns = ["subname"])

                for tag in tags:
                    where = f"listing_id = '{data['id']}' AND variation_extension = '{variation['extension']}' AND tag_id = '{tag}'"
                    if len(cls._pygres.select("product_variation__tag", where = where)) == 0:
                        cls._pygres.insert("product_variation__tag", {
                            "listing_id": data['id'],
                            "variation_extension": variation['extension'],
                            "tag_id": tag
                        })

            # clean up if extensions get updated
            # this wouldn't be required if rows have a unique identifier that could be used to update the row rather than accidentally inserting new data
            # but i like to make things hard i guess
            for variation in cls._pygres.select("product_variations", where = f"listing_id = '{data["id"]}'"):
                if variation["extension"] not in extensions:
                    cls._pygres.delete("product_variations", where = f"listing_id = '{variation["listing_id"]}' AND extension = '{variation["extension"]}'")
            for tag in cls._pygres.select("product_variation__tag", where = f"listing_id = '{data["id"]}'"):
                if tag["variation_extension"] not in extensions:
                    cls._pygres.delete("product_variation__tag", where = f"listing_id = '{tag["listing_id"]}' AND variation_extension = '{tag["variation_extension"]}' AND tag_id = '{tag["tag_id"]}'")

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error

    @classmethod
    def delete_product(cls, id):
        cls._pygres.delete("product_listing", where = f"id = '{id}'")
        cls._complete_action()

    # STOCK METHODS
    @classmethod
    def get_stock_list(cls):
        return cls._pygres.select("instock_listing")

    @classmethod
    def get_stock(cls, id):
        result = cls._pygres.select("instock_listing", where = f"id = '{id}'")[0]
        result["items"] = cls._pygres.select("instock_items", where = f"listing_id = '{id}'")
        for item in result["items"]:
            item["tags"] = [stock_tag["tag_id"] for stock_tag in cls._pygres.select(
                "instock_listing__tag",
                columns = ["tag_id"],
                distinct = True,
                where = f"listing_id = '{id}' AND item_serial = '{item["serial"]}'"
            )]
        return result

    @classmethod
    def create_stock(cls, data):
        try:
            items = data.pop("items")

            cls._pygres.insert("instock_listing", data)

            for item in items:
                tags = item.pop("tags")

                item['listing_id'] = data['id']
                item["overview"] = json.dumps(item["overview"])
                cls._pygres.insert("instock_items", item)

                for tag in tags:
                    cls._pygres.insert("instock_listing__tag", {
                        "listing_id": data['id'],
                        "item_serial": item['serial'],
                        "tag_id": tag
                    })

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to create product: ", error)
            cls._error()
            return error

    @classmethod
    def update_stock(cls, id, data):
        try:
            items = data.pop("items")

            cls._pygres.update("instock_listing", data, where = f"id = '{id}'")

            serials = set()
            for item in items:
                tags = item.pop("tags")
                serials.add(item["serial"])

                item['listing_id'] = data['id']
                item["overview"] = json.dumps(item["overview"])

                where = f"listing_id = '{data["id"]}' AND serial = '{item["serial"]}'"
                if len(cls._pygres.select("instock_items", where = where)) == 0:
                    cls._pygres.insert("instock_items", item)
                else:
                    cls._pygres.update("instock_items", item, where = where)

                for tag in tags:
                    where = f"listing_id = '{data['id']}' AND item_serial = '{item['serial']}' AND tag_id = '{tag}'"
                    if len(cls._pygres.select("instock_listing__tag", where = where)) == 0:
                        cls._pygres.insert("instock_listing__tag", {
                            "listing_id": data['id'],
                            "item_serial": item['serial'],
                            "tag_id": tag
                        })

            # clean up if extensions get updated
            # this wouldn't be required if rows have a unique identifier that could be used to update the row rather than accidentally inserting new data
            # but i like to make things hard i guess
            for item in cls._pygres.select("instock_items", where = f"listing_id = '{data["id"]}'"):
                if item["serial"] not in serials:
                    cls._pygres.delete("instock_items", where = f"listing_id = '{item["listing_id"]}' AND extension = '{item["extension"]}'")
            for tag in cls._pygres.select("instock_listing__tag", where = f"listing_id = '{data["id"]}'"):
                if tag["item_serial"] not in serials:
                    cls._pygres.delete("instock_listing__tag", where = f"listing_id = '{tag["listing_id"]}' AND item_serial = '{tag["item_serial"]}' AND tag_id = '{tag["tag_id"]}'")

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error

    @classmethod
    def delete_stock(cls, id):
        cls._pygres.delete("instock_listing", where = f"id = '{id}'")
        cls._complete_action()

    # SALVAGE METHODS
    @classmethod
    def get_salvage_list(cls):
        return cls._pygres.select("salvage_listing")

    @classmethod
    def get_salvage(cls, id):
        result = cls._pygres.select("salvage_listing", where = f"id = '{id}'")[0]
        result["items"] = cls._pygres.select("salvage_items", where = f"listing_id = '{id}'")
        for item in result["items"]:
            item["tags"] = [stock_tag["tag_id"] for stock_tag in cls._pygres.select(
                "salvage_listing__tag",
                columns = ["tag_id"],
                distinct = True,
                where = f"listing_id = '{id}' AND item_serial = '{item["serial"]}'"
            )]
        return result

    @classmethod
    def create_salvage(cls, data):
        try:
            items = data.pop("items")

            cls._pygres.insert("salvage_listing", data)
            cls._pygres.regin("salvage_listing", columns = ["id", "name", "description"])

            for item in items:
                tags = item.pop("tags")

                item['listing_id'] = data['id']
                item["overview"] = json.dumps(item["overview"])
                cls._pygres.insert("salvage_items", item)

                for tag in tags:
                    cls._pygres.insert("salvage_listing__tag", {
                        "listing_id": data['id'],
                        "item_serial": item['serial'],
                        "tag_id": tag
                    })

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to create product: ", error)
            cls._error()
            return error

    @classmethod
    def update_salvage(cls, id, data):
        try:
            items = data.pop("item")

            cls._pygres.update("salvage_listing", data, where = f"id = '{id}'")
            cls._pygres.regin("salvage_listing", columns = ["id", "name", "description"])

            serials = set()
            for item in items:
                tags = item.pop("tags")
                serials.add(item["serial"])

                item['listing_id'] = data['id']
                item["overview"] = json.dumps(item["overview"])

                where = f"listing_id = '{data["id"]}' AND serial = '{item["serial"]}'"
                if len(cls._pygres.select("salvage_items", where = where)) == 0:
                    cls._pygres.insert("salvage_items", item)
                else:
                    cls._pygres.update("salvage_items", item, where = where)

                for tag in tags:
                    where = f"listing_id = '{data['id']}' AND item_serial = '{item['serial']}' AND tag_id = '{tag}'"
                    if len(cls._pygres.select("salvage_items__tag", where = where)) == 0:
                        cls._pygres.insert("salvage_items__tag", {
                            "listing_id": data['id'],
                            "item_serial": item['serial'],
                            "tag_id": tag
                        })

            # clean up if extensions get updated
            # this wouldn't be required if rows have a unique identifier that could be used to update the row rather than accidentally inserting new data
            # but i like to make things hard i guess
            for item in cls._pygres.select("salvage_items", where = f"listing_id = '{data["id"]}'"):
                if item["serial"] not in serials:
                    cls._pygres.delete("salvage_items", where = f"listing_id = '{item["listing_id"]}' AND extension = '{item["extension"]}'")
            for tag in cls._pygres.select("salvage_items__tag", where = f"listing_id = '{data["id"]}'"):
                if tag["item_serial"] not in serials:
                    cls._pygres.delete("salvage_items__tag", where = f"listing_id = '{tag["listing_id"]}' AND item_serial = '{tag["item_serial"]}' AND tag_id = '{tag["tag_id"]}'")

            cls._complete_action()
        except QueryError as error:
            print("Error while attempting to update product: ", error)
            cls._error()
            return error

    @classmethod
    def delete_salvage(cls, id):
        cls._pygres.delete("salvage_listing", where = f"id = '{id}'")
        cls._complete_action()

    # CUSTOM METHODS
    @classmethod
    def get_custom_list(cls):
        return cls.__pygres.select("custom_items")

    @classmethod
    def get_custom(cls, id):
        return cls._pygres.select("custom_items", where = f"id = '{id}'")[0]

    @classmethod
    def create_custom(cls, data):
        cls._pygres.insert("custom_items", data)
        cls._pygres.regin("custom_items", columns = ["name", "description", "customer", "product_id"])
        cls._complete_action()

    @classmethod
    def update_custom(cls, id, data):
        cls._pygres.update("custom_items", data, where = f"id = '{id}'")
        cls._pygres.regin("custom_items", columns = ["name", "description", "customer", "product_id"])
        cls._complete_action()

    @classmethod
    def delete_custom(cls, id):
        cls._pygres.delete("custom_items", where = f"id = '{id}'")
        cls._complete_action()

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
