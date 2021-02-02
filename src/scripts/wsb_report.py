"""
wsb_scraper.py

Date Created: March 9th, 2020

Author: georgefahmy

Description: Generate a report for stock mentions and the number of occurrences in
    /r/wallstreetbets. Options allow for different types of filters and thresholds.

"""


# Base Python #
import json
import logging
import os
import re
import sys

from argparse import ArgumentParser
from collections import Counter
from datetime import datetime
from tqdm import tqdm as bar

# Extended Python #
from pathlib import Path
from praw import Reddit
from pprint import pprint
from utils.common import check_ticker, get_sentiment, scrape_for_caps

# Logger
logger = logging.getLogger(__name__)
LOGGER_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"
TICKERS = Path("tickers.txt").resolve()
IGNORE_FILE = "src/utils/ignore.json"

# Arg Parser setup #
def get_arg_parser():
    """
    """

    arg_parser = ArgumentParser(
        description="""Generate a report for stock mentions and the number of occurrences
            in /r/wallstreetbets. Options allow for different types of filters and thresholds. """
    )

    arg_parser.add_argument(
        "type",
        help="""Choose which submissions to search: top, hot or new, If top, --type-flag is
            an optional flag to choose day, week, month, year, all""",
        choices=["top", "hot", "new"],
    )

    arg_parser.add_argument(
        "-f",
        "--type-flag",
        default="day",
        choices=["hour", "day", "week", "month"],
        help="enter the type of sorting for 'top': 'hour, day, week, month'",
    )

    arg_parser.add_argument(
        "--submissions", default=10, help="Enter the number of submissions to scrape", type=int,
    )

    arg_parser.add_argument(
        "-c",
        "--comments",
        default=10,
        help="Enter the limit for how many comment pages to scrape. Default=10",
        type=int,
    )

    arg_parser.add_argument(
        "-p",
        "--print",
        default=10,
        help="Limit the number of stocks printed after scraping. Default=5",
        type=int,
    )

    arg_parser.add_argument(
        "--sub-score",
        default=5,
        help="Minimum submission score to include in analysis. Default=5",
        type=int,
    )

    arg_parser.add_argument(
        "--com-score",
        default=5,
        help="Minimum comment score to include in analysis. Default=5",
        type=int,
    )

    arg_parser.add_argument(
        "-i", "--ignore", nargs="*", type=str.upper, help="List of stock symbols to ignore",
    )

    arg_parser.add_argument(
        "-d",
        "--display_dict",
        default=False,
        action="store_true",
        help="Option to display dictionary of all stocks found. Default=False",
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


# Generate Tickers dictionary
symbols = {}
for line in [line.rstrip("\n") for line in open(TICKERS)]:
    symbols[line.split("|")[0]] = line.split("|")[1]

with open(IGNORE_FILE, "r") as fp:
    ignore_list_json = json.load(fp)

ignore_list = list(set(ignore_list_json["DEFAULT_IGNORE_LIST"]))


def find_stocks(wall_street_bets, parsed):
    count_list = []

    if parsed.ignore:
        with open(IGNORE_FILE, "w+") as fp:
            ignore_list.extend(parsed.ignore)
            ignore_list_json["DEFAULT_IGNORE_LIST"] = sorted(list(set(ignore_list)))
            json.dump(ignore_list_json, fp, indent=4)

    logger.debug(ignore_list)

    wsb_ticker_list = {}
    sub_counter = 1
    for submission in wall_street_bets:

        logger.info("New Submission %d: %s", sub_counter, submission.title)
        sub_counter += 1
        logger.info("%d total comments found", len(submission.comments.list()))

        if submission.score > parsed.sub_score:
            caps_list = scrape_for_caps(submission.selftext)

            if caps_list:
                ticker_list = check_ticker(caps_list, ignore_list)
                if ticker_list:
                    for ticker in ticker_list:
                        count_list.append(ticker)
                        wsb_ticker_list[ticker] = symbols[ticker]
            try:
                submission.comments.replace_more(limit=parsed.comments)
                comment_stocks = []
                filtered_comments = 0
                for comment in submission.comments.list():
                    logger.debug(comment.author)
                    if comment.author == "AutoModerator":
                        logger.debug("Skipping AutoModerator")
                        continue

                    if comment.score > parsed.com_score:
                        filtered_comments += 1
                        caps_list = scrape_for_caps(comment.body)
                        if caps_list:
                            ticker_list = check_ticker(caps_list, ignore_list)
                            if ticker_list:
                                logger.debug(get_sentiment(comment.body))
                                for ticker in ticker_list:
                                    comment_stocks.append(ticker)
                                    count_list.append(ticker)
                                    wsb_ticker_list[ticker] = symbols[ticker]
            except Exception as e:
                logger.error(e)
                continue

            logger.info("Comments above score threshold: %d", filtered_comments)
            logger.info("Stocks found in comments: %d", len(comment_stocks))

        else:
            logger.warning("Submission below score threshold! Skipping")

    logger.info("Done!")
    logger.info("Total number unique stocks: %d", len(wsb_ticker_list))

    return wsb_ticker_list, Counter(count_list)


def print_top_count(wsb_ticker_list, frequency, parsed):

    top_stocks = frequency.most_common(parsed.print)
    if parsed.type == "top":
        top_string = " for the {},".format(str(parsed.type_flag).lower())
    else:
        top_string = ""

    print(
        "\nConfiguration: Sorting {} {} submissions{} with comment depth of {} pages. \
        Minimum submission score: {}. Minimum comment score: {}".format(
            parsed.submissions,
            str(parsed.type).capitalize(),
            top_string,
            parsed.comments,
            parsed.sub_score,
            parsed.com_score,
        )
    )
    print("\nTop {} talked about stocks:".format(min([parsed.print, len(wsb_ticker_list)])))

    for i in range(min([parsed.print, len(wsb_ticker_list)])):
        print(
            "[{}] - {}: {} occurances".format(
                str(top_stocks[i][0]),
                str(wsb_ticker_list[top_stocks[i][0]]),
                str(top_stocks[i][1]),
            )
        )


def main(*args):
    start = datetime.now()
    parsed = parse_args(args)

    if parsed.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOGGER_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(handler)

    if str(parsed.type).lower() == "top":
        logger.info("Top %d submissions for the %s:", parsed.submissions, parsed.type_flag)

        wall_street_bets = (
            Reddit(
                client_id="vRhMbe_s-60osQ",
                client_secret="cY4m1vwXkv9p0p3Lyz-4RM3-CrA",
                user_agent="extraction by /u/willfullytr",
            )
            .subreddit("wallstreetbets")
            .top(str(parsed.type_flag).lower(), limit=parsed.submissions)
        )

    elif str(parsed.type).lower() == "hot":
        logger.info("Hot %d submissions:", parsed.submissions)

        wall_street_bets = (
            Reddit(
                client_id="vRhMbe_s-60osQ",
                client_secret="cY4m1vwXkv9p0p3Lyz-4RM3-CrA",
                user_agent="extraction by /u/willfullytr",
            )
            .subreddit("wallstreetbets")
            .hot(limit=parsed.submissions)
        )

    elif str(parsed.type).lower() == "new":
        logger.info("%d new submissions:", parsed.submissions)

        wall_street_bets = (
            Reddit(
                client_id="vRhMbe_s-60osQ",
                client_secret="cY4m1vwXkv9p0p3Lyz-4RM3-CrA",
                user_agent="extraction by /u/willfullytr",
            )
            .subreddit("wallstreetbets")
            .new(limit=parsed.submissions)
        )

    wsb_ticker_list, frequency = find_stocks(wall_street_bets, parsed)

    print_top_count(wsb_ticker_list, frequency, parsed)

    if parsed.display_dict:
        print("\nFull List of stocks found:")
        pprint(wsb_ticker_list)

        # logger.warning("Invalid type selected")
    logger.info("Program executed in: {}".format(datetime.now() - start))


if __name__ == "__main__":
    main()
