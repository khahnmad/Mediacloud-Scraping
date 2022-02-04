import mediacloud_collection as mf

"""
First, gather urls using the MediaCloud API
"""
# Parameters
date = [2020,10,15]
my_api_key = 'MC_API_KEY' # this should be the name of your api key in your .env file
keyword = 'kentucky'
collection = 'tags_id_media:34412234' # this the US National News collection
access_mediacloud = mf.AccessMediaCloud(key_file=my_api_key)
# Exports a csv file with the urls for the given query
access_mediacloud.collection_pipeline(year=date[0], month=date[1], day=date[2], keyword=keyword, collection=collection,
                                      length=1)
# the title of the exported csv file will be the following:
# title = f'{year}-{month}-{day}_{keyword}.csv'
urls_file =  f'{date[0]}-{date[1]}-{date[2]}_{keyword}.csv'

"""
Second, scrape the gathered urls using BeautifulSoup
"""
scraper = mf.ScrapeArticles()
scraper.extract_article_content(csv_file=urls_file, event_name="example-process")
