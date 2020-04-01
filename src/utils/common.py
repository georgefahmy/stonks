"""
common.py

Date Created: April 1st, 2020

Author: georgefahmy

Description:

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
from pathlib import Path
from textblob import TextBlob

# Logger
logger = logging.getLogger(__name__)

LOGGER_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"
TICKERS = Path("tickers.txt").resolve()

if not os.path.isfile(TICKERS):
    os.system("get_symbols")

# Generate Tickers dictionary
logger.info("generating Symbols list")
symbols = {}
for line in [line.rstrip("\n") for line in open(TICKERS)]:
    symbols[line.split("|")[0]] = line.split("|")[1]


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
            word = re.sub("([^\w\s]+$|^[^\w\s]+)", "", word)
            if len(word) == 1:
                caps = re.findall(REGEX_STRING, word)
                if caps:
                    caps_list.append(caps[0])
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
