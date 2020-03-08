import logging
import re

from praw import Reddit
from pprint import pprint

# Logger
logger = logging.getLogger(__name__)

LOGGER_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"

logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(LOGGER_FORMAT, datefmt=DATE_FORMAT))
logger.addHandler(handler)


# Setup
wall_street_bets = (
    Reddit("wsb1", user_agent="extraction by /u/willfullytr")
    .subreddit("wallstreetbets")
    .top("day", limit=10)
)


# Generate Tickers dictionary
symbols = {}
for line in [line.rstrip("\n") for line in open("tickers.txt")]:
    symbols[line.split("|")[0]] = line.split("|")[1]


# CAPS Scraper
def scrape_for_caps(string):
    REGEX_STRING = "(^[A-Z]+\s|[A-Z]+$|^[A-Z]+[\-][A-Z]?|^[A-Z]+[\.][A-Z]?)"
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


def check_ticker(caps_list):
    ticker_list = []
    for word in caps_list:
        if word in symbols.keys():
            logger.info("Valid stock symbol found: %s", word)
            ticker_list.append(word)

    return ticker_list


def find_stocks():

    wsb_ticker_list = {}
    for submission in wall_street_bets:
        logger.info("New Submission: %s", submission.title)
        logger.info("%d comments found", len(submission.comments.list()))

        caps_list = scrape_for_caps(submission.selftext)
        if caps_list:
            ticker_list = check_ticker(caps_list)
            if ticker_list:
                for ticker in ticker_list:
                    wsb_ticker_list[ticker] = symbols[ticker]

        submission.comments.replace_more(limit=20)
        for comment in submission.comments.list():

            if comment.score > 20:
                body = comment.body
                caps_list = scrape_for_caps(body)
                if caps_list:
                    ticker_list = check_ticker(caps_list)
                    if ticker_list:
                        for ticker in ticker_list:
                            wsb_ticker_list[ticker] = symbols[ticker]

    logger.info("%d Stocks found", len(wsb_ticker_list))
    logger.info("Done!")
    return wsb_ticker_list


wsb_ticker_list = find_stocks()
pprint(wsb_ticker_list)
