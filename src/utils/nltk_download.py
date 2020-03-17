"""
nltk_download.py
Date Created: March 13th, 2020

Author: georgefahmy

Description: This script downloads the database for doing text analysis on the comment bodies for
    sentiment analysis.

"""


# Base Python #
import ssl

# Extended Python #
import nltk


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download()
