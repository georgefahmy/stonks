from __future__ import with_statement

import contextlib

try:
    from urllib.parse import urlencode

except ImportError:
    from urllib import urlencode

try:
    from urllib.request import urlopen

except ImportError:
    from urllib2 import urlopen


import sys

# url = "www.google.com"


def make_tiny(url):
    # request_url = "http://tinyurl.com/api-create.php?" + urlencode({"url": url})
    response = urlopen("http://tinyurl.com/api-create.php?url=" + str(url))

    html = response.read()

    return html.decode("utf-8")


# print(str(make_tiny(url)))
