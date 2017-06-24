#!/usr/bin/python

import traceback
import time
from functions import *

# Private file, has one function: login(), which returns an authorized PRAW instance.
from auth import login

FORMAT = "POST: %(message)s"
logging.basicConfig(level = logging.INFO, format = FORMAT)


def submissionstream():
    """submissionstream(): This function looks up new submissions which quote the Qur'an in the title or
    in the selftext."""

    for submission in sub.stream.submissions():
        procsubmission(submission)

if __name__ == '__main__':
    r = login()
    sub = r.subreddit("SkyrimQuotes")
    while True:
        try:
            logging.info("starting...")
            submissionstream()
        except Exception as e:
            trace = traceback.format_exc()
            logging.info("EXCEPTION: {} \n \n {}".format(str(e), str(trace)))
            time.sleep(30)
