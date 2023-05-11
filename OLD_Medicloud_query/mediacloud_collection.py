# Imports
from dotenv import load_dotenv # reads key-value pairs from a .env file
import os
import mediacloud.api
import datetime
import time
import mediacloud.tags
import csv
from dateutil.relativedelta import *
from bs4 import BeautifulSoup as bs
import requests
import glob
import requests.exceptions
import re

# Miscellaneous functions
def import_csv(csv_file):  # parses data into a nested list
    nested_list = []  # initialize list
    with open(csv_file, newline='', encoding='utf-8') as csvfile:  # open csv file
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            nested_list.append(row)  # add each row of the csv file to a list
    return nested_list

def export_nested_list(csv_name, nested_list):
    with open(csv_name, 'w', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in nested_list:
            writer.writerow(row)


class AccessMediaCloud:
    def __init__(self, key_file):
        self.key_file = key_file


    def setup(self):
        load_dotenv()
        api_key = os.getenv(self.key_file) # Read API key from the .env file
        # Check that the key works with mediacloud
        mc = mediacloud.api.MediaCloud(api_key)

        # print('MediaCloud version:', mediacloud.__version__)
        # make sure your connection and API key work by asking for the high-level system statistics
        # a = time.time()
        # mc.stats()
        # b = time.time()
        # print('Connection check:', b - a)
        return mc

    # Media Cloud functions
    def all_matching_stories(self, mc_client, q, fq):
        """
        Return all the stories matching a query within Media Cloud. Page through the results automatically.
        :param mc_client: a `mediacloud.api.MediaCloud` object instantiated with your API key already
        :param q: your boolean query
        :param fq: your date range query
        :return: a list of media cloud story items
        """
        last_id = 0
        more_stories = True
        stories = []
        while more_stories:
            page = mc_client.storyList(q, fq, last_processed_stories_id=last_id, rows=500, sort='processed_stories_id')
            print("  got one page with {} stories".format(len(page)))
            if len(page) == 0:
                more_stories = False
            else:
                stories += page
                last_id = page[-1]['processed_stories_id']
        return stories


    def collect_stories(self, query, dates):
        # Check how many stories are there
        mc = self.setup()
        story_count = mc.storyCount(query, dates)
        print(f'There are {mc.storyCount(query, dates)["count"]} stories for the query')

        # Fetch all the stories that match the query
        a = time.time()
        all_stories = self.all_matching_stories(mc, query, dates)
        b = time.time()
        # print(f'Takes {b - a} seconds to run')

        # flatten things a little bit to make writing a CSV easier
        for s in all_stories:
            # see the "language" notebook for more details on themes
            theme_tag_names = ','.join(
                [t['tag'] for t in s['story_tags'] if t['tag_sets_id'] == mediacloud.tags.TAG_SET_NYT_THEMES])
            s['themes'] = theme_tag_names
        return all_stories


    def write_csv(self, all_stories, name):
        # NOTE: Edit the fieldnames as preferred
        fieldnames = ['stories_id', 'publish_date', 'title', 'url', 'language', 'ap_syndicated', 'themes', 'media_id',
                      'media_name', 'media_url']
        with open(name, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for s in all_stories:
                writer.writerow(s)


    def collection_pipeline(self, year: int, month: int, day: int, keyword, collection, length):
        # establish query - mass shooting = search word, US national media = collection
        # ms_us_query = '"mass shooting" and tags_id_media:34412234'
        query = f"{keyword} and {collection}"
        mc = self.setup()

        # todo: make time period generalizable

        # establish date range
        start_date = datetime.date(year, month, day)
        end_date = start_date + datetime.timedelta(days=length)
        # end_first_month = start_date + relativedelta(months=+1)
        # end_second_month = end_first_month + relativedelta(months=+1)
        # end_third_month = end_second_month + relativedelta(months=+1)

        time_segment = mc.dates_as_query_clause(start_date, end_date)  # default is start & end inclusive
        # second_month = mc.dates_as_query_clause(end_first_month, end_second_month)
        # third_month = mc.dates_as_query_clause(end_second_month, end_third_month)

        stories =  self.collect_stories(query, time_segment)
        # first_month_stories = self.collect_stories(query, first_month)
        # second_month_stories = self.collect_stories(query, second_month)
        # third_month_stories = self.collect_stories(query, third_month)
        # print('COLLECTED ALL STORIES')

        # Combine to one nested list for all data
        # all_stories = []
        # for i in range(len(first_month_stories)):
        #     all_stories.append(first_month_stories[i])
        # for i in range(len(second_month_stories)):
        #     all_stories.append(second_month_stories[i])
        # for i in range(len(third_month_stories)):
        #     all_stories.append(third_month_stories[i])

        # Export data
        title = f'{year}-{month}-{day}_{keyword}.csv'
        self.write_csv(stories, title)
        # print('PROCESS COMPLETE')

class ScrapeArticles:
    def __init__(self):
        pass
    def access_article(self, url):  # Acesses a single url and returns all the url's p tags
        soup = bs(requests.get(url, timeout=20).text, "html.parser")
        # timeout for the request is 20 seconds; it never takes longer than 10 seconds for a working link, so this is
        # safe
        if 'rss.cnn' in url:
            body_text = soup.find_all("div", {"class": "zn-body__paragraph"})
            stripped_paragraph = [tag.get_text().strip() for tag in body_text]
        else:
            paragraphs = soup.find_all('p')  # justify that this is working for the articles by taking a manual sample
            stripped_paragraph = [tag.get_text().strip() for tag in paragraphs]
        return [url, " ".join(stripped_paragraph)]  # [url, text from the url]

    def get_text(self, urls_list, event_name,starting_url=0):
        # given a list of urls, returns the text from the working urls and a list of the bad urls
        # Initialize variables
        url_text = [['url', 'text']]
        bad_urls, midpoint_urls = [], []
        for i in range(starting_url, len(urls_list)):  # iterate through the urls
            if str(i).endswith('00') == True:
                print(f'    working on number {i}')
            try:
                text = self.access_article(urls_list[i])
                url_text.append(text)  # get the article text
                midpoint_urls.append(text)
            except requests.exceptions.ReadTimeout:
                bad_urls.append(['Timeout error', urls_list[i]])

            except requests.exceptions.ConnectionError:
                bad_urls.append(['Connection error', urls_list[i]])

            except requests.exceptions.TooManyRedirects:
                bad_urls.append(['Too Many Redirects', urls_list[i]])

            if str(i).endswith('000'):  # Exports the gathered information before running through all urls
                # Export urls & text that has been gathered so far
                csv_file_name = event_name + '_text-' + str(i) + '.csv'
                export_nested_list(csv_file_name, midpoint_urls)

                # Export list of a bad urls
                bad_urls_csv_name = event_name + '_bad-urls-' + str(i) + '.csv'
                export_nested_list(bad_urls_csv_name, bad_urls)

        return url_text, bad_urls

    # SUMMARY FUNCTION
    def extract_article_content(self, csv_file, event_name):
        mediacloud_content = import_csv(csv_file)
        if mediacloud_content != None:  # in case 0 urls are gathered from mediacloud from this timeframe
            urls = [mediacloud_content[i][3] for i in range(1, len(mediacloud_content))]
            text, bad_urls = self.get_text(urls, event_name)
            # print('GOT TEXT')

            for i in range(len(mediacloud_content)):
                for j in range(len(text)):
                    if text[j][0] == mediacloud_content[i][3]:
                        # if the urls match, then append the text to the original list
                        mediacloud_content[i].append(text[j][1])

            # Export nested list of all mediacloud content + the text from the given url
            csv_file_name = event_name + '_text.csv'
            export_nested_list(csv_file_name, mediacloud_content)
            # Export list of a bad urls
            bad_urls_csv_name = event_name + '_bad-urls.csv'
            export_nested_list(bad_urls_csv_name, bad_urls)
            # print('--PROCESS COMPLETE--')