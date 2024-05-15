import json
import re
from os import system
import nltk
from nltk.corpus import brown, words, wordnet, stopwords
from nltk.tokenize import word_tokenize
from nltk.metrics import edit_distance
from .pygres import PygreSQL, FetchError, QueryError, CommitError, RollbackError, ConnectionError

word_list = set(words.words() + brown.words())
pattern = re.compile(r"^\*.+\*$")

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
        cls._pygres.extend("pg_trgm")

        # Product Related Tables
        cls._pygres.create("finishes", {
            "id": "VARCHAR(5)",
            "name": "VARCHAR(255)",
            "outdoor": "BOOL"
        })
        finishes = [
            {"id": "PB", "name": "Polished Brass", "outdoor": "YES"},
            {"id": "PN", "name": "Polished Nickel", "outdoor": "YES"},
            {"id": "GP", "name": "Green Patina", "outdoor": "YES"},
            {"id": "BP", "name": "Brown Patina", "outdoor": "YES"},
            {"id": "AB", "name": "Antique Brass", "outdoor": "YES"},
            {"id": "SN", "name": "Satin Nickel", "outdoor": "YES"},
            {"id": "LP", "name": "Light Pewter", "outdoor": "YES"},
            {"id": "STBR", "name": "Statuary Brown", "outdoor": "NO"},
            {"id": "STBL", "name": "Statuary Black", "outdoor": "NO"},
            {"id": "PC", "name": "Polished Chrome", "outdoor": "YES"},
            {"id": "BN", "name": "Black Nickel", "outdoor": "YES"}
        ]
        for finish in finishes:
            cls._pygres.insert("finishes", finish)

        cls._pygres.create("product_listing", {
            "id": "VARCHAR(10)",
            "name": "VARCHAR(255)",
            "description": "TEXT"
        }, primary_key = ["id"])
        cls._pygres.gin("product_listing", columns = ["id", "name", "description"])
        cls._pygres.create("product_variations", {
            "extension": "VARCHAR(10)",
            "subname": "VARCHAR(255)",
            "price": "INT",
            "display": "BOOL",
            "overview": "JSONB",
            "listing_id": "VARCHAR(10)"
        }, foreign_key = {"listing_id": "product_listing(id)"})
        cls._pygres.gin("product_variations", columns = ["subname"])

        cls._pygres.create("instock_listing", {
            "id": "SERIAL",
            "sale": "BOOL",
            "price": "INT",
            "product_id": "VARCHAR(7)",
            "variation_extension": "VARCHAR(10)"
        }, primary_key = ["id"], foreign_key = {"product_id": "product_listing(id)"})
        cls._pygres.create("instock_items", {
            "serial": "INT",
            "display": "BOOL",
            "overview": "JSONB",
            "listing_id": "INT"
        }, foreign_key = {"listing_id": "instock_listing(id)"})

        cls._pygres.create("salvage_listing", {
            "id": "VARCHAR(10)",
            "name": "VARCHAR(255)",
            "description": "TEXT",
        }, primary_key = ["id"])
        cls._pygres.gin("salvage_listing", columns = ["id", "name", "description"])
        cls._pygres.create("salvage_items", {
            "serial": "INT",
            "price": "INT",
            "display": "BOOL",
            "overview": "JSONB",
            "listing_id": "VARCHAR(10)"
        }, foreign_key = {"listing_id": "salvage_listing(id)"})

        # Gallery Related Tables
        cls._pygres.create("custom_items", {
            "id": "SERIAL",
            "name": "VARCHAR(255)",
            "description": "TEXT",
            "customer": "VARCHAR(255)",
            "display": "BOOL",
            "product_id": "VARCHAR(10)",
            "variation_extension": "VARCHAR(10)"
        }, primary_key = ["id"], foreign_key = {"product_id": "product_listing(id)"})
        cls._pygres.gin("custom_items", columns = ["name", "description", "customer", "product_id"])

        # Tag Related Tables
        cls._pygres.create("tag_categories", {
            "id": "SERIAL",
            "name": "VARCHAR(255)",
            "description": "TEXT"
        }, primary_key = ["id"])
        categories = [
            {"name": "Class", "description": "Whether the item is a(n) Lighting, Bathroom, Washstands, Furnishing, Mirrors, Cabinets, Display, Hardware, Tile"},
            {"name": "Category", "description": "The order of the classification, such as sconce, hanging, flushmount, etc."},
            {"name": "Style", "description": "The artistic period that the item is from."},
            {"name": "Family", "description": "The stuctural grouping of the item, such as \"torch\" for Loft Light, Urban Torch, etc."},
            {"name": "Designer", "description": "The name of the designer who created the piece."},
            {"name": "Material", "description": "The type of materials used to create the item, such as alabaster, marble, aluminum, brass, etc."},
            {"name": "Distinction", "description": "Specifically for lighting used to distinguish exterior and interior."},
            {"name": "Environmental", "description": "Specifies any environmental conditions the item can be used in, such as waterproof."}
        ]
        for category in categories:
            cls._pygres.insert("tag_categories", category)

        cls._pygres.create("tag", {
            "id": "SERIAL",
            "name": "VARCHAR(255)",
            "category_id": "INT"
        }, primary_key = ["id"], foreign_key = {"category_id": "tag_categories(id)"})
        cls._pygres.gin("tag", columns = ["name"])

        cls._pygres.create("product_variation__tag", {
            "listing_id": "VARCHAR(10)",
            "variation_extension": "VARCHAR(10)",
            "tag_id": "INT"
        }, foreign_key = {"listing_id": "product_listing(id)", "tag_id": "tag(id)"})
        cls._pygres.create("instock_listing__tag", {
            "listing_id": "INT",
            "item_serial": "INT",
            "tag_id": "INT",
        }, foreign_key = {"listing_id": "instock_listing(id)", "tag_id": "tag(id)"})
        cls._pygres.create("salvage_listing__tag", {
            "listing_id": "VARCHAR(10)",
            "item_serial": "INT",
            "tag_id": "INT"
        }, foreign_key = {"listing_id": "salvage_listing(id)", "tag_id": "tag(id)"})
        cls._pygres.create("custom_items__tag", {
            "item_id": "INT",
            "tag_id": "INT"
        }, foreign_key = {"item_id": "custom_items(id)", "tag_id": "tag(id)"})

        cls._complete_action()

    @classmethod
    def __expand_query(cls, query):
        def autocorrect(word):
            if pattern.search(word) is not None or word.lower() in word_list:
                return word
            return min(word_list, key = lambda x: edit_distance(x, word.lower()))

        def preprocess(query):
            words = word_tokenize(' '.join([autocorrect(word) for word in query.split()]))

            stop_words = set(stopwords.words("english"))
            words = [word for word in words if word.lower() not in stop_words]

            return ' '.join(words)

        def expand(query):
            expanded_query = []
            for word in query.split():
                word_synonyms = set([synonym.name().replace('_', ' ').split('.')[0] for synonym in wordnet.synsets(word)])
                word_synonyms.add(word)
                expanded_query.append("(" + " | ".join(word_synonyms) + ")")
            
            return " & ".join(expanded_query)

        return expand(preprocess(query))

    @classmethod
    def search_products(cls, text: str):
        search_text = text # cls.__expand_query(text)
        
        columns = ["*", f"ts_rank(index, plainto_tsquery('english', '{search_text}')) AS rank"]
        where = f"index @@ plainto_tsquery('english', '{search_text}')"
        results = cls._pygres.select("product_listing", columns = columns, where = where, order = "rank DESC")

        columns = ["listing_id", f"ts_rank(index, plainto_tsquery('english', '{search_text}')) AS rank"]
        where = f"index @@ plainto_tsquery('english', '{search_text}')"
        intermediate = cls._pygres.select("product_variations", columns = columns, where = where, order = "rank DESC")
        intermediate = ' OR '.join([f"id = {id}" for id in [result["listing_id"] for result in intermediate]])

        results += cls._pygres.select("product_listing", where = intermediate)

        seen = set()
        return [result for result in results if not (result["id"] in seen or seen.add(result["id"]))]

    @classmethod
    def search_tags(cls, text: str):
        try:
            if text == '':
                return cls._pygres.select("tag")
            search_text = text # cls.__expand_query(text)
            columns = ["*", f"ts_rank(index, plainto_tsquery('english', '{search_text}')) AS rank"]
            where = f"index @@ plainto_tsquery('english', '{search_text}')"
            return cls._pygres.select("tag", columns = columns, where = where, order = "rank DESC")
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    @classmethod
    def search_components(cls, text: str):
        try:
            component_tag_id = cls._pygres.select("tag", where = f"name = 'Replacement'")[0]["id"]
            if text == "":
                variations_by_tag = cls._pygres.select("product_variation__tag", where = f"tag_id = {component_tag_id}")
                where = " OR ".join([f"id = '{variation["listing_id"]}'" for variation in variations_by_tag])
                return cls._pygres.select("product_listing", where = where)
            
            return []
        except QueryError as error:
            print("Error while attempting to search database: " + str(error))
            cls._error()
            return []

    @classmethod
    def get_metal_finishes_list(cls):
        return cls._pygres.select("finishes")

    @classmethod
    def get_tag_categories(cls):
        return cls._pygres.select("tag_categories")

    # TAG METHODS
    @classmethod
    def get_tag_list(cls):
        return cls._pygres.select("tag")

    @classmethod
    def get_tag(cls, id):
        return cls._pygres.select("tag", where = f"id = '{id}'")[0]

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
    def get_product_list(cls, filter_ids: list = None):
        return cls._pygres.select("product_listing")

    @classmethod
    def get_product(cls, id):
        result = cls._pygres.select("product_listing", where = f"id = '{id}'")[0]
        result["variations"] = cls._pygres.select("product_variations", where = f"listing_id = '{id}'")
        for variation in result["variations"]:
            variation["tags"] = [product_tag["tag_id"] for product_tag in cls._pygres.select(
                "product_variation__tag",
                columns = ["tag_id"],
                distinct = True,
                where = f"listing_id = '{id}' AND variation_extension = '{variation["extension"]}'"
            )]

        return result

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
