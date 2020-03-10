import logging
import os
import re
import sys

from argparse import ArgumentParser
from collections import Counter
from praw import Reddit
from pprint import pprint
from textblob import TextBlob

# Logger
logger = logging.getLogger(__name__)
LOGGER_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"

# DD is "Due Diligence", RH is "Robinhood", "WSB is wallstreetbets",
DEFAULT_IGNORE_LIST = [
    "DD",
    "RH",
    "USD",
    "ARE",
    "CL",
    "TD",
    "WSB",
    "PM",
    "YOLO",
    "IPO",
    "SUB",
    "EOD",
]

# Arg Parser setup #
def get_arg_parser():
    """
    Gets arguments for stock scraping.
    """

    arg_parser = ArgumentParser(description="Arguments for which stocks to scrape")

    arg_parser.add_argument(
        "type", help="Choose which submissions to search: top for the day, hot or new",
    )

    arg_parser.add_argument(
        "--type-flag",
        default="day",
        help="enter the type of sorting for 'Top': 'day, week, month'",
    )

    arg_parser.add_argument(
        "--submissions", default=10, help="Enter the number of submissions to scrape", type=int,
    )

    arg_parser.add_argument(
        "-c",
        "--comments",
        default=100,
        help="Enter the limit for how many comment pages to scrape. Default=None",
        type=int,
    )

    arg_parser.add_argument(
        "-p",
        "--print",
        default=3,
        help="Limit the number of stocks printed after scraping. Default=5",
        type=int,
    )

    arg_parser.add_argument(
        "-s",
        "--score",
        default=5,
        help="Minimum comment score to include in analysis. Default=20",
        type=int,
    )

    arg_parser.add_argument(
        "-i", "--ignore", nargs="*", help="List of stock symbols to ignore",
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
for line in [line.rstrip("\n") for line in open("tickers.txt")]:
    symbols[line.split("|")[0]] = line.split("|")[1]


# CAPS Scraper
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


def check_ticker(caps_list, ignore_list):
    ticker_list = []
    for word in caps_list:
        if word in ignore_list:
            continue
        if word in symbols.keys():
            logger.debug("Valid stock symbol found: %s", word)
            ticker_list.append(word)

    return ticker_list


def print_top_count(wsb_ticker_list, frequency, parsed):

    top_stocks = frequency.most_common(parsed.print)
    if parsed.type == "day":
        top_string = " for the {},".format(str(parsed.type_flag).lower())
    else:
        top_string = ""

    print(
        "\nConfiguration: Sorting {} {} submissions{} with comment depth of {} pages. Minimum comment score: {}".format(
            parsed.submissions,
            str(parsed.type).capitalize(),
            top_string,
            parsed.comments,
            parsed.score,
        )
    )
    print("\nTop {} talked about stocks:".format(parsed.print))

    for i in range(parsed.print):
        print(
            "[{}] - {}: {} occurances".format(
                str(top_stocks[i][0]),
                str(wsb_ticker_list[top_stocks[i][0]]),
                str(top_stocks[i][1]),
            )
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


def find_stocks(wall_street_bets, parsed):
    count_list = []
    if parsed.ignore:
        ignore_list = DEFAULT_IGNORE_LIST.extend(parsed.ignore)
    else:
        ignore_list = DEFAULT_IGNORE_LIST
    logger.debug(ignore_list)

    wsb_ticker_list = {}
    for submission in wall_street_bets:
        logger.info("New Submission: %s", submission.title)
        logger.info("%d comments found", len(submission.comments.list()))

        caps_list = scrape_for_caps(submission.selftext)

        if caps_list:
            ticker_list = check_ticker(caps_list, ignore_list)
            if ticker_list:
                for ticker in ticker_list:
                    count_list.append(ticker)
                    wsb_ticker_list[ticker] = symbols[ticker]

        submission.comments.replace_more(limit=parsed.comments)
        comment_stocks = []
        for comment in submission.comments.list():

            logger.debug(comment.author)
            if comment.author == "AutoModerator":
                logger.debug("Skipping AutoModerator")
                continue

            if comment.score > parsed.score:

                caps_list = scrape_for_caps(comment.body)
                if caps_list:
                    ticker_list = check_ticker(caps_list, ignore_list)
                    if ticker_list:
                        logger.debug(get_sentiment(comment.body))
                        for ticker in ticker_list:
                            comment_stocks.append(ticker)
                            count_list.append(ticker)
                            wsb_ticker_list[ticker] = symbols[ticker]

        logger.info("%d stocks found in comments", len(comment_stocks))

    logger.info("Total number unique stocks: %d", len(wsb_ticker_list))
    logger.info("Done!")

    return wsb_ticker_list, Counter(count_list)


def main(*args):

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
            Reddit("wsb1", user_agent="extraction by /u/willfullytr")
            .subreddit("wallstreetbets")
            .top(str(parsed.type_flag).lower(), limit=parsed.submissions)
        )

    elif str(parsed.type).lower() == "hot":
        logger.info("Hot %d submissions:", parsed.submissions)

        wall_street_bets = (
            Reddit("wsb1", user_agent="extraction by /u/willfullytr")
            .subreddit("wallstreetbets")
            .hot(limit=parsed.submissions)
        )

    elif str(parsed.type).lower() == "new":
        logger.info("%d new submissions:", parsed.submissions)

        wall_street_bets = (
            Reddit("wsb1", user_agent="extraction by /u/willfullytr")
            .subreddit("wallstreetbets")
            .new(limit=parsed.submissions)
        )

    wsb_ticker_list, frequency = find_stocks(wall_street_bets, parsed)

    print_top_count(wsb_ticker_list, frequency, parsed)

    if parsed.display_dict:
        print("\nFull List of stocks found:")
        pprint(wsb_ticker_list)

        # logger.warning("Invalid type selected")


if __name__ == "__main__":
    main()
