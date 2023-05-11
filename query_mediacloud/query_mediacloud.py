"""
INPUT:
    - query phrase
    - start date
    - end date
    - collection id

OUTPUT: All stories (urls) from MediaCloud via the Wayback Machine that meet these parameters

"""
# Imports
from waybacknews.searchapi import SearchApiClient
import mediacloud.api
import dotenv
import os
import datetime as dt

import shared_functions as sf

# Load env variables
dotenv.load_dotenv()

# FUNCTIONS
def load_api_clients():
    # Loads the Api clients necessary
    MC_API_KEY = os.getenv('MC_API_KEY')  # Read the API key
    mc_dir = mediacloud.api.DirectoryApi(MC_API_KEY)

    wm_api = SearchApiClient("mediacloud")
    return mc_dir, wm_api


def get_domains(mc_directory,collection_id:int)->list:
    # Source: @rahulbot : https://github.com/mediacloud/api-client/issues/82
    # Get all the domains that form part of the given collection
    # Variables
    SOURCES_PER_PAGE = 100
    offset = 0

    sources = []
    while True:
        # grab a page of sources in the collection
        response = mc_directory.source_list(collection_id=collection_id, limit=SOURCES_PER_PAGE, offset=offset)
        # add it to our running list of all the sources in the collection
        sources += response['results']
        # if there is no next page then we're done so bail out
        if response['next'] is None:
            break
        # otherwise setup to fetch the next page of sources
        offset += len(response['results'])

    domains = [s['name'] for s in sources]
    return domains


def get_stories(query_phrase:str, collection_id:int, start_date, end_date)->list:
    # Get all the stories for the given query, collection, and time period

    n = 400 # number of domains that you can give in one query, 400 seems to work

    # API CLIENTS
    mc_dir, wm_api = load_api_clients()

    # Get domains
    domains = get_domains(mc_dir, collection_id)
    print(f"    - Got {len(domains)} domains")

    # Get stories
    if len(domains) < n+1:
        stories = list(
            wm_api.all_articles(f'"{query_phrase}" AND domain:({" OR ".join(domains)})', start_date, end_date))
    else:
        # Break up the domains into segments and query each one
        stories = []
        for i in range(int(len(domains)/n)+1):
            domain_segment = domains[i * n:(i * n) + n]
            stories += list(
                wm_api.all_articles(f'"{query_phrase}" AND domain:({" OR ".join(domain_segment)})',
                                    start_date, end_date))
    return stories




# ADJUSTABLE VARIABLES
query_phrase = 'kentucky'
start_date = dt.datetime(2022, 2, 9)
end_date = dt.datetime(2022, 2, 12)
collection = 200363050 # US CENTER 2019


if __name__ == '__main__':
    exportable = []
    stories = get_stories(query_phrase, collection, start_date, end_date)
    for elt in stories:
        exportable += elt
    print(f"    - found {len(exportable)} stories\n")
    sf.export_as_json(export_name=f'output/{query_phrase}_{collection}.json',data=exportable)

