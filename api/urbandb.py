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

class UrbanDB:
    _pygres = None

    @classmethod
    def _error(cls):
        cls._pygres.rollback()

    @classmethod
    def _complete_action(cls):
        cls._pygres.commit()

    @classmethod
    def open_pygres(cls, env_file):
        try:
            if cls._pygres is None:
                env = json.load(open(env_file, 'r'))
                cls._pygres = PygreSQL(*env.values())
        except:
            raise Exception()

    @classmethod
    def initialize_database(cls):
        cls._pygres.extend("pg_trgm")

        cls._pygres.create("product_listing", {
            "id": "VARCHAR(7)",
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
            "listing_id": "VARCHAR(7)"
        }, foreign_key = {"listing_id": "product_listing(id)"})
        cls._pygres.gin("product_variations", columns = ["subname"])

        # cls._pygres.create("instock_listing", {
        #     "id": "VARCHAR(7)",
        #     "name": "VARCHAR(255)",
        #     "description": "TEXT",
        #     "product_id": "VARCHAR(7)"
        # }, primary_key = ["id"], foreign_key = {"product_id": "product_listing(id)"})
        # cls._pygres.gin("instock_listing", columns = ["id", "name", "description"])
        # cls._pygres.create("instock_items", {
        #     "serial": "INT",
        #     "overstock": "BOOL",
        #     "price": "INT",
        #     "display": "BOOL",
        #     "overview": "JSONB",
        #     "listing_id": "VARCHAR(7)"
        # }, primary_key = ["serial"], foreign_key = {"listing_id": "instock_listing(id)"})

        # cls._pygres.create("salvage_listing", {
        #     "id": "VARCHAR(7)",
        #     "name": "VARCHAR(255)",
        #     "description": "TEXT",
        #     "price": "INT",
        #     "display": "BOOL",
        #     "overview": "JSONB"
        # }, primary_key = ["id"])
        # cls._pygres.gin("salvage_listing", columns = ["id", "name", "description"])

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
            {"name": "Distiction", "description": "Specifically for lighting used to distinguish exterior and interior."},
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
            "listing_id": "VARCHAR(7)",
            "variation_extension": "VARCHAR(10)",
            "tag_id": "INT"
        }, foreign_key = {"listing_id": "product_listing(id)", "tag_id": "tag(id)"})
        # cls._pygres.create("instock_listing__tag", {
        #     "listing_id": "VARCHAR(7)",
        #     "tag_id": "INT(10)"
        # }, foreign_key = {"listing_id": "instock_listing('id')", "tag_id": "tag('id')"})
        # cls._pygres.create("salvage_listing__tag", {
        #     "listing_id": "VARCHAR(7)",
        #     "tag_id": "INT(10)"
        # }, foreign_key = {"listing_id": "salvage_listing('id')", "tag_id": "tag('id')"})

        # cls._pygres.create("blog_post__tag", {
        #     "post_id": "INT(10)",
        #     "tag_id": "INT(10)"
        # }, foreign_key = {"post_id": "blog_post('id')", "tag_id": "tag('id')"})

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
            cls._pygres.rollback()
            return []

    @classmethod
    def get_tag(cls, id):
        return cls._pygres.select("tag", where = f"id = '{id}'")

    @classmethod
    def get_tag_categories(cls):
        return cls._pygres.select("tag_categories")

    @classmethod
    def create_tag(cls, data):
        cls._pygres.insert("tag", data)
        cls._pygres.regin("tag", columns = ["name"])

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
        except QueryError as error:
            print("Error while attempting to create product: ", error)
            cls._pygres.rollback()
            return error

    @classmethod
    def update_product(cls, id, data):
        cls._pygres.update("product_listing", data, where = f"id = '{id}'")

    @classmethod
    def update_variation(cls, id, data):
        cls._pygres.update("product_variation", data, where = f"id = '{id}'")

    @classmethod
    def delete_product(cls, id):
        cls._pygres.delete("product_listing", where = f"id = '{id}'")        

    @classmethod
    def delete_variation(cls, id):
        cls._pygres.delete("product_variation", where = f"id = '{id}'")

    @classmethod
    def close_pygres(cls):
        cls._pygres.close()

