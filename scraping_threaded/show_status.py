# ===========================================================================
#                            Scraping Statistics
# ===========================================================================

from tabulate import tabulate
from time import perf_counter
from utils.database import *
import click

# ================================= MAIN ================================


@click.command()
def main():

    timer_start = perf_counter()

    # Connect to database
    _, db = getConnection(use_dotenv=True)

    # Content
    # Processing status counts
    click.echo(click.style("Processing Status:", fg="blue", bold=True))
    results = countProcessingStatus(db)
    print(tabulate(results))

    # HTTP status codes
    click.echo(click.style("\nHTTP Status Codes:", fg="blue", bold=True))
    results = countStatusCodes(db)
    print(tabulate(results))

    # Print runtime
    timer_stop = perf_counter()
    print("Runtime:", round(timer_stop - timer_start, 4))


if __name__ == "__main__":
    main()
