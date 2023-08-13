# ===========================================================================
#                            Scraping Progress
# ===========================================================================

from tabulate import tabulate
from datetime import datetime
from utils.database import *
import click
import time

# ================================= HELPERS ================================


def calcDiff(previous_counts, new_counts):
    result = []
    for item2 in new_counts:

        # New count
        id_value2 = item2.get('_id', "")
        count2 = item2.get('count', 0)

        for item1 in previous_counts:

            # Prev count
            id_value1 = item1.get('_id', "")
            count1 = item1.get('count', 0)

            if id_value1 == id_value2:
                diff = count2 - count1
                break
        else:
            diff = count2
            count1 = 0

        result.append({'_id': id_value2, 'previous_count': count1,
                       'new_count': count2, 'diff': diff})

    return result

# ================================= MAIN ================================

# fmt: off
@click.command()
@click.option("--refresh_rate", default=5, help="Refresh every n seconds")
# fmt: on
def main(refresh_rate):

    # Connect to database
    _, db = getConnection(use_dotenv=True)

    click.echo(click.style("Loading results ...", fg="blue", bold=True))
    results = {}

    while True:

        # Fetch data and calculate diff
        new_results = countProcessingStatus(db)
        results_diff = calcDiff(results, new_results)
        results = new_results
        click.clear()

        # Header
        click.echo(click.style("Processing Status:", fg="blue", bold=True))

        # Content: current status and document counts
        header_names = {"_id": "Status", "previous_count": "Prev. Count",
                        "new_count": "Count", "diff": "Diff"}
        print(tabulate(results_diff, headers=header_names))

        # Footer
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        click.echo(click.style(f"Last updated: {current_time}", fg="green"))
        click.echo(click.style(f"Press Ctrl + c to exit", fg="green"))

        # Wait before refresh
        time.sleep(float(refresh_rate))


if __name__ == "__main__":
    main()
