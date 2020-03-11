import datetime
import logging
import re

from praw import Reddit
from pprint import pprint
from textblob import TextBlob
from utils.ignore import DEFAULT_IGNORE_LIST


# Logger
logger = logging.getLogger(__name__)

LOGGER_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"

logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(LOGGER_FORMAT, datefmt=DATE_FORMAT))
logger.addHandler(handler)


# Stream Setup
stream = (
    Reddit("wsb1", user_agent="extraction by /u/willfullytr")
    .subreddit("wallstreetbets")
    .stream.comments()
)


def get_sentiment(text):
    clean_text = " ".join(
        re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split()
    )
    analysis = TextBlob(clean_text)
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity == 0:
        return "neutral"
    else:
        return "negative"


def check_ticker(caps_list, ignore_list):
    ticker_list = []
    for word in caps_list:
        if word in ignore_list:
            continue
        if word in symbols.keys():
            logger.debug("Valid stock symbol found: %s", word)
            ticker_list.append(word)

    return ticker_list


def scrape_for_caps(string):
    REGEX_STRING = "(^[A-Z]+$|^[A-Z]+[\-][A-Z]?$|^[A-Z]+[\.][A-Z]?$|^[$][A-Z]+$)"
    words = re.findall("(\w+)", string)
    if words:
        caps_list = []
        for word in words:
            if len(word) < 5:
                if not word.istitle():
                    caps = re.findall(REGEX_STRING, word)
                    if caps:
                        caps_list.append(caps[0])

        return caps_list


# Generate Tickers dictionary
symbols = {}
for line in [line.rstrip("\n") for line in open("tickers.txt")]:
    symbols[line.split("|")[0]] = line.split("|")[1]

for comment in stream:

    caps_list = scrape_for_caps(comment.body)
    if caps_list:
        ticker_list = check_ticker(caps_list, DEFAULT_IGNORE_LIST)
        if ticker_list:
            print(
                "-----{}-----\n[{}] {}: {}".format(
                    comment.submission.title, datetime.datetime.now(), comment.author, comment.body
                )
            )
            print("\nSentiment:\n{}\n".format(get_sentiment(comment.body)))
            print("Stocks Found:")
            for ticker in list(set(ticker_list)):
                print("[{}] {}".format(ticker, symbols[ticker]))
            print("\n")
