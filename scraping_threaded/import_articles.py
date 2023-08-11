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

# --------------------------------- Import Functions  --------------------------------


def insertArticles(db, batch_id: int, articles: list):
    """Inserts list of articles into database"""
    data = []
    # for article in tqdm(list(articles), desc="Articles"):
    for article in articles:
        data.append(Article(batch_id=batch_id, **
                    article).model_dump(mode="json"))
    return db.articles.insert_many(data)


# ================================= MAIN ================================

# fmt: off
@click.command()
@click.option("--path", default="./articles.json", help="Location of JSON file")
@click.option("--batchsize", default=1000, help="Number of articles per batch")
@click.option("--overwrite", default=False, help="Delete last imported batch")
def main(path, batchsize, overwrite):
# fmt: on

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

    with open(path, 'r') as json_file:
        # Count total lines in the file
        total_lines = sum(1 for line in json_file)

        json_file.seek(0)  # Reset file pointer
        batch = []

        with tqdm(total=total_lines, desc="Articles") as pbar:  # Initialize tqdm progress bar
            for line in json_file:
                record = json.loads(line)
                batch.append(record)

                if len(batch) == batchsize:
                    insertArticles(db, new_batch_id, batch)
                    batch = []

                pbar.update(1)  # Update progress bar for each line

            # Process the remaining records in the last batch
            if batch:
                insertArticles(db, new_batch_id, batch)

    # Insert Metadata
    # result = insertArticles(db, new_batch_id, list(articles))
    # click.echo(click.style(
    #    f"Articles importet to be scraped: {len(result.inserted_ids)}", fg="green"))

    # ------------------------------------------------

    # Print runtime
    timer_stop = perf_counter()
    print("Runtime:", round(timer_stop - timer_start, 4), "s")


if __name__ == "__main__":
    main()
