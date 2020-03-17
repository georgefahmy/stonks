"""
streamer.py

Date Created: March 9th, 2020

Author: georgefahmy

Description: Reddit WallStreetBets stream with stock extraction from comments. Includes comment
    sentiment as well as links to the comment URL. Stock symbol extraction can also be used to
    automate retrieving stock price information.

"""


# Base Python #
import logging
import os
import pytz
import re
import sys


from datetime import datetime
from pprint import pprint

# Extended Python #
import yahoo_fin.stock_info as si
import yahoo_fin.options as oi

from argparse import ArgumentParser
from praw import Reddit
from textblob import TextBlob
from utils.ignore import DEFAULT_IGNORE_LIST


# Logger
logger = logging.getLogger(__name__)

LOGGER_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"

# Generate Tickers dictionary
logger.info("generating Symbols list")
symbols = {}
for line in [line.rstrip("\n") for line in open("tickers.txt")]:
    symbols[line.split("|")[0]] = line.split("|")[1]


def get_arg_parser():
    """
    Gets arguments for stock scraping.
    """

    arg_parser = ArgumentParser(
        description="""Reddit WallStreetBets stream with stock extraction
        from comments. Includes comment sentiment as well as links to the comment URL. Stock symbol
        extraction can also be used to automate retrieving stock price information."""
    )

    arg_parser.add_argument(
        "-l",
        "--link",
        action="store_true",
        default=False,
        help="optional flag to display comment permalink in the stream. Default=False",
    )

    arg_parser.add_argument(
        "-s",
        "--sentiment",
        action="store_true",
        default=False,
        help="Optional flag to display comment sentiment (experimental). Default=False",
    )

    arg_parser.add_argument(
        "-m",
        "--multi",
        action="store_true",
        default=False,
        help="Optional flag to stream from r/wallstreetbets, r/wsb, r/investing. Default=False",
    )

    arg_parser.add_argument(
        "--debug", default=False, action="store_true", help="Displays debug messages in console",
    )

    return arg_parser


def parse_args(args):
    parser = get_arg_parser()

    if not args:
        args = sys.argv[1:]

    return parser.parse_args(args)


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


def scrape_for_caps(string):
    REGEX_STRING = "(^[A-Z]+$|^[A-Z]+[\-][A-Z]?$|^[A-Z]+[\.][A-Z]?$|^[$][A-Z]+$)"
    words = re.findall("(\S+)", string)
    if words:
        caps_list = []
        for word in words:
            word = re.sub("([^\w\s]+$)", "", word)
            if len(word) < 5:
                if not word.istitle():
                    caps = re.findall(REGEX_STRING, word)
                    if caps:
                        caps_list.append(caps[0])

        return caps_list


def check_ticker(caps_list, ignore_list):
    ticker_list = []
    for word in caps_list:
        if word in ignore_list:
            continue
        if word in symbols.keys():
            logger.debug("Valid stock symbol found: %s", word)
            ticker_list.append(word)

    return ticker_list


def main(*args):

    parsed = parse_args(args)

    if parsed.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOGGER_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(handler)

    # Stream Setup

    if parsed.multi:
        subreddits = ["wallstreetbets", "wsb", "investing"]
        sub_string = "+".join(subreddits)
        logger_string = "r/" + ", r/".join(subreddits) + " ..."

        logger.info("Starting multireddit stream for: %s", logger_string)
        stream = (
            Reddit("wsb1", user_agent="extraction by /u/willfullytr")
            .subreddit(sub_string)
            .stream.comments(skip_existing=True)
        )

    else:
        logger.info("Getting WallStreetBets comments stream...")
        stream = (
            Reddit("wsb1", user_agent="extraction by /u/willfullytr")
            .subreddit("wallstreetbets")
            .stream.comments(skip_existing=True)
        )

    if parsed.link:
        logger.info("link flag set: will provide links in printout")

    if parsed.sentiment:
        logger.info("Sentiment flag set: comment sentiment will be interpreted (experimental)")

    logger.info("Starting stream!")

    for comment in stream:
        logger.debug(comment)
        caps_list = scrape_for_caps(comment.body)
        logger.debug(caps_list)
        if caps_list:
            ticker_list = check_ticker(caps_list, DEFAULT_IGNORE_LIST)
            logger.debug(ticker_list)
            if ticker_list:

                print(
                    "\n-----{}-----\n[{}] Comment by: /u/{} in /r/{}\n{}\n".format(
                        comment.submission.title,
                        datetime.now(),
                        comment.author,
                        comment.subreddit,
                        comment.body,
                    )
                )
                print("Stocks Found:")
                for ticker in list(set(ticker_list)):
                    ticker_price = round(si.get_live_price(ticker), 3)
                    print(
                        "[{}] {}\nCurrent Price: ${}".format(ticker, symbols[ticker], ticker_price)
                    )

                if parsed.sentiment:
                    print("\nComment sentiment: {}".format(get_sentiment(comment.body)))

                if parsed.link:
                    comment_link = "www.reddit.com" + comment.permalink
                    print("\nURL: {}\n".format(comment_link))

    # TODO add check for volume of options purchased, open interest to check trends of stock interest.
    # TODO add a check for puts or calls (puts, calls, p, c) in the comment to help with sentiment.
    # TODO add comparison for stock prices current vs yesterday vs history patterns, or other interesting comparisons.


if __name__ == "__main__":
    main()
