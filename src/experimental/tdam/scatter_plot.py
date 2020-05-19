import numpy as np

from pprint import pprint
from matplotlib import pyplot as plt, rcParams


SEC_PER_HOUR = 3600
HOURS_TO_DISPLAY = 3
SECONDS_TO_LIMIT = SEC_PER_HOUR * HOURS_TO_DISPLAY

FIG_WIDTH = 6.33
STD_FIG_HEIGHT = 5


def scatter_plot(tdclient, symbol, scatter, fig_size=None):
    options = tdclient.optionsDF(symbol)
    quote = tdclient.quoteDF(symbol)

    # for debugging purposes
    if False:
        pprint(options.head(20).to_dict())
        # pprint(quote.head(1).to_dict())
        # print(quote["description"].values[0])
    if fig_size is None:
        fig_width = FIG_WIDTH
        fig_height = STD_FIG_HEIGHT
    else:
        fig_width = fig_size[0]
        fig_height = fig_size[1]

    # Realtime stock info, price, name, percent change from yesterday
    price = quote["lastPrice"].values[0]
    stock_name = quote["description"].values[0]
    percent_change = quote["netPercentChangeInDouble"].values[0]

    # Isolate call options
    call_options = options[options["putCall"] == "CALL"]
    call_dates = call_options["expirationDate"].to_numpy()
    call_volumes = call_options["totalVolume"].to_numpy()
    call_interest = call_options["openInterest"].to_numpy()
    call_strikes = call_options["strikePrice"].to_numpy()
    call_symbol = call_options["symbol"].to_numpy()

    # Isolate the put options
    put_options = options[options["putCall"] == "PUT"]
    put_dates = put_options["expirationDate"].to_numpy()
    put_volumes = put_options["totalVolume"].to_numpy()
    put_interest = put_options["openInterest"].to_numpy()
    put_strikes = put_options["strikePrice"].to_numpy()
    put_symbol = put_options["symbol"].to_numpy()

    try:
        if scatter == "interest" or scatter == "unusual":
            max_call_interest = max(call_interest)
            max_put_interest = max(put_interest)
            if max_call_interest == 0 or max_put_interest == 0:
                valid = False
            else:
                valid = True
        elif scatter == "volume":
            valid = True
    except:
        valid = False

    if valid:
        if scatter == "volume":
            max_norm = max([max(call_volumes), max(put_volumes)])
            call_markers = (
                (call_volumes - min(call_volumes)) / (max_norm - min(call_volumes))
            ) * 300
            put_markers = ((put_volumes - min(put_volumes)) / (max_norm - min(put_volumes))) * 300

            call_annotations = call_volumes
            call_annotations2 = call_interest
            put_annotations = put_volumes
            put_annotations2 = put_interest

            c1 = call_volumes ** 0.2
            c2 = put_volumes ** 0.2

            call_total = "{:,}".format(call_volumes.sum())
            put_total = "{:,}".format(put_volumes.sum())

            scatter_title = "Volume"

        elif scatter == "interest":
            max_norm = max([max(call_interest), max(put_interest)])

            call_markers = (
                (call_interest - min(call_interest)) / (max_norm - min(call_interest))
            ) * 300
            put_markers = (
                (put_interest - min(put_interest)) / (max_norm - min(put_interest))
            ) * 300

            call_annotations = call_interest
            call_annotations2 = call_volumes
            put_annotations = put_interest
            put_annotations2 = put_volumes

            c1 = call_interest ** 0.2
            c2 = put_interest ** 0.2

            call_total = "{:,}".format(call_interest.sum())
            put_total = "{:,}".format(put_interest.sum())

            scatter_title = "Open Interest"

        elif scatter == "unusual":

            try:
                call_filter_index = call_interest > 50
                put_filter_index = put_interest > 50
                call_V_OI = np.divide(
                    call_volumes[call_filter_index], call_interest[call_filter_index]
                )
                put_V_OI = np.divide(put_volumes[put_filter_index], put_interest[put_filter_index])
            except:
                call_filter_index = call_interest > 0
                put_filter_index = put_interest > 0
                call_V_OI = np.divide(
                    call_volumes[call_filter_index], call_interest[call_filter_index]
                )
                put_V_OI = np.divide(put_volumes[put_filter_index], put_interest[put_filter_index])
            max_norm = max([max(call_V_OI), max(put_V_OI)])

            call_markers = ((call_V_OI - min(call_V_OI)) / (max_norm - min(call_V_OI))) * 300
            put_markers = ((put_V_OI - min(put_V_OI)) / (max_norm - min(put_V_OI))) * 300

            call_dates = call_dates[call_filter_index]
            call_strikes = call_strikes[call_filter_index]

            put_dates = put_dates[put_filter_index]
            put_strikes = put_strikes[put_filter_index]

            call_annotations = np.round(call_V_OI, 3)
            call_annotations2 = call_volumes[call_filter_index]
            call_annotations3 = call_interest[call_filter_index]

            put_annotations = np.round(put_V_OI, 3)
            put_annotations2 = put_volumes[put_filter_index]
            put_annotations3 = put_interest[put_filter_index]

            c1 = call_V_OI ** 0.2
            c2 = put_V_OI ** 0.2

            call_symbol = call_symbol[call_filter_index]
            put_symbol = put_symbol[put_filter_index]

            call_total = (
                "V: {:,}".format(call_volumes.sum()) + " " + "OI: {:,}".format(call_interest.sum())
            )
            put_total = (
                "V: {:,}".format(put_volumes.sum()) + " " + "OI: {:,}".format(put_interest.sum())
            )
            scatter_title = "Unusual Options"

        # Setup the figure for two subplots, one for calls, one for puts
        plt.style.use("ggplot")
        fig, axs = plt.subplots(2, figsize=(fig_width, fig_height))
        norm = plt.Normalize(0, 1)
        cmap1 = plt.cm.ocean
        cmap2 = plt.cm.gist_earth

        # Isolate the separate subplots
        calls = axs[0]
        puts = axs[1]

        # Scatter plot the data with the size of the marker equal to the volume
        sc1 = calls.scatter(
            call_dates, call_strikes, c=c1, edgecolors="k", s=call_markers, cmap=cmap1,
        )
        sc2 = puts.scatter(put_dates, put_strikes, c=c2, edgecolors="k", s=put_markers, cmap=cmap2,)

        # this plots the current price as a horizontal line, and shades the ITM section of the plot
        sc1.axes.axhline(price, 0, 1, color="k", linestyle="dashed", alpha=0.4)
        sc2.axes.axhline(price, 0, 1, color="k", linestyle="dashed", alpha=0.4)
        calls.axhspan(min(calls.get_ylim()), price, alpha=0.3)
        puts.axhspan(price, max(puts.get_ylim()), alpha=0.3)

        # Setup x and y labels and ticks
        sc1.axes.tick_params(axis="x", labelsize=8, rotation=25)
        sc2.axes.tick_params(axis="x", labelsize=8, rotation=25)

        fig.tight_layout(pad=4.0, h_pad=2.0)

        # Set the X and Y labels as well as the current price and % box
        fig.text(0.5, 0.05, "Expiration Dates", ha="center", fontsize=8)
        fig.text(0.05, 0.5, "Strike Price", va="center", rotation="vertical", fontsize=8)
        fig.text(
            0.75,
            0.045,
            "Last Price\n${} ({}%)".format(price, percent_change),
            ha="center",
            bbox=dict(facecolor="blue", alpha=0.4),
        )

        # Titles for the figure and subplots
        fig.suptitle("{} ({}) - {}".format(stock_name, symbol, scatter_title), fontsize=11)
        calls.set_title("Calls - Total {}: {}".format(scatter_title, call_total), fontsize=9)
        puts.set_title("Puts - Total {}: {}".format(scatter_title, put_total), fontsize=9)

        # Setup the calls and puts annotation box
        annot1 = calls.annotate(
            "",
            xy=(0, 0),
            xytext=(-65, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="fancy"),
        )
        annot2 = puts.annotate(
            "",
            xy=(0, 0),
            xytext=(-65, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="fancy"),
        )
        annot1.set_visible(False)
        annot2.set_visible(False)

        def update_annot1(ind):
            if scatter == "volume":
                index = ind["ind"][:4]
                text1 = "{}".format(
                    "\n".join(
                        str(call_symbol[n].split("_")[1])
                        + ": "
                        + "Vol: {:,}".format(call_annotations[n])
                        + " OI: {:,}".format(call_annotations2[n])
                        for n in index
                    )
                )
            elif scatter == "interest":
                index = ind["ind"][:4]
                text1 = "{}".format(
                    "\n".join(
                        str(call_symbol[n].split("_")[1])
                        + ": "
                        + "OI: {:,}".format(call_annotations[n])
                        + " Vol: {:,}".format(call_annotations2[n])
                        for n in index
                    )
                )
            elif scatter == "unusual":
                index = ind["ind"][:4]
                text1 = "{}".format(
                    "\n".join(
                        str(call_symbol[n].split("_")[1])
                        + ": "
                        + "V/OI: {:,}, V: {:,}, OI: {:,}".format(
                            call_annotations[n], call_annotations2[n], call_annotations3[n]
                        )
                        for n in index
                    )
                )
            pos1 = sc1.get_offsets()[ind["ind"][0]]
            annot1.xy = pos1
            annot1.set_text(text1)
            annot1.get_bbox_patch().set_facecolor(cmap1(norm(c1[ind["ind"][0]])))
            annot1.get_bbox_patch().set_alpha(0.8)

        def update_annot2(ind):
            if scatter == "volume":
                index = ind["ind"][:4]
                text2 = "{}".format(
                    "\n".join(
                        str(put_symbol[n].split("_")[1])
                        + ": "
                        + "Vol: {:,}".format(put_annotations[n])
                        + " OI: {:,}".format(put_annotations2[n])
                        for n in index
                    )
                )
            elif scatter == "interest":
                index = ind["ind"][:4]
                text2 = "{}".format(
                    "\n".join(
                        str(put_symbol[n].split("_")[1])
                        + ": "
                        + "OI: {:,}".format(put_annotations[n])
                        + " Vol: {:,}".format(put_annotations2[n])
                        for n in index
                    )
                )
            elif scatter == "unusual":
                index = ind["ind"][:4]
                text2 = "{}".format(
                    "\n".join(
                        str(put_symbol[n].split("_")[1])
                        + ": "
                        + "V/OI: {:,}, V: {:,}, OI: {:,}".format(
                            put_annotations[n], put_annotations2[n], put_annotations3[n]
                        )
                        for n in index
                    )
                )

            pos2 = sc2.get_offsets()[ind["ind"][0]]
            annot2.xy = pos2
            annot2.set_text(text2)
            annot2.get_bbox_patch().set_facecolor(cmap2(norm(c2[ind["ind"][0]])))
            annot2.get_bbox_patch().set_alpha(0.8)

        def hover(event):
            vis = annot1.get_visible()
            if event.inaxes == calls.axes:
                cont, ind1 = sc1.contains(event)
                if cont:
                    update_annot1(ind1)
                    annot1.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot1.set_visible(False)
                        fig.canvas.draw_idle()

            vis = annot2.get_visible()
            if event.inaxes == puts.axes:
                cont, ind2 = sc2.contains(event)
                if cont:
                    update_annot2(ind2)
                    annot2.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot2.set_visible(False)
                        fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)
        plt.show()
    else:
        print("Open_interest data invalid or missing...")