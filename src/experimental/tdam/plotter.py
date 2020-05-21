import numpy as np

from pprint import pprint
from matplotlib import pyplot as plt, rcParams, ticker

from datetime import timedelta

SEC_PER_HOUR = 3600
DEFAULT_HOURS_TO_DISPLAY = 0.5

FIG_WIDTH = 6.36
STD_FIG_HEIGHT = 5
PRICE_WIDTH = 6.36
PRICE_HEIGHT = 2.45


def detailed_plotter(
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
    percent_change="",
    target=None,
    xlabel=None,
    label1=None,
    label2=None,
    label3=None,
    label4=None,
    color1=None,
    color2=None,
    color3=None,
    color4=None,
    fig_size=None,
    limit=True,
    live=True,
    delay=None,
    hours=None,
    pause_time=0.1,
):
    plt.style.use("ggplot")
    plt.ion()
    if live:
        rcParams["toolbar"] = "None"

    if fig_size is None:
        fig_width = FIG_WIDTH
        fig_height = STD_FIG_HEIGHT
    else:
        fig_width = fig_size[0]
        fig_height = fig_size[1]

    if delay is None:
        delay = 60
    else:
        delay = float(delay)

    if hours is None:
        seconds_to_limit = SEC_PER_HOUR * DEFAULT_HOURS_TO_DISPLAY
    else:
        seconds_to_limit = SEC_PER_HOUR * hours

    if line1 == []:
        # this is the call to matplotlib that allows dynamic plotting
        fig, axs = plt.subplots(3, figsize=(FIG_WIDTH, STD_FIG_HEIGHT))

        # create a variable for the line so we can later update it
        diffs = axs[0]
        diffs.margins(x=1)
        diffs.get_shared_x_axes().join(axs[0], axs[1], axs[2])
        totals = axs[1]
        totals2 = totals.twinx()  # two y axes on the second subplot
        price = axs[2]
        volume = price.twinx()
        width = timedelta(seconds=delay / 2.5)
        volume_width = timedelta(seconds=(delay * 0.9))

        (line1,) = diffs.bar(
            np.array(x_data), y1_data, width, align="edge", color=color1, alpha=0.8, label=label1
        )
        (line2,) = diffs.bar(
            np.array(x_data), y2_data, -width, align="edge", color=color2, alpha=0.8, label=label2
        )
        (line3,) = totals.plot(x_data, y3_data, color=color1, alpha=0.8)
        (line4,) = totals2.plot(x_data, y4_data, color=color2, alpha=0.8)
        (line5,) = price.plot(x_data, np.round(y5_data, 3), color=color3, alpha=0.8, label="Price")
        (line6,) = volume.bar(
            x_data, y6_data, volume_width, color="black", alpha=0.2, label="Volume"
        )

        if target:
            line5.axes.axhline(target, 0, 1, color=color4, linestyle="dashed", label="Target")

        # update plot label/title
        diffs.set_ylabel("Volume", fontsize=10)
        diffs.tick_params(axis="y", labelsize=8)
        diffs.set_xticklabels([])
        diffs.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))

        # diffs.set_yscale("log")

        totals.set_ylabel("Total Calls", fontsize=10)
        totals.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
        totals.set_yticks(np.linspace(totals.get_ybound()[0], totals.get_ybound()[1], 5))
        totals.tick_params(axis="y", labelsize=8)

        totals2.grid(None)
        totals2.set_ylabel("Total Puts", fontsize=10)
        totals2.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
        totals2.set_yticks(np.linspace(totals2.get_ybound()[0], totals2.get_ybound()[1], 5))
        totals2.tick_params(axis="y", labelsize=8)

        price.set_ylabel("Stock Price", fontsize=10)
        price.set_xlabel("Time of Day", fontsize=10)
        price.tick_params(axis="both", labelsize=8)
        price.get_yaxis().get_major_formatter().set_useOffset(False)
        price.get_yaxis().set_major_formatter(ticker.FormatStrFormatter("$%1.2f"))

        volume.grid(None)
        volume.tick_params(axis="y", labelsize=7)
        volume.set_ylabel("Volume", fontsize=10)
        volume.set_yticks(np.linspace(0, volume.get_ylim()[1] + 1, 5))

        fig.autofmt_xdate()
        fig.legend(loc="upper right", fontsize=7)
        plt.autoscale(axis="y", tight=True)
        fig.tight_layout(pad=1.0, h_pad=2.0)
        fig.subplots_adjust(top=1.2)
        if live:
            plt.show()
        else:
            plt.show(block=True)
    # createe list of tuple information for use in for loops later
    # line, y_data, color, calls
    bar_list = [
        (line1, y1_data, color1, True),
        (line2, y2_data, color2, False),
    ]
    # line, y_data, color label, title info, bar
    line_data_list = [
        (line3, y3_data, True, True, False),
        (line4, y4_data, True, False, False),
        (line5, y5_data, False, False, False),
        (line6, y6_data, False, False, True),
    ]
    plt.suptitle(
        "{} ({}): ${} ({}%)".format(
            stock_name, symbol, np.round(y5_data[-1], 3), round(percent_change, 2)
        ),
        fontsize=10,
        y=0.98,
    )
    plt.tight_layout(pad=1.0, h_pad=2.0)
    plt.subplots_adjust(top=0.925)

    # line3.axes.set_title(
    #     "Total Call Volume: {:,} - Total Put Volume: {:,}".format(y3_data[-1], y4_data[-1]),
    #     fontsize=9,
    # )

    # after the figure, axis, and line are created, we need to update the y-data
    for line, data, color, calls in bar_list:
        width = timedelta(seconds=(delay / 2.5))
        if limit:
            num_values_to_keep = int(seconds_to_limit / delay)
            x_data = x_data[-num_values_to_keep:]
            data = data[-num_values_to_keep:]

        if calls:
            line.axes.clear()
            line.axes.set_ylabel("Volume", fontsize=10)
            line.axes.set_xticklabels([])
            line.axes.bar(
                x_data, data, -width, align="edge", color=color, alpha=0.8, label=label1,
            )
            line.axes.autoscale_view(scalex=True)

        else:

            line.axes.set_xticklabels([])
            line.axes.bar(
                x_data, data, width, align="edge", color=color, alpha=0.8, label=label1,
            )
            line.axes.autoscale_view(scalex=True)

    for line, data, total, title, bar in line_data_list:
        if limit:

            num_values_to_keep = int(seconds_to_limit / delay)
            x_data = x_data[-num_values_to_keep:]
            data = data[-num_values_to_keep:]

        if not bar:
            line.set_data(x_data, data)
            line.axes.relim()
            line.axes.autoscale_view(scalex=True)

            # adjust limits if new data goes beyond bounds
            if np.min(data) <= line.axes.get_ylim()[0] or np.max(data) >= line.axes.get_ylim()[1]:
                if np.min(data) == np.max(data):
                    plt.ylim([np.min(data) - 1, np.max(data) + 1])
                    if total:
                        line.axes.set_yticks(
                            np.linspace(line.axes.get_ybound()[0], line.axes.get_ybound()[1], 5)
                        )
                else:
                    plt.ylim([np.min(data) - np.std(data), np.max(data) + np.std(data)])
                    if total:
                        line.axes.set_yticks(
                            np.linspace(line.axes.get_ybound()[0], line.axes.get_ybound()[1], 5)
                        )

        if title:
            line.axes.set_title(
                "Total Call Volume: {:,} - Total Put Volume: {:,}".format(y3_data[-1], y4_data[-1]),
                fontsize=9,
            )
        if total:
            line.axes.set_yticks(
                np.linspace(line.axes.get_ybound()[0], line.axes.get_ybound()[1], 5)
            )

        if bar:
            volume = line.axes
            volume_width = timedelta(seconds=(delay * 0.95))
            volume.cla()
            volume.set_ylim(bottom=0)
            volume.set_ylabel("Volume", fontsize=10)
            volume.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
            volume.bar(
                x_data, data, volume_width, color="black", alpha=0.2, label="Volume",
            )
            volume.set_yticks(np.linspace(0, line6.axes.get_ylim()[1] + 1, 5))
            volume.grid(None)

            if np.max(data) >= volume.get_ylim()[1]:
                volume.set_ylim([0, np.max(data) + np.std(data)])
                volume.set_yticks(np.linspace(0, volume.get_ylim()[1] + 1, 5))

            else:
                if np.min(data) == np.max(data):
                    volume.set_ylim([0, np.max(data) + 1])
                    volume.set_yticks(np.linspace(0, volume.get_ylim()[1] + 1, 5))

                else:
                    volume.set_ylim([0, np.max(data) + np.std(data)])
                    volume.set_yticks(np.linspace(0, volume.get_ylim()[1] + 1, 5))

    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    if not live:
        rcParams["toolbar"] = "toolbar2"
        plt.show(block=True)

    # return line so we can update it again in the next iteration
    return (line1, line2, line3, line4, line5, line6)


def price_plotter(
    tdclient,
    symbol,
    stock_name,
    x_data,
    line5,
    line6,
    price_data,
    volume_data,
    percent_change="",
    target=None,
    xlabel="Time of Day",
    label="Price",
    color="k",
    pause_time=0.5,
    limit=True,
    fig_size=None,
    live=True,
    delay=None,
    hours=None,
):
    plt.style.use("ggplot")
    plt.ion()
    rcParams["toolbar"] = "None"
    width = timedelta(seconds=(delay * 0.95))
    if fig_size is None:
        fig_width = PRICE_WIDTH
        fig_height = PRICE_HEIGHT
    else:
        fig_width = fig_size[0]
        fig_height = fig_size[1]

    if percent_change is None:
        percent_change = ""
    else:
        percent_change = round(percent_change, 2)

    if delay is None:
        delay = 60
    else:
        delay = float(delay)

    if hours is None:
        seconds_to_limit = SEC_PER_HOUR * DEFAULT_HOURS_TO_DISPLAY
    else:
        seconds_to_limit = SEC_PER_HOUR * hours

    if line5 == []:
        # this is the call to matplotlib that allows dynamic plotting
        fig, price = plt.subplots(1, figsize=(PRICE_WIDTH, PRICE_HEIGHT))
        volume = price.twinx()
        # create a variable for the line so we can later update it
        (line5,) = price.plot(
            x_data, np.round(price_data, 2), color=color, alpha=0.8, label="Price"
        )
        (line6,) = volume.bar(x_data, volume_data, width, color="black", alpha=0.2, label="Volume")

        if target:
            line5.axes.axhline(target, 0, 1, color="b", linestyle="dashed", label="Target")

        # update plot and ax label/title
        price.set_ylabel("Stock Price", fontsize=9)
        price.set_xlabel(xlabel, fontsize=8)
        price.tick_params(axis="y", labelsize=7)
        price.tick_params(axis="x", labelsize=7)
        price.get_yaxis().get_major_formatter().set_useOffset(False)
        price.set_yticks(np.linspace(price.get_ybound()[0], price.get_ybound()[1], 5))

        volume.tick_params(axis="y", labelsize=7)
        volume.set_yticks(np.linspace(0, volume.get_ylim()[1] + 1, 5))

        price.set_title(
            "{} ({}) - ${} ({}%)".format(
                stock_name, symbol, round(price_data[-1], 3), percent_change
            ),
            fontsize=9,
        )
        plt.gca().autoscale(axis="x", tight=True)
        ax = plt.gca()
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        fig.autofmt_xdate()
        fig.tight_layout()

        if live:
            plt.show()
        else:
            plt.show(block=True)

    line5.axes.set_title(
        "{} ({}) - ${} ({}%)".format(stock_name, symbol, round(price_data[-1], 3), percent_change),
        fontsize=9,
    )
    # after the figure, axis, and line are created, we need to update the y-data
    if limit:
        num_values_to_keep = int(seconds_to_limit / int(delay))
        x_data = x_data[-num_values_to_keep:]
        price_data = price_data[-num_values_to_keep:]
        volume_data = volume_data[-num_values_to_keep:]

    price = line5.axes
    volume = line6.axes
    line5.set_data(x_data, np.round(price_data, 2))

    price.relim()
    price.autoscale_view(scalex=True)
    price.get_yaxis().set_major_formatter(ticker.FormatStrFormatter("$%1.2f"))
    price.set_yticks(np.linspace(round(price.get_ylim()[0], 2), round(price.get_ylim()[1], 2), 5))

    width = timedelta(seconds=(delay * 0.95))
    volume.cla()
    volume.set_ylim(bottom=0)
    volume.set_ylabel("Volume", fontsize=10)
    volume.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
    volume.bar(x_data, volume_data, width, color="black", alpha=0.2, label="Volume")
    volume.set_yticks(np.linspace(0, line6.axes.get_ylim()[1] + 1, 5))
    volume.grid(None)

    # adjust limits if new data goes beyond bounds
    if np.min(price_data) <= price.get_ylim()[0] or np.max(price_data) >= price.get_ylim()[1]:
        if np.min(price_data) == np.max(price_data):
            price.set_ylim([np.min(price_data) - 1, np.max(price_data) + 1])
            price.set_yticks(
                np.linspace(round(price.get_ylim()[0], 2), round(price.get_ylim()[1], 2), 5)
            )

        else:
            price.set_ylim(
                [np.min(price_data) - np.std(price_data), np.max(price_data) + np.std(price_data)]
            )
            price.set_yticks(
                np.linspace(round(price.get_ylim()[0], 2), round(price.get_ylim()[1], 2), 5)
            )

    if np.max(volume_data) >= volume.get_ylim()[1]:
        volume.set_ylim([0, np.max(volume_data) + np.std(volume_data)])
        volume.set_yticks(np.linspace(0, volume.get_ylim()[1] + 1, 5))

    else:
        if np.min(volume_data) == np.max(volume_data):
            volume.set_ylim([0, np.max(volume_data) + 1])
            volume.set_yticks(np.linspace(0, volume.get_ylim()[1] + 1, 5))

        else:
            volume.set_ylim([0, np.max(volume_data) + np.std(volume_data)])
            volume.set_yticks(np.linspace(0, volume.get_ylim()[1] + 1, 5))

    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered abovef
    plt.tight_layout(pad=1.0, h_pad=2.0)
    plt.pause(pause_time)
    if not live:
        plt.rcParams["toolbar"] = "toolbar2"
        plt.show(block=True)

    # return line so we can update it again in the next iteration
    return (line5, line6)
