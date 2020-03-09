"""
my_stocks.py

Date Created: February 27th, 2020

Author: georgefahmy

Description: This script reports what stocks and options are currently held.

"""


# Base Python #
import logging
import os
import sys

from pprint import pprint

# Extended Python #
import robin_stocks

username = "geofahm"
password = "S8A-ddV-GTU-vNp"

robin_stocks.login(username, password, by_sms=True, store_session=True)

my_stocks = robin_stocks.build_holdings()
