# ===========================================================================
#                            Setup Database
# ===========================================================================
# Sets up the MongoDB database by creating empty collections. Strictly
# speaking, creating the collections beforehand is not necessary because
# they will be created automatically when the first document is inserted.
# Nonetheless, some queries and checks would fail and is seems just like
# a save way to do it.

from time import perf_counter
import pymongo as pm
import click
from utils.database import *

# ================================= MAIN ================================

# fmt: off
@click.command()
def main():
# fmt: on

    timer_start = perf_counter()

    # Connect to database
    _, db = getConnection(use_dotenv=True)

    # ------------------- Collections -------------------

    # Create collections if not existing
    collections = db.list_collection_names()

    collections_new = ["articles"]

    for collection in collections_new:
        if collection not in collections:
            db.create_collection(collection)

    # ------------------- Indexes -------------------

    db.articles.create_index('batch_id', name='index_articles_batch_id')
    db.articles.create_index('media_name', name='index_articles_media_name')
    db.articles.create_index([("status", pm.TEXT)],
                             name='index_articles_status')

    # List all collections
    print("Collections in DB:", db.list_collection_names())

    # Print runtime
    timer_stop = perf_counter()
    print("Runtime:", round(timer_stop - timer_start, 4), "s")


if __name__ == "__main__":
    main()
