import shared_functions as sf

from scraping_scripts import scraping_support_functions as ss

import random
import time

import requests
from bs4 import BeautifulSoup as bs


def read_url(url:str)->str:
    # 1) Check if it's website that does not return article text, like google maps
    scrapable = ss.check_scrapability(url)
    if scrapable is not True:
        return scrapable # returns the error associated with the not scrapeable website

    # 2) Try to get soup & handle errors
    try:
        response = requests.get(url, timeout=20).text
        # timeout for the request is 20 seconds; should never take longer than 10 seconds for a working link
        if len(response) == 0:
            return "ERROR: Article not found"

        soup = bs(response, "html.parser")
    except requests.exceptions.ConnectionError:
        return "ERROR: requests.exceptions.ConnectionError"
    except requests.exceptions.ReadTimeout:
        return "ERROR: requests.exceptions.ReadTimeout"
    except requests.exceptions.TooManyRedirects:
        return "ERROR: Too Many redirects"
    except Exception as e:
        return f"ERROR: {e}"

    # 3) Get article text from soup

    # Check to see if the soup contains explicit errors
    valid_soup = ss.check_soup_validity(soup.text.lower())
    if valid_soup is not True:
        return valid_soup # return the error if it is found

    # Check if an alternative form of article text extraction is necessary
    alt_scraping = ss.do_alternative_scraping(url, response, soup)
    if alt_scraping is not None:
        return alt_scraping # Return the extracted text if alt scraping was necessary

    # Get contents of the page in the standard way
    paragraphs = soup.find_all('p')
    stripped_paragraph = [tag.get_text().strip() for tag in paragraphs]

    # If the standard way to scrape returned empty, try a different handling
    if len(stripped_paragraph) == 0 or stripped_paragraph == [""]:
        return ss.handle_empty_ptags(url, soup, response)

    return " ".join(stripped_paragraph)  # return the content as one string


def scrape_urls(data:list, english_only:bool):
    for i in range(len(data)):
        obj = data[i]

        # Check if the article is not in English & if English is required
        if english_only and obj['language']!='en':
            obj['text'] = 'ERROR: Not in English'
            continue

        # If the same domain is scraped twice in a row, add a random pause
        if obj['domain'] == data[i-1]['domain']:
            random_time = random.randint(1, 5)
            time.sleep(random_time)

        # Extract article text
        obj['text'] = read_url(obj['url'])

    sf.export_as_json('scraped_text.json',data)

if __name__ == '__main__':
    # Import sample urls from the mediacloud query
    # urls = sf.import_json_content(str(sf.repo_loc / 'query_mediacloud/output/kentucky_200363050.json'))
    urls = sf.import_json_content(str(sf.repo_loc / 'query_mediacloud/output/testing.json'))

    # Scrape the urls
    text = scrape_urls(urls, english_only=True)
