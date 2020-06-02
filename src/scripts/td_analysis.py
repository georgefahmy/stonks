# Base Python #
import logging
import os
import re
import sys
import select

from argparse import ArgumentParser
from datetime import datetime, timedelta
from pprint import pprint
from time import sleep

# Extended Python #
import pandas as pd
import numpy as np
import tdameritrade

from matplotlib import pyplot as plt, rcParams
from tdameritrade import auth, TDClient
from experimental.tdam.plotter import detailed_plotter, price_plotter
from experimental.tdam.scatter_plot import scatter_plot

# TODO Add multi threading. one thread to gather the data for a stock and store it in a DataFrame
# TODO a second thread to plot that data as it is being streamed
# TODO a third thread potentially to plot the full data set.

# REDIRECT_URI = "http://localhost:8080"
CLIENT_ID = os.getenv("TDAMERITRADE_CLIENT_ID")
REFRESH_TOKEN = os.getenv("TDAMERITRADE_REFRESH_TOKEN")

tdclient = TDClient(client_id=CLIENT_ID, refresh_token=REFRESH_TOKEN)


def get_arg_parser():
    """
    Gets arguments for stock scraping.
    """

    arg_parser = ArgumentParser(
        description="""Detailed analysis of stocks and options using the tdameritrade api."""
    )

    arg_parser.add_argument(
        "symbol", type=str.upper, help="Stock symbol to analyze",
    )

    arg_parser.add_argument(
        "-p",
        "--price-only",
        action="store_true",
        default=False,
        help="Only display the price and volume portion of the plots.",
    )

    arg_parser.add_argument(
        "-t", "--target", type=float, help="Plots a horizontal line at the target price.",
    )

    arg_parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=60,
        help="How often to update the plot. Default 60 seconds.",
    )

    arg_parser.add_argument(
        "-hh",
        "--hours",
        type=float,
        default=0.5,
        help="Optional flag for number of hours to limit the plot to display.",
    )

    arg_parser.add_argument(
        "-s",
        "--scatter",
        choices=["volume", "v", "interest", "i", "unusual", "u", "bidask", "b", "both"],
        default=None,
        help="Generates an instantanious snapshot of all option positions and volumes",
    )

    arg_parser.add_argument(
        "-l", "--limit", action="store_false", default=True, help="Dont limit the plotting window",
    )
    arg_parser.add_argument(
        "-w",
        "--window_size",
        type=float,
        nargs=2,
        default=None,
        help="provide optional window size for plots. width x height y",
    )

    return arg_parser


def parse_args(args):
    parser = get_arg_parser()

    if not args:
        args = sys.argv[1:]

    return parser.parse_args(args)


def td_plot(symbol, target, limit, price_only, delay, hours, scatter, window_size):
    first = True
    original_delay = delay

    # Initialize all the plot lists
    x_data = []  # dates
    y1_data = []  # call diff
    y2_data = []  # put diff
    y3_data = []  # call volume
    y4_data = []  # put volume
    y5_data = []  # price
    y6_data = []  # Stock Volume

    # Initialize the Lines for the plot
    line1 = []  # call diff line
    line2 = []  # Put diff line
    line3 = []  # Call volume line
    line4 = []  # Put volume line
    line5 = []  # Price Line
    line6 = []  # Volume Line
    line7 = []  # Moving Average of Price

    if scatter is not None:
        scatter_plot(tdclient, symbol, scatter)

    else:
        while True:
            iteration_start = datetime.now()
            try:
                options = tdclient.optionsDF(symbol)
                quote = tdclient.quoteDF(symbol)
                stock_name = quote["description"].values[0]

                if len(stock_name) >= 40:
                    stock_name = stock_name[:40]
            except:
                stock_name = symbol
                continue

            # Debug purposes
            if False:
                # pprint(options.head(1).to_dict())
                pprint(quote.head(1).to_dict())

            try:
                quote_timestamp = int(str(quote["quoteTimeInLong"].to_list()[0])[:-3])
                quote_date = datetime.fromtimestamp(quote_timestamp).replace(microsecond=0)
                if True:  # date == x_data[-1] or date < x_data[-1]:
                    # print("date is same as last quote")
                    date = datetime.now().replace(microsecond=0)
                time_diff = date - quote_date
                # print(date, quote_date, time_diff)
            except:
                date = datetime.now().replace(microsecond=0)

            x_data.append(date)

            price = quote["lastPrice"].values[0]
            volume = quote["totalVolume"].values[0]
            percent_change = quote["netPercentChangeInDouble"].values[0]

            calls = options[options["putCall"] == "CALL"]
            puts = options[options["putCall"] == "PUT"]

            call_volume = calls["totalVolume"].sum()
            put_volume = puts["totalVolume"].sum()

            if first:
                prev_calls = call_volume
                prev_puts = put_volume
                prev_volume = volume
                first = False

            call_diff = call_volume - prev_calls
            put_diff = put_volume - prev_puts
            volume_diff = volume - prev_volume

            prev_calls = call_volume
            prev_puts = put_volume
            prev_volume = volume

            y1_data.append(call_diff)
            y2_data.append(put_diff)
            y3_data.append(call_volume)
            y4_data.append(put_volume)
            y5_data.append(price)
            y6_data.append(volume_diff)

            iteration_duration = datetime.now() - iteration_start

            if delay < iteration_duration.total_seconds():
                delay = 2 * iteration_duration.total_seconds()
            else:
                delay = original_delay

            sleep(max([delay - iteration_duration.total_seconds(), 1]))

            if price_only:
                line5, line6 = price_plotter(
                    tdclient,
                    symbol,
                    stock_name,
                    x_data,
                    line5,
                    line6,
                    y5_data,
                    y6_data,
                    delay=delay,
                    hours=hours,
                    percent_change=percent_change,
                    fig_size=window_size,
                )
            else:
                line1, line2, line3, line4, line5, line6 = detailed_plotter(
                    tdclient,
                    symbol,
                    stock_name,
                    x_data,
                    line1,
                    line2,
                    line3,
                    line4,
                    line5,
                    line6,
                    y1_data,
                    y2_data,
                    y3_data,
                    y4_data,
                    y5_data,
                    y6_data,
                    percent_change=percent_change,
                    color1="g",
                    color2="r",
                    color3="k",
                    label1="Calls",
                    label2="Puts",
                    limit=limit,
                    target=target,
                    delay=delay,
                    hours=hours,
                    fig_size=window_size,
                )

            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line_data = (line1, line2, line3, line4, line5, line6)
                y_data = (y1_data, y2_data, y3_data, y4_data, y5_data, y6_data)
                line = input()
                print("Ending Live Plotter, displaying full data")
                keyboard_input = 1
                break

        if keyboard_input == 1:
            if price_only:
                price_plotter(
                    tdclient,
                    symbol,
                    stock_name,
                    x_data,
                    line_data[4],
                    line_data[5],
                    y_data[4],
                    y_data[5],
                    delay=delay,
                    limit=False,
                    fig_size=[8, 5],
                    live=False,
                    percent_change=percent_change,
                )
            else:
                detailed_plotter(
                    tdclient,
                    symbol,
                    stock_name,
                    x_data,
                    line_data[0],
                    line_data[1],
                    line_data[2],
                    line_data[3],
                    line_data[4],
                    line_data[5],
                    y_data[0],
                    y_data[1],
                    y_data[2],
                    y_data[3],
                    y_data[4],
                    y_data[5],
                    color1="g",
                    color2="r",
                    color3="k",
                    label1="Calls",
                    label2="Puts",
                    limit=False,
                    target=target,
                    delay=delay,
                    live=False,
                    percent_change=percent_change,
                )


def main(*args):
    args = parse_args(args)

    td_plot(
        args.symbol,
        args.target,
        args.limit,
        args.price_only,
        args.delay,
        args.hours,
        args.scatter,
        args.window_size,
    )


if __name__ == "__main__":
    main()
