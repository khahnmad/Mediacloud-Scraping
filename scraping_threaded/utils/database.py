# ===========================================================================
#                            Database Operation Helpers
# ===========================================================================

from typing import List
from dotenv import load_dotenv
from bson import ObjectId
import pymongo as pm
import gridfs
import os

# --------------------------------- Connection --------------------------------


def getConnection(
    connection_string: str = "", database_name: str = "", use_dotenv: bool = False
):
    "Returns MongoDB and GridFS connection"

    # Load config from config file
    if use_dotenv:
        load_dotenv()
        connection_string = os.getenv("CONNECTION_STRING")
        database_name = os.getenv("DATABASE_NAME")

    # Use connection string
    conn = pm.MongoClient(connection_string)
    db = conn[database_name]
    fs = gridfs.GridFS(db)

    return fs, db

# --------------------------------- Batch --------------------------------


def getLatestBatchID(db) -> int:
    "Returns the highest existing batch ID"
    result = db.articles.find_one(sort=[("batch_id", pm.DESCENDING)])
    latest_batch = result.get("batch_id", 0) if result is not None else 0
    return latest_batch


def getFirstBatchID(db) -> int:
    "Returns the lowest existing batch ID with unprocessed pages"

    result = db.articles.find_one(
        filter={"status": "UNPROCESSED"}, sort=[("batch_id", pm.ASCENDING)]
    )
    batch_id = result.get("batch_id", 0) if result is not None else 0
    return batch_id


def deleteBatch(db, batch_id: int):
    """Deletes all documents of a batch"""
    db.articles.delete_many({"batch_id": batch_id})

# --------------------------------- Documents --------------------------------


def fetchTasks(
    db,
    batch_id: int,
    status: str,
    limit: int = 0,
    fields: dict = {},
):
    """Returns a batch of scraping tasks"""

    # Add status code to fields
    fields["status_code"] = 1
    query = {"$and": []}

    if batch_id and status:
        query["$and"] = [{"status": status}, {"batch_id": batch_id}]
    elif status:
        # Consider all batches if no batch ID specified
        query["$and"] = [{"status": status}]
    elif batch_id:
        # Consider all batches if no batch ID specified
        query["$and"] = [{"batch_id": batch_id}]

    # Sorting requires a lot of memory
    tasks = db.articles.find(query, fields).limit(limit)

    return list(tasks)

# --------------------------------- Files --------------------------------


def getPageContent(fs: gridfs, id: str, encoding="UTF-8"):
    """Retrieves a file from GridFS"""
    f = fs.get(ObjectId(id))
    return f.read().decode(encoding)


def getPageContentInfo(db, id: str):
    """Retrieves a file from GridFS"""
    info = db.fs.files.find_one({"_id": ObjectId(id)})
    return dict(info)


def savePageContent(fs, content, encoding="UTF-8", attr={}):
    """Saves a file in GridFS"""
    if content and len(content) > 0:
        if type(content) == str:
            content = content.encode(encoding)
        file_id = fs.put(content, **attr)
        return file_id
    # else:
    #    raise ValueError("File must not be emtpy")
    return None


# def updateTask(db, id: str, values: dict = {}):
#     "Updates scraping task in database"

#     filter = {"_id": ObjectId(id)}
#     values = {
#         "$set": {**values},
#         "$inc": {"tries": 1},
#     }
#     r = db.articles.update_one(filter, values)
#     return r

def updateTask(db, id: str, values: dict = {}, result={}):
    "Updates scraping task in database"

    filter = {"_id": ObjectId(id)}
    values = {
        "$set": {**values, "scraping_result": {**result}} if result else {**values},
        "$inc": {"tries": 1},
    }
    r = db.articles.update_one(filter, values)
    return r

# --------------------------------- Statistics --------------------------------


def countProcessingStatus(db):
    """Returns list of processing status and corresponding document count"""
    group = {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    sort = {"$sort": {"count": -1}}
    query = [group, sort]
    results = db.articles.aggregate(query)
    return list(results)


def countStatusCodes(db):
    """Returns list of http status codes and corresponding document count"""
    group = {"$group": {"_id": "$scraping_result.status_code", "count": {"$sum": 1}}}
    sort = {"$sort": {"count": -1}}
    query = [group, sort]
    results = db.articles.aggregate(query)
    return list(results)
