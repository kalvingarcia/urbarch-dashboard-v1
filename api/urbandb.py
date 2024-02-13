import json
from os import system
from .pygres import PygreSQL

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

        # cls._pygres.create("tag_categories", {
        #     "id": "INT(10) SERIAL",
        #     "name": "VARCHAR(255)"
        # }, primary_key = ["id"])
        # cls._pygres.create("tag", {
        #     "id": "INT(10) SERIAL",
        #     "name": "VARCHAR(255)",
        #     "category_id": "INT(10)"
        # }, primary_key = ["id"], foreign_key = {"category_id": "tag_categories('id')"})
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

