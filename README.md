## Robin Stonks
#### My lame attempt to have a python script manage my stock portfolio

Best to run this in a virtual environment to keep things clean.

`git clone https://github.com/georgefahmy/stonks.git`

`cd stonks`

`pip install .`


Run `python nltk_download.py` and download 'all-corpora'.
_(need to look into this more for tuning the model)_

Before running any scripts, run `get_symbols` to generate the tickers.txt. This file
is used for determining whether a set of capital letters used in a comment is a stock symbol or not.

Main scripts help description below.

If stock tickers are showing up that you suspect are not of importance, or actually being
discussed, edit the `src/utils/ignore.py`. Also you can use the `-i <TICKER SYMBOLS...>` as an
optional flag for temporarily ignoring additional stock symbols.

### wsb_report
```
usage: wsb_report [-h] [--type-flag TYPE_FLAG] [--submissions SUBMISSIONS]
                  [-c COMMENTS] [-p PRINT] [--sub-score SUB_SCORE]
                  [--com-score COM_SCORE] [-i [IGNORE [IGNORE ...]]] [-d]
                  [--debug]
                  type

Generate a report for stock mentions and the number of occurrences in
/r/wallstreetbets. Options allow for different types of filters and
thresholds.

positional arguments:
  type                  Choose which submissions to search: top, hot or new,
                        If top, --type-flag is an optional flag to choose day,
                        week, month, year, all

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
  --sub-score SUB_SCORE
                        Minimum submission score to include in analysis.
                        Default=5
  --com-score COM_SCORE
                        Minimum comment score to include in analysis.
                        Default=5
  -i [IGNORE [IGNORE ...]], --ignore [IGNORE [IGNORE ...]]
                        List of stock symbols to ignore
  -d, --display_dict    Option to display dictionary of all stocks found.
                        Default=False
  --debug               Displays debug messages in console
```


### streamer

```
usage: streamer [-h] [-l] [-s] [-m] [--debug]

Reddit WallStreetBets stream with stock extraction from comments. Includes
comment sentiment as well as links to the comment URL. Stock symbol extraction
can also be used to automate retrieving stock price information.

optional arguments:
  -h, --help       show this help message and exit
  -l, --link       optional flag to display comment permalink in the stream.
                   Default=False
  -s, --sentiment  Optional flag to display comment sentiment (experimental).
                   Default=False
  -m, --multi      Optional flag to stream from r/wallstreetbets, r/wsb,
                   r/investing. Default=False
  --debug          Displays debug messages in console
```

### all_stream

```
usage: all_stream [-h] [-f [FILTER [FILTER ...]]] [-st] [-l] [-s] [--debug]
                  [subreddits [subreddits ...]]

all_stream.py streams one or more subreddits' comments. Add --filter option
for filtering for specific words in the comment body. Additional options
available

positional arguments:
  subreddits            Subreddit(s) to pull comment stream from.

optional arguments:
  -h, --help            show this help message and exit
  -f [FILTER [FILTER ...]], --filter [FILTER [FILTER ...]]
                        Optional flag to filter for specific text in comment
                        body. Default=None
  -S, --stocks         Optional flag to display stock information found in
                        the comment. Default=False
  -l, --link            Optional flag to display comment url in the stream.
                        Default=False
  -s, --sentiment       Optional flag to display comment sentiment
                        (experimental). Default=False
  --debug               Displays debug messages in console
  ```
