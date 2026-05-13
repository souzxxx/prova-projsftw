import os
from pymongo import MongoClient, ASCENDING

_client = None
_collection = None


def get_courses_collection():
    global _client, _collection
    if _collection is not None:
        return _collection

    mongo_uri = os.environ["MONGO_URI"]
    db_name = os.environ.get("MONGO_DB", "cursos")
    _client = MongoClient(mongo_uri)
    _collection = _client[db_name]["courses"]
    _collection.create_index([("codigo", ASCENDING)], unique=True)
    return _collection
