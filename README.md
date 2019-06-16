# App Review Scraper 

A simple Python scraper to get reviews from Google Play Store and App Store. This script scrapes the reviews (sorted by most recent) and saves it as a **.csv file**.


### Requirements:
- [Python 3](https://www.python.org/downloads/)


### Sample usage:

<pre>
python scrape.py <b>--pages</b> 3 <b>--android</b> com.facebook.katana <b>--ios</b> 284882215 <b>--country</b> ph <b>--output</b> reviews.csv
</pre>


### Parameters:
- \-\-pages - the number of pages to scrape (40 per page)
- \-\-country - the country code where the reviews will be scraped (only for iOS)
- \-\-android - the Google Play Store App ID of the app you want to scrape reviews (ex. https/\/play.google.com/store/apps/details?id=**edu.mobapde.wake**)
- \-\-ios - the App Store App ID of the app you want to scrape reviews (ex. https/\/apps.apple.com/ph/app/facebook/id**284882215**)
- \-\-output - the file path where the .csv file will be saved
