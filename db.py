import os
from pymongo import MongoClient, ASCENDING

_client = None
_collection = None


def get_courses_collection():
    global _client, _collection
    if _collection is not None:
        return _collection

    mongo_uri = os.environ["MONGO_URI"]
    _client = MongoClient(mongo_uri)
    db = _client.get_default_database() or _client["cursos"]
    _collection = db["courses"]
    _collection.create_index([("codigo", ASCENDING)], unique=True)
    return _collection
