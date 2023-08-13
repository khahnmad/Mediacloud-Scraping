# ===========================================================================
#                            Import Batch of Articles
# ===========================================================================
# Use this file to import a new batch of data. For now, a unique batch ID
# is used to group data. This will be handy if data has to be reimportet.

from schemas import Article
from time import perf_counter
from tqdm import tqdm
from utils.database import *
from utils.files import *
import click
import pydantic as py
import logging
import sys

# --------------------------------- Import Functions  --------------------------------


def read_json_file(file_path, logger):
    """Read and return the lines of a JSON file."""
    try:
        with open(file_path, 'r') as json_file:
            return json_file.readlines()
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return []


def process_file(file_path, db, batch_size, batch_id, logger):
    """Process a JSON file, decode content, and insert articles in batches."""

    logger.info(f"Processing file {file_path}")
    lines = read_json_file(file_path, logger)

    if not lines:
        return

    batch = []

    with tqdm(total=len(lines), desc=os.path.basename(file_path)) as pbar:

        # Extract filename from path
        file_name = os.path.basename(file_path)

        for line in lines:

            try:
                record = json.loads(line)
                batch.append(record)
                if len(batch) == batch_size:
                    insertArticles(db, batch_id, batch, logger, file_name)
                    batch = []
                pbar.update(1)

            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON in {file_path}: {e}")
                continue

        if batch:
            insertArticles(db, batch_id, batch, logger, file_name)


def insertArticles(db, batch_id: int, articles: list, logger, file_name):
    """Inserts list of articles into database"""
    data = []
    # for article in tqdm(list(articles), desc="Articles"):
    for article in articles:
        try:
            article = Article(batch_id=batch_id,
                              imported_from=file_name,
                              **article)
            data.append(article.model_dump(mode="json"))
        except py.ValidationError as e:
            logger.error(f"{e}: {e.__traceback__} - {article}")
    return db.articles.insert_many(data)


# ================================= MAIN ================================

# fmt: off
@click.command()
@click.option("--path_logfile", default="logs_insert.log", help="Logfile location") 
@click.option("--path", default="./data/urls_converted/", help="Location of JSON files")
@click.option("--batchsize", default=1000, help="Number of articles per batch")
@click.option("--overwrite", default=False, help="Delete last imported batch")
def main(path_logfile, path, batchsize, overwrite):
# fmt: on

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

    logger.info("Importing Articles")

    timer_start = perf_counter()

    # ------------------- Read JSON Files -------------------

    # articles = readJSON(path, encoding="utf-8").get("content")

    # ------------------- Connect to Database -------------------

    # Connect to database
    _, db = getConnection(use_dotenv=True)

    # ------------------- Batch ID -------------------

    # Delete previous batch; This option is useful
    # in cases where a batch has to be reimported
    if overwrite:
        click.confirm(
            "Are you sure you want to delete last batch?", abort=True)
        old_batch_id = getLatestBatchID(db)
        deleteBatch(db, old_batch_id)

    # Increment Batch ID
    old_batch_id = getLatestBatchID(db)
    new_batch_id = int(old_batch_id) + 1
    click.echo(click.style(
        f"New Batch ID: {new_batch_id}", fg="blue", bold=True))

    # ------------------- Insert Articles -------------------

    # Iterate through all JSON files in the input directory
    for file_name in os.listdir(path):
        if file_name.endswith('.json'):
            file_path = os.path.join(path, file_name)
            process_file(file_path, db, batchsize, new_batch_id, logger)

    # ------------------------------------------------

    # Print runtime
    timer_stop = perf_counter()
    logger.info("Runtime:", str(round(timer_stop - timer_start, 4)), "s")


if __name__ == "__main__":
    main()
