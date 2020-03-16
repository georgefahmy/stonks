import ftplib
import logging
import os
import re

logger = logging.getLogger(__name__)
LOGGER_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"


def main():
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOGGER_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(handler)

    # Connect to ftp.nasdaqtrader.com
    logger.info("Generating ticker list...")
    ftp = ftplib.FTP("ftp.nasdaqtrader.com", "anonymous", "anonymous@debian.org")
    # Download files nasdaqlisted.txt and otherlisted.txt from ftp.nasdaqtrader.com
    for file in ["nasdaqlisted.txt", "otherlisted.txt"]:
        ftp.cwd("/SymbolDirectory")
        localfile = open(file, "wb")
        ftp.retrbinary("RETR " + file, localfile.write)
        localfile.close()
    ftp.quit()

    # Grep for common stock in nasdaqlisted.txt and otherlisted.txt
    for file in ["nasdaqlisted.txt", "otherlisted.txt"]:
        localfile = open(file, "r")
        for line in localfile:
            ticker = line.split("|")[0]
            name = line.split("|")[1]
            # Append tickers to file tickers.txt
            open("tickers.txt", "a+").write(ticker + "|" + name + "\n")

    logger.info("Done!")


if __name__ == "__main__":
    main()
