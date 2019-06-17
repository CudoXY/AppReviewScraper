# Originally from https://gist.github.com/kgn/e96e7ae71a38447ac614

# Install packages from script
import subprocess
import sys

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

install('requests')
install('pandas')
install('feedparser')

# -----------------------------

from optparse import OptionParser
from pathlib import Path
import feedparser
import pandas as pd

# Constants
COLUMN_TITLE = 'title'
COLUMN_REVIEW_DATE = 'review_date'
COLUMN_AUTHOR = 'author'
COLUMN_AUTHOR_URL = 'author_url'
COLUMN_VERSION = 'version'
COLUMN_RATING = 'rating'
COLUMN_REVIEW = 'review'
COLUMN_VOTE_COUNT = 'vote_count'
COLUMN_VOTE_SUM = 'vote_sum'

URL_APPSTORE_REVIEWS = 'https://itunes.apple.com/%s/rss/customerreviews/id=%s/page=%d/sortby=mostrecent/xml'


def create_df():
    """
    Creates the base DataFrame for the reviews table containing the necessary columns.

    :return:
        The base Pandas DataFrame
    """
    return pd.DataFrame(columns=[COLUMN_TITLE, COLUMN_REVIEW_DATE, COLUMN_AUTHOR, COLUMN_AUTHOR_URL,
                                 COLUMN_VERSION, COLUMN_RATING, COLUMN_REVIEW, COLUMN_VOTE_COUNT, COLUMN_VOTE_SUM])


def get_app_store_reviews(app_store_id, country, page_index=1):
    """
    Scrapes the App Store reviews based on the page index.

    :param app_store_id:
        App Store App ID (starts at 1)

    :param country:
        The country where the reviews will be scraped from

    :param page_index:
        The page index

    :return:
        The Pandas DataFrame object of the scraped values
    """

    def parse_xml(url):
        """
        Parses the XML object from the RSS URL

        :param url:
            URL of the App Store RSS (in JSON format)

        :return:
            The parsed XML object
        """
        return feedparser.parse(url)

    url = URL_APPSTORE_REVIEWS % (country, app_store_id, page_index)
    data = parse_xml(url)

    # Format the data into a table\
    df = create_df()
    df[COLUMN_TITLE] = [entry['title'].replace('’', '\'') for entry in data.entries[1:]]

    df[COLUMN_REVIEW_DATE] = [entry['updated'] for entry in data.entries[1:]]
    df[COLUMN_REVIEW_DATE] = pd.to_datetime(df[COLUMN_REVIEW_DATE])

    df[COLUMN_AUTHOR] = [entry['author_detail']['name'] for entry in data.entries[1:]]
    df[COLUMN_AUTHOR_URL] = [entry['author_detail']['href'] for entry in data.entries[1:]]
    df[COLUMN_VERSION] = [entry['im_version'] for entry in data.entries[1:]]
    df[COLUMN_RATING] = [int(entry['im_rating']) for entry in data.entries[1:]]
    df[COLUMN_REVIEW] = [entry['content'][0]['value'].replace('’', '\'') for entry in data.entries[1:]]
    df[COLUMN_VOTE_COUNT] = [int(entry['im_votecount']) for entry in data.entries[1:]]
    df[COLUMN_VOTE_SUM] = [int(entry['im_votesum']) for entry in data.entries[1:]]

    print("[*] Retrieved " + str(len(df)) + " reviews")

    return df


def save_page_reviews(app_store_id, country, page_count, output_file_path):
    """
    Scrapes and saves the App Store reviews based on the given the number of pages.

    :param app_store_id:
        App Store App ID

    :param country:
        The country where the reviews will be scraped from

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

        df_review = get_app_store_reviews(app_store_id, country, i + 1)

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
    parser.add_option("-c", "--country",
                      action="store",
                      dest="country",
                      default="ph",
                      help="The country code where the reviews will be scraped", )

    (options, args) = parser.parse_args()

    print("[*] Downloading the first " + str(options.pages) + " pages from: " + options.app_id)

    save_page_reviews(options.app_id, options.country, options.pages, options.output)

    print("[*] Finished downloading to file " + options.output)


if __name__ == '__main__':
    main()
