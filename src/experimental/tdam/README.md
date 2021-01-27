First `git clone https://github.com/timkpaine/tdameritrade.git`

`cd tdameritrade` > `pip install .` or `python setup.py install`
(`pip install -e .` if you want to make modifications)

Install the requirements
`pip install -r requirements`

Download the chromedriver from:
`https://sites.google.com/a/chromium.org/chromedriver/home`
and put it in your PATH. (I put mine in /usr/local/bin/)

Once you have this chromedriver in your path you need to run the authentication function from tdameritrade.

Set up the follow environment variables:
```export TDAMERITRADE_CLIENT_ID="<your client id>"
export REDIRECT_URI="<your redirect uri>"
```

Once the environment variables are set from your TD Ameritrade developer account, run:
```
python auth.py
```
and follow the prompts.

After this program runs it will open chrome and prompt you to log into your TDAmeritrade account.
This is your trading account, not your developer account.

After this is done, it will save the credentials file in the main folder and then write it as
and environment variable.

### td_analysis
```
usage: tda [-h] [-p] [-t TARGET] [-d DELAY] [-hh HOURS]
           [-s {volume,v,open_interest,interest,i,unusual,u,bidask,b,both,all}]
           [-l] [-w WINDOW_SIZE WINDOW_SIZE]
           symbol

Detailed analysis of stocks and options using the tdameritrade api.

positional arguments:
  symbol                Stock symbol to analyze

optional arguments:
  -h, --help            show this help message and exit
  -p, --price-only      Only display the price and volume portion of the
                        plots.
  -t TARGET, --target TARGET
                        Plots a horizontal line at the target price.
  -d DELAY, --delay DELAY
                        How often to update the plot. Default 60 seconds.
  -hh HOURS, --hours HOURS
                        Optional flag for number of hours to limit the plot to
                        display.
  -s, --scatter {volume,v,open_interest,interest,i,unusual,u,bidask,b,both,all}
                        Generates an instantaneous snapshot of all option
                        positions and volumes, options: volume, interest (open
                        interest), unusual (volume/open_interest), bidask
                        (bid/ask spread), both (volume and open_interest), all
                        (volume, open interest, unusual options, bidask spread)
  -l, --limit           Dont limit the plotting window
  -w WINDOW_SIZE WINDOW_SIZE, --window_size WINDOW_SIZE WINDOW_SIZE
                        provide optional window size for plots. width x height y
  ```
