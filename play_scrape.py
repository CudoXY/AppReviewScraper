# Install packages from script
import subprocess
import sys

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

install('requests')
install('pandas')

# -----------------------------

import requests
import re
from optparse import OptionParser
import pandas as pd
from pathlib import Path

# Constants
REVIEW_SORT_ORDER_NEWEST = 0
REVIEW_SORT_ORDER_RATING = 1

COLUMN_AUTHOR = 'author'
COLUMN_REVIEW_DATE = 'review_date'
COLUMN_RATING = 'rating'
COLUMN_CONTENT = 'content'

URL_GOOGLEPLAY_REVIEWS = "https://play.google.com/store/getreviews?authuser=0"


def create_df():
    """
    Creates the base DataFrame for the reviews table containing the necessary columns.

    :return:
        The base Pandas DataFrame
    """
    return pd.DataFrame(columns=[COLUMN_AUTHOR, COLUMN_REVIEW_DATE, COLUMN_RATING, COLUMN_CONTENT])


#
def get_google_play_reviews(play_store_id, page_index):
    """
    Scrapes the Play Store reviews based on the page index. As of this implementation, the Play Store
    only returns 40 reviews per page.

    :param play_store_id:
        Play Store App ID
    
    :param page_index:
        The page index
        
    :return:
        The Pandas DataFrame object of the scraped values
    """

    def parse_author_name(response):
        """
        Parses the author name from the POST request from Google Play

        :param response:
            The response from the POST request from Google Play

        :return:
            The parsed list of author name
        """

        return [author[9:][:-44] for author in re.findall("author-name(.*?)review-date", response.text)]

    def parse_rating(response):
        """
        Parses the ratings from the POST request from Google Play

        :param response:
            The response from the POST request from Google Play

        :return:
            The parsed list of ratings
        """

        return [int(rating) for rating in re.findall("Rated (.*?) stars out of five stars", response.text)]

    def parse_review_date(response):
        """
        Parses the review date from the POST request from Google Play

        :param response:
            The response from the POST request from Google Play

        :return:
            The parsed list of review date
        """

        return [review_date[8:][:-39] for review_date in re.findall("review-date(.*?)reviews-permalink", response.text)]

    def parse_review_content(response):
        """
        Parses the review content from the POST request from Google Play

        :param response:
            The response from the POST request from Google Play

        :return:
            The parsed list of review content
        """

        return [review_content[26:][:-24].encode('ascii', 'ignore').decode('ascii').replace('\\\"', '\"')
                for review_content in re.findall("review-title(.*?)review-link", response.text)]

    # Creates a POST request to be scraped
    data = {
        "reviewType": 0,
        "pageNum": page_index,
        "id": play_store_id,
        "reviewSortOrder": REVIEW_SORT_ORDER_NEWEST,
        "xhr": 1,
        "hl": "en"
    }
    r = requests.post(URL_GOOGLEPLAY_REVIEWS, data=data)

    # Format the data into a table
    df = create_df()
    df[COLUMN_AUTHOR] = parse_author_name(r)
    df[COLUMN_REVIEW_DATE] = parse_review_date(r)
    df[COLUMN_REVIEW_DATE] = pd.to_datetime(df[COLUMN_REVIEW_DATE])
    df[COLUMN_RATING] = parse_rating(r)
    df[COLUMN_CONTENT] = parse_review_content(r)

    print("[*] Retrieved " + str(len(df)) + " reviews")

    return df


def save_page_reviews(play_store_id, page_count, output_file_path):
    """
    Scrapes and saves the Play Store reviews based on the given the number of pages.

    :param play_store_id:
        Play Store App ID

    :param page_count:
        The number of page to be scraped

    :param output_file_path:
        The path where to save the output file

    :return:
        The Pandas DataFrame object of the scraped values
    """

    df_result = pd.DataFrame()
    output_file = Path(output_file_path)
    for i in range(int(page_count)):

        df_review = get_google_play_reviews(play_store_id, i)

        if len(df_review) <= 0:
            continue

        df_result = pd.concat([df_result, df_review])

        print("[*] Appending " + str(len(df_review)) + " reviews to file")
        df_review.to_csv(output_file_path, mode='a', index=False, header=not output_file.is_file())

    return df_result


def main():
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    parser.add_option("-p", "--pages",
                      action="store",
                      dest="pages",
                      default=5,
                      help="The number of pages you want to scrape", )
    parser.add_option("-i", "--id",
                      action="store",
                      dest="app_id",
                      help="The id of the app you want to scrape comments", )
    parser.add_option("-o", "--output",
                      action="store",
                      dest="output",
                      default="output.csv",
                      help="The output file where you want to dump results", )

    (options, args) = parser.parse_args()

    print("[*] Downloading the first " + str(options.pages) + " pages from: " + options.app_id)

    save_page_reviews(options.app_id, options.pages, options.output)

    print("[*] Finished downloading to file " + options.output)


if __name__ == '__main__':
    main()
