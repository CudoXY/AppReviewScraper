try:
    from pip import main as pipmain
except ImportError:
    from pip._internal import main as pipmain

pipmain(['install', 'requests'])
pipmain(['install', 'pandas'])

import os
from optparse import OptionParser
import appstore_scrape
import play_scrape


# Constants
PLATFORM_ANDROID_FILENAME_SUFFIX = 'android'
PLATFORM_IOS_FILENAME_SUFFIX = 'ios'


def append_platform_to_filename(base_filename, platform_suffix):
    """
    Appends the platform suffix to the end of the file name

    :param base_filename:
        The file name to be appended on

    :param platform_suffix:
        The suffix to be appended

    :return:
        The formatted file name with the suffix
    """

    name, ext = os.path.splitext(base_filename)
    return "{name}_{uid}{ext}".format(name=name, uid=platform_suffix, ext=ext)


def main():
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    parser.add_option("-p", "--pages",
                      action="store",
                      dest="pages",
                      default=5,
                      help="The number of pages you want to scrape")
    parser.add_option("-o", "--output",
                      action="store",
                      dest="output",
                      default="output.csv",
                      help="The output file where you want to dump results")
    parser.add_option("--android",
                      action="store",
                      dest="android_app_id",
                      help="The Google Play Store App ID of the app you want to scrape reviews")
    parser.add_option("--ios",
                      action="store",
                      dest="ios_app_id",
                      help="The App Store App ID of the app you want to scrape reviews")

    (options, args) = parser.parse_args()

    if options.android_app_id is not None and options.android_app_id:
        print("[*] Starting scraping for iOS (%s)", options.android_app_id)
        save_path = append_platform_to_filename(options.output, PLATFORM_ANDROID_FILENAME_SUFFIX)
        play_scrape.save_page_reviews(options.android_app_id, options.pages, save_path)
        print("[*] Finished scraping to file " + save_path)
        print()

    if options.ios_app_id is not None and options.ios_app_id:
        print("[*] Starting scraping for iOS (%s)", options.ios_app_id)
        save_path = append_platform_to_filename(options.output, PLATFORM_IOS_FILENAME_SUFFIX)
        appstore_scrape.save_page_reviews(options.ios_app_id, options.pages, save_path)
        print("[*] Finished scraping to file " + save_path)
        print()


if __name__ == '__main__':
    main()
