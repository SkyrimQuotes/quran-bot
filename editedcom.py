#!/usr/bin/python

import traceback
import time
from functions import *

# Private file, has one function: login(), which returns an authorized PRAW instance.
from auth import login


FORMAT = "EDIT: %(message)s"
logging.basicConfig(level = logging.INFO, format = FORMAT)


def editedstream():
    """editedstream(): This function looks up edited comments and posts which quote the Qur'an."""

    for comment in sub.stream.comments(pause_after = 1):
        if comment is None:
            break
        proceditcom(comment)

    for post in sub.stream.submissions(pause_after = 1):
        if post is None:
            break
        proceditsub(post)

if __name__ == '__main__':
    r = login()
    sub = r.subreddit("SkyrimQuotes")
    while True:
        try:
            logging.info("starting...")
            editedstream()
            time.sleep(60)
            logging.info("ended.")

        except Exception as e:
            trace = traceback.format_exc()
            logging.info("EXCEPTION: {} \n \n {}".format(str(e), str(trace)))
            time.sleep(120)
