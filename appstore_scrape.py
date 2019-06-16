# Originally from https://gist.github.com/kgn/e96e7ae71a38447ac614

try:
    from pip import main as pipmain
except ImportError:
    from pip._internal import main as pipmain

pipmain(['install', 'requests'])
pipmain(['install', 'pandas'])

from optparse import OptionParser
from pathlib import Path
from urllib.request import urlopen

import json
import pandas as pd

# Constants
COLUMN_REVIEW_ID = 'id'
COLUMN_TITLE = 'title'
COLUMN_AUTHOR = 'author'
COLUMN_AUTHOR_URL = 'author_url'
COLUMN_VERSION = 'version'
COLUMN_RATING = 'rating'
COLUMN_REVIEW = 'review'
COLUMN_VOTE_COUNT = 'vote_count'

URL_APPSTORE_REVIEWS = 'https://itunes.apple.com/rss/customerreviews/id=%s/page=%d/sortby=mostrecent/json'


def create_df():
    """
    Creates the base DataFrame for the reviews table containing the necessary columns.

    :return:
        The base Pandas DataFrame
    """
    return pd.DataFrame(columns=[COLUMN_REVIEW_ID, COLUMN_TITLE, COLUMN_AUTHOR, COLUMN_AUTHOR_URL,
                                 COLUMN_VERSION, COLUMN_RATING, COLUMN_REVIEW, COLUMN_VOTE_COUNT])




def get_app_store_reviews(app_store_id, page_index=1):
    """
    Scrapes the App Store reviews based on the page index. As of this implementation, the App Store
    only returns 30 reviews per page.

    :param play_store_id:
        App Store App ID (starts at 1)

    :param page_index:
        The page index

    :return:
        The Pandas DataFrame object of the scraped values
    """

    def parse_json(url):
        """
        Parses the JSON object from the RSS URL

        :param url:
            URL of the App Store RSS (in JSON format)

        :return:
            The parsed JSON object
        """
        response = urlopen(url)
        response_data = str(response.read().decode("utf-8"))
        return json.loads(response_data)

    url = URL_APPSTORE_REVIEWS % (app_store_id, page_index)
    data = parse_json(url).get('feed')

    if data.get('entry') is None:
        return

    df = create_df()
    review_id_list = []
    title_list = []
    author_list = []
    author_url_list = []
    version_list = []
    rating_list = []
    review_list = []
    vote_count_list = []

    for entry in data.get('entry'):
        if entry.get('im:name'):
            continue

        review_id_list.append(entry.get('id').get('label'))
        title_list.append(entry.get('title').get('label').replace('"', '""'))
        author_list.append(entry.get('author').get('name').get('label'))
        author_url_list.append(entry.get('author').get('uri').get('label'))
        version_list.append(entry.get('im:version').get('label'))
        rating_list.append(entry.get('im:rating').get('label'))
        review_list.append(entry.get('content').get('label').replace('"', '""'))
        vote_count_list.append(entry.get('im:voteCount').get('label'))

    # Format the data into a table
    df[COLUMN_REVIEW_ID] = review_id_list
    df[COLUMN_TITLE] = title_list
    df[COLUMN_AUTHOR] = author_list
    df[COLUMN_AUTHOR_URL] = author_url_list
    df[COLUMN_VERSION] = version_list
    df[COLUMN_RATING] = rating_list
    df[COLUMN_REVIEW] = review_list
    df[COLUMN_VOTE_COUNT] = vote_count_list

    print("[*] Retrieved " + str(len(df)) + " reviews")

    return df


def save_page_reviews(app_store_id, page_count, output_file_path):
    """
    Scrapes and saves the App Store reviews based on the given the number of pages.

    :param app_store_id:
        App Store App ID

    :param page_count:
        The number of page to be scraped

    :param output_file_path:
        The path where to save the output file

    :return:
        The Pandas DataFrame object of the scraped values
    """

    df_result = pd.DataFrame()
    output_file = Path(output_file_path)
    for i in range(0, int(page_count)):

        df_review = get_app_store_reviews(app_store_id, i+1)

        if df_review is None or len(df_review) <= 0:
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

