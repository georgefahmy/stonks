import logging
import re

from praw import Reddit
from pprint import pprint

pbar = ProgressBar(widgets=["Processing Issues: ", Percentage(), " ", Bar(), " ", ETA()])

# Logger
logger = logging.getLogger(__name__)

LOGGER_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"

logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(LOGGER_FORMAT, datefmt=DATE_FORMAT))
logger.addHandler(handler)


# Stream Setup
stream = (
    Reddit("wsb1", user_agent="extraction by /u/willfullytr")
    .subreddit("wallstreetbets")
    .stream.comments()
)

# Generate Tickers dictionary
symbols = {}
for line in [line.rstrip("\n") for line in open("tickers.txt")]:
    symbols[line.split("|")[0]] = line.split("|")[1]

for comment in stream:
    body = comment.body
    caps_list = scrape_for_caps(body)
    if caps_list:
        ticker_list = check_ticker(caps_list)
        if ticker_list:
            for ticker in ticker_list:
                print(ticker)
