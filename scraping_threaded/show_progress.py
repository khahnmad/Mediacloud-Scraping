# ===========================================================================
#                            Scraping Progress
# ===========================================================================

from tabulate import tabulate
from datetime import datetime
from utils.database import *
import click
import time

# ================================= MAIN ================================

# fmt: off
@click.command()
@click.option("--refresh_rate", default=30, help="Refresh every n seconds")
# fmt: on
def main(refresh_rate):

    # Connect to database
    _, db = getConnection(use_dotenv=True)

    while True:

        # Header
        click.echo(click.style("Processing Status:", fg="blue", bold=True))

        # Content: current status and document counts
        results = countProcessingStatus(db)
        print(tabulate(results))

        # Footer
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        click.echo(click.style(f"Last updated: {current_time}", fg="green"))
        click.echo(click.style(f"Press Ctrl + c to exit", fg="green"))

        # Wait before refresh
        time.sleep(float(refresh_rate))
        click.clear()


if __name__ == "__main__":
    main()
