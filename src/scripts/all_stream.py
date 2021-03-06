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
from argparse import ArgumentParser
from praw import Reddit
from utils.ignore import DEFAULT_IGNORE_LIST
from utils.common import check_ticker, get_sentiment, scrape_for_caps


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
        description="""all_stream.py streams one or more subreddits' comments.
        Add --filter option for filtering for specific words in the comment body.
        Additional options available"""
    )

    arg_parser.add_argument(
        "subreddits", nargs="*", help="Subreddit(s) to pull comment stream from.",
    )

    arg_parser.add_argument(
        "-f",
        "--filter",
        nargs="*",
        default=None,
        help="Optional flag to filter for specific text in comment body. Default=None",
    )

    arg_parser.add_argument(
        "-S",
        "--stocks",
        action="store_true",
        default=False,
        help="Optional flag to display stock information found in the comment. Default=False",
    )

    arg_parser.add_argument(
        "-l",
        "--link",
        action="store_true",
        default=False,
        help="Optional flag to display comment url in the stream. Default=False",
    )

    arg_parser.add_argument(
        "-s",
        "--sentiment",
        action="store_true",
        default=False,
        help="Optional flag to display comment sentiment (experimental). Default=False",
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
    sub_string = "+".join(parsed.subreddits)
    logger_string = "r/" + ", r/".join(parsed.subreddits) + " ..."

    logger.info("Starting stream for: %s", logger_string)
    stream = (
        Reddit(
            client_id="vRhMbe_s-60osQ",
            client_secret="cY4m1vwXkv9p0p3Lyz-4RM3-CrA",
            user_agent="extraction by /u/willfullytr",
        )
        .subreddit(sub_string)
        .stream.comments(skip_existing=True)
    )

    if parsed.link:
        logger.info("link flag set: will provide links in printout")

    if parsed.sentiment:
        logger.info("Sentiment flag set: comment sentiment will be interpreted (experimental)")

    logger.info("Filter for words: %s", parsed.filter)
    for comment in stream:

        if parsed.filter is not None:
            comment_body = re.findall("(\S+)", re.sub("([^\w\s]+$)", "", str(comment.body).lower()))

            if any(str(word).lower() in comment_body for word in parsed.filter):
                logger.debug("Submission: %s", comment.submission.title)
                logger.debug("Subreddit: %s", comment.subreddit)

                print(
                    "\n-----{}-----\n[{}] Comment by: /u/{} in /r/{}\n{}\n".format(
                        comment.submission.title,
                        datetime.now(),
                        comment.author,
                        comment.subreddit,
                        comment.body,
                    )
                )
                found = True
            else:
                found = False
        else:
            logger.debug(comment)
            logger.debug("Submission: %s", comment.submission.title)
            logger.debug("Subreddit: %s", comment.subreddit)

            print(
                "\n-----{}-----\n[{}] Comment by: /u/{} in /r/{}\n{}\n".format(
                    comment.submission.title,
                    datetime.now(),
                    comment.author,
                    comment.subreddit,
                    comment.body,
                )
            )
            found = True

        if parsed.link and found:
            comment_link = "www.reddit.com" + comment.permalink
            print("URL: {}\n".format(comment_link))

        if parsed.sentiment and found:
            print("Sentiment:\n{}\n".format(get_sentiment(comment.body)))

        if parsed.stocks and found:
            caps_list = scrape_for_caps(comment.body)
            logger.debug(caps_list)

            if caps_list:
                ticker_list = check_ticker(caps_list, DEFAULT_IGNORE_LIST)
                logger.debug(ticker_list)

                if ticker_list:
                    print("Stocks Found:")
                    for ticker in list(set(ticker_list)):
                        print("[{}] {}".format(ticker, symbols[ticker]))


if __name__ == "__main__":
    main()
