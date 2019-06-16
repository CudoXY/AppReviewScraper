# Google Play Store Scraper

A simple Python scraper to get reviews from the Google Play Store sorted by the most recent review, and save it as a .csv file.

### Requirements:
- [Python 3](https://www.python.org/downloads/)


### Sample usage:
```
python play_scrape.py --pages 3 --id edu.mobapde.wake --output reviews.csv
```

### Parameters:
- \-\-pages - the number of pages to scrape (40 per page)
- \-\-id - the app ID from the Google Play Store (ex. https://play.google.com/store/apps/details?id=**edu.mobapde.wake**)
- \-\-output - the file path where the CSV will be saved

---
_Originally forked from https://github.com/RiccardoAncarani/play-scrape_
