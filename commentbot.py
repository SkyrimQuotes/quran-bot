#!/usr/bin/python

import traceback
import time
from functions import *

# Private file, has one function: login(), which returns an authorized PRAW instance.
from auth import login

FORMAT = "COMM: %(message)s"
logging.basicConfig(level = logging.INFO, format = FORMAT)


def commentstream():
    """ocmmentstream(): This function looks up new comments which quote the Qur'an."""

    for comment in sub.stream.comments():
        proccomment(comment)

if __name__ == '__main__':
    r = login()
    sub = r.subreddit("SkyrimQuotes")
    while True:
        try:
            logging.info("starting...")
            commentstream()
        except Exception as e:
            trace = traceback.format_exc()
            logging.info("EXCEPTION: {} \n \n {}".format(str(e), str(trace)))
            time.sleep(30)
