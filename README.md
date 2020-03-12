## Robin Stonks
#### My lame attempt to have a python script manage my stock portfolio

Best to run this in a virtual environment to keep things clean.

`pip install -r requirements.txt`

Run `python nltk_download.py` and download 'corpora'.
_(need to look into this more for tuning the model)_

Before running `streamer.py` or `wsb_report.py` scripts, run `python get_symbols.py` to generate the tickers.txt. This file
is used for determining whether a set of capital letters used in a comment is a stock symbol or not.

Main scripts help description below.

```
usage: wsb_report.py [-h] [--type-flag TYPE_FLAG] [--submissions SUBMISSIONS]
                      [-c COMMENTS] [-p PRINT] [-s SCORE]
                      [-i [IGNORE [IGNORE ...]]] [-d] [--debug]
                      type

Generate a report for stock mentions and the number of occurrences in
/r/wallstreetbets. Options allow for different types of filters and
thresholds.

positional arguments:
  type                  Choose which submissions to search: top for the day,
                        hot or new

optional arguments:
  -h, --help            show this help message and exit
  --type-flag TYPE_FLAG
                        enter the type of sorting for 'Top': 'day, week,
                        month'
  --submissions SUBMISSIONS
                        Enter the number of submissions to scrape
  -c COMMENTS, --comments COMMENTS
                        Enter the limit for how many comment pages to scrape.
                        Default=None
  -p PRINT, --print PRINT
                        Limit the number of stocks printed after scraping.
                        Default=5
  -s SCORE, --score SCORE
                        Minimum comment score to include in analysis.
                        Default=20
  -i [IGNORE [IGNORE ...]], --ignore [IGNORE [IGNORE ...]]
                        List of stock symbols to ignore
  -d, --display_dict    Option to display dictionary of all stocks found.
                        Default=False
  --debug               Displays debug messages in console
```


Live stream of comments posted to WSB and the stocks found in those comments, as well as the general sentiment (experimental)
```
usage: streamer.py [-h] [-l] [-s] [--debug]

Arguments for which stocks to scrape

optional arguments:
  -h, --help       show this help message and exit
  -l, --link       optional flag to display comment permalink in the stream.
                   Default=False
  -s, --sentiment  Optional flag to display comment sentiment (experimental).
                   Default=False
  --debug          Displays debug messages in console
```
