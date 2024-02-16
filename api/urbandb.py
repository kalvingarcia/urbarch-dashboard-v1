import json
import re
from os import system
import nltk
from nltk.corpus import brown, words, wordnet, stopwords
from nltk.tokenize import word_tokenize
from nltk.metrics import edit_distance
from .pygres import PygreSQL

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
        cls._pygres.create("product_listing", {
            "id": "VARCHAR(7)",
            "name": "VARCHAR(255)",
            "description": "TEXT"
        }, primary_key = ["id"], index = ["id", "name", "description"])
        cls._pygres.create("product_variations", {
            "extension": "VARCHAR(10)",
            "subname": "VARCHAR(255)",
            "price": "INT",
            "display": "BOOL",
            "overview": "JSONB",
            "listing_id": "VARCHAR(7)"
        }, foreign_key = {"listing_id": "product_listing(id)"}, index = ["subname"])

        cls._pygres.create("instock_listing", {
            "id": "VARCHAR(7)",
            "name": "VARCHAR(255)",
            "description": "TEXT",
            "product_id": "VARCHAR(7)"
        }, primary_key = ["id"], foreign_key = {"product_id": "product_listing(id)"}, index = ["id", "name", "description"])
        cls._pygres.create("instock_items", {
            "serial": "INT",
            "overstock": "BOOL",
            "price": "INT",
            "display": "BOOL",
            "overview": "JSONB",
            "listing_id": "VARCHAR(7)"
        }, primary_key = ["serial"], foreign_key = {"listing_id": "instock_listing(id)"})

        cls._pygres.create("salvage_listing", {
            "id": "VARCHAR(7)",
            "name": "VARCHAR(255)",
            "description": "TEXT",
            "price": "INT",
            "display": "BOOL",
            "overview": "JSONB"
        }, primary_key = ["id"], index = ["id", "name", "description"])

        cls._pygres.create("tag_categories", {
            "id": "INT",
            "name": "VARCHAR(255)"
        }, primary_key = ["id"], index = ["name"])
        cls._pygres.create("tag", {
            "id": "INT",
            "name": "VARCHAR(255)",
            "category_id": "INT"
        }, primary_key = ["id"], foreign_key = {"category_id": "tag_categories(id)"}, index = ["name"])
        # cls._pygres.create("product_listing__tag", {
        #     "listing_id": "VARCHAR(7)",
        #     "tag_id": "INT(10)"
        # }, foreign_key = {"listing_id": "product_listing('id')", "tag_id": "tag('id')"})
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
        
        columns = ["*", f"ts_rank(to_tsvector('english', id || ' ' || name || ' ' || description), plainto_tsquery('english', '{search_text}')) AS rank"]
        where = f"to_tsvector('english', id || ' ' || name || ' ' || description) @@ plainto_tsquery('english', '{search_text}')"
        results = cls._pygres.select("product_listing", columns = columns, where = where, order = "rank DESC")

        columns = ["listing_id", f"ts_rank(to_tsvector('english', subname), plainto_tsquery('english', '{search_text}')) AS rank"]
        where = f"to_tsvector('english', subname) @@ plainto_tsquery('english', '{search_text}')"
        intermediate = cls._pygres.select("product_variations", columns = columns, where = where, order = "rank DESC")
        intermediate = ' OR '.join([f"id = {id}" for id in [result["listing_id"] for result in intermediate]])

        results += cls._pygres.select("product_listing", where = intermediate)

        seen = set()
        return [result for result in results if not (result["id"] in seen or seen.add(result["id"]))]

    @classmethod
    def search_tags(cls, text: str):
        try:
            search_text = cls.__expand_query(text)
            columns = ["*", f"ts_rank(to_tsvector('english', name), plainto_tsquery('english', '{search_text}')) AS rank"]
            where = f"to_tsvector('english', name) @@ plainto_tsquery('english', '{search_text}')"
            return cls._pygres.select("tag", columns = columns, where = where, order = "rank DESC")
        except:
            raise Exception()

    @classmethod
    def get_tag_list(cls):
        pass

    @classmethod
    def get_product_list(cls, filter_ids: list = None):
        return cls._pygres.select("product_listing")

    @classmethod
    def get_product(cls, id):
        result = cls._pygres.select("product_listing", where = f"id = '{id}'")[0]
        result["variations"] = cls._pygres.select("product_variations", where = f"listing_id = '{id}'")
        return result

    @classmethod
    def create_product(cls, data):
        variations = data.pop("variations")
        cls._pygres.insert("product_listing", data)
        for variation in variations:
            variation['listing_id'] = data['id']
            cls._pygres.insert("product_variations", variation)

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

