# Originally from https://github.com/RiccardoAncarani/play-scrape

try:
    from pip import main as pipmain
except ImportError:
    from pip._internal import main as pipmain

pipmain(['install', 'requests'])
pipmain(['install', 'pandas'])

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

    def parse_author_name(str):
        """
        Parses the author name from the scraped HTML element.

        :param str:
            The HTML element to be parsed

        :return:
            The parsed author name
        """

        return str[9:][:-44]

    def parse_review_date(str):
        """
        Parses the review date from the scraped HTML element.

        :param str:
            The HTML element to be parsed

        :return:
            The parsed review date
        """

        return str[8:][:-39]

    def parse_review_content(str):
        """
        Parses the review content from the scraped HTML element.

        :param str:
            The HTML element to be parsed

        :return:
            The parsed review content
        """

        return str[26:][:-24].encode('ascii', 'ignore').decode('ascii').replace('\\\"', '\"')

    # Creates a POST request to be scraped
    data = {
        "reviewType": 0,
        "pageNum": page_index,
        "id": play_store_id,
        "reviewSortOrder": REVIEW_SORT_ORDER_NEWEST,
        "xhr": 1,
        "hl": "en"
    }
    r = requests.post("https://play.google.com/store/getreviews?authuser=0", data=data)

    # Parse the data
    author_list = [parse_author_name(author) for author in re.findall("author-name(.*?)review-date", r.text)]
    review_date_list = [parse_review_date(review_date) for review_date in
                        re.findall("review-date(.*?)reviews-permalink", r.text)]
    stars_list = re.findall("Rated (.*?) stars out of five stars", r.text)
    review_content_list = [parse_review_content(review_content) for review_content in
                           re.findall("review-title(.*?)review-link", r.text)]

    # Format the data into a table
    df = create_df()
    df[COLUMN_AUTHOR] = author_list
    df[COLUMN_REVIEW_DATE] = review_date_list
    df[COLUMN_RATING] = stars_list
    df[COLUMN_CONTENT] = review_content_list

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
