# ===========================================================================
#                            Fetch Article Content
# ===========================================================================
# Use this script fo scrape the content of the articles

from scraper.default import DefaultScraper, CappedException
from schemas import Status, ScrapingResult
from bson.objectid import ObjectId
from time import perf_counter
from threading import Thread
from utils.database import *
import logging
import click
import time
import math
import sys
import random
import re


# ---------------------------------------------------------------------------
#                            HELPERS
# ---------------------------------------------------------------------------


def chunks(l, n):
    """Yield n number of striped chunks from l."""
    for i in range(0, n):
        yield l[i::n]


def chunkify(input_list, n):
    # Create a dictionary to group entries by media_url
    grouped_entries = {}
    for entry in input_list:
        media_url = entry.get("media_url")
        if media_url:
            grouped_entries.setdefault(media_url, []).append(entry)

    # Split the grouped entries into roughly evenly sized blocks
    blocks = [[] for _ in range(n)]
    for media_entries in grouped_entries.values():
        smallest_block = min(blocks, key=len)
        smallest_block.extend(media_entries)

    return blocks

# ---------------------------------------------------------------------------
#                            MULTIPROCESSING
# ---------------------------------------------------------------------------


def processTasks(id, tasks, logger, db, fs, timeout):
    """Process a list of tasks in a seperate thread"""

    # Initiate scraper
    logger.info(f"Worker {id} started ...")
    scraper = DefaultScraper(str(id), logger, timeout=5)

    # Process tasks
    for task_id, task in enumerate(tasks):

        try:

            # create the scraping result
            r = ScrapingResult(target_url=task["url"])

            # Fetch webpage content
            try:
                r = scraper.get(r)
                status = Status.CONTENT_FETCHED
            except Exception as e:
                logger.error(f"Worker {id:2}:  {repr(e)}")
                status = Status.FAILED

            # Write webpage content to file system
            meta = {"target_url": task["url"], "article_id": task["_id"]}
            file_id = savePageContent(
                fs, r.content_html, r.encoding, attr=meta)

            # Update task status and save webpage content reference
            r.content_html = str(file_id)

            # Updated tasks by changig status and info about sraping results
            updateTask(db, id=task["_id"],
                       values={'status': status},
                       result=r.model_dump())

            time.sleep(timeout)
            logger.info(
                f"Worker {id:2}: [{str(r.status_code)}] [{task_id}/{len(tasks)}] {str(r.target_url)}")

        except Exception as e:
            logger.error(f"Worker {id:2}:  {repr(e)}")

    logger.info(f"Worker {id:2}: finished")


# ---------------------------------------------------------------------------
#                            MAIN
# ---------------------------------------------------------------------------

# fmt: off
@click.command()
@click.option("--path_logfile", default="logs.log", help="Logfile location")
@click.option("--workers", default=4, help="Number of threads used for scraping")
@click.option("--timeout", default=1, help="Time give for the request in seconds")
@click.option("--limit", default=100, help="Only scraping first n urls (0 equals no limit)")
@click.option('--status', default="UNPROCESSED", help="Any status (FAILED, UNPROCESSED, etc.)")
@click.option("--max_retries", default=5, help="Consider only URLs which were scraped less than n times (0 to force)")
@click.option("--batch", default="last", help="all, first last, or a number indicating the batch")
def main(path_logfile, workers, timeout, limit, status,  max_retries, batch): 

    # ------------------- LOGGING -------------------

    # Create logger
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s  %(levelname)-8s %(message)s")

    # Log to terminal
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # Log to file
    file_handler = logging.FileHandler(path_logfile)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("Start Scraping Run")

    # fmt: on
    timer_start = perf_counter()

    # ------------------- DATABASE -------------------

    # Connect to Database
    fs, db = getConnection(use_dotenv=True)

    # Only retrieve the fields that are necessary for the scraping
    fields = {'media_url': 1, 'url': 1, 'tries': 1}

    # ------------------- FETCH TASKS -------------------

    tasks = fetchTasks(db, None, status, limit, fields)
    logger.info(f"Number of URLs: {len(tasks)}")

    # ------------------- RETRIES -------------------

    max_retries = max_retries if max_retries else math.inf
    tasks = [t for t in tasks if t.get("tries", 0) <= max_retries]

    # ------------------- RANDOMIZE TASKS -------------------

    # inplace randomization
    random.shuffle(tasks)

    # ------------------- FETCH CONTENT -------------------

    logger.info(f"Number of URLs to be scraped: {len(tasks)}")

    # if there is more than worker use threads
    if workers > 1:

        threads = []

        # Create and start one thread per chunk
        for id, chunk in enumerate(chunkify(tasks, workers)):
            args = (id, chunk, logger, db, fs, timeout)  # fmt: skip
            t = Thread(target=processTasks, args=args)
            threads.append(t)
            t.start()

        # Wait for the threads to complete
        for t in threads:
            t.join()

    else:
        processTasks(-1, tasks, logger, db, fs, timeout)

    # ------------------- WRAP UP -------------------

    # Print runtime
    timer_stop = perf_counter()
    logger.info("Ending Scraping Run")
    logger.info("Runtime: " + str(round(timer_stop - timer_start, 4)))


if __name__ == "__main__":
    main()
