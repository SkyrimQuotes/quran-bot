#!/usr/bin/python

import logging
import traceback
import time
from functions import *

# Private file, has one function: login(), which returns an authorized PRAW instance.
from auth import login

FORMAT = "POST: %(message)s"
logging.basicConfig(level = logging.INFO, format = FORMAT)


def submissionstream():
    """submissionstream(): This function looks up new submissions which quote the Qur'an in the title or
    in the selftext.
    after 6 requests with no new posts, it switches to commentstream()."""
    for submission in sub.stream.submissions():
        title = str(submission.title)
        selftext = str(submission.selftext)
        logging.info("found post: " + str(title))
        requestedlist = checktext([title, selftext])
        # if it quoted the Qur'an:
        if requestedlist:
            logging.info("post passed check: " + str(title))
            hasposted = checkrepliesforposts(submission)
            proclist = processlist(requestedlist)
            # if the bot hasn't replied yet:
            if not hasposted[0]:
                logging.info("haven't posted a reply yet.")
                replystr = makerply(proclist)
                submission.reply(replystr)
                logging.info("replied.")
            # if the bot replied:
            else:
                logging.info("already replied.")
                botcomment = hasposted[1]
                botcomtext = botcomment.body
                inputlist = set(proclist)
                # checks metadata. if the post was edited with different quotes
                # (read: isn't exactly what the bot had posted):
                editedlist = checkmetadata(botcomtext, inputlist)
                if editedlist:
                    # edit the reply with the new quotes.
                    logging.info("post was edited with more quotes. updating reply...")
                    replystr = makerply(editedlist)
                    botcomment.edit(replystr)
                    logging.info("updated.")
                else:
                    logging.info("quotes unchanged.")
        else:
            logging.info("post doesn't quote the Quran. ignoring...")

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
