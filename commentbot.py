#!/usr/bin/python

import logging
import traceback
import time
from functions import *

# Private file, has one function: login(), which returns an authorized PRAW instance.
from auth import login

FORMAT = "COMM: %(message)s"
logging.basicConfig(level = logging.INFO, format = FORMAT)


def commentstream():
    """ocmmentstream(): This function looks up new comments which quote the Qur'an.
    after 6 requests with no new comments, it switches to submissionstream()."""
    for comment in sub.stream.comments():
        selftext = comment.body
        author = str(comment.author.name)
        logging.info("found comment by " + author)
        # so it doesn't reply to itself. otherwise, look above. mostly the same code.
        if author != "QuranBot":
            requestedlist = checktext(selftext)
            if requestedlist:
                logging.info(author + "'s comment passed check.")
                hasposted = checkrepliesforcomments(comment)
                proclist = processlist(requestedlist)
                if not hasposted[0]:
                    logging.info("haven't posted a reply yet.")
                    replystr = makerply(proclist)
                    comment.reply(replystr)
                    logging.info("replied.")
                else:
                    logging.info("already replied.")
                    botcomment = hasposted[1]
                    botcomtext = botcomment.body
                    inputlist = set(proclist)
                    editedlist = checkmetadata(botcomtext, inputlist)
                    if editedlist:
                        logging.info("comment was edited with more quotes. updating reply...")
                        replystr = makerply(editedlist)
                        botcomment.edit(replystr)
                        logging.info("updated.")
                    else:
                        logging.info("quotes unchanged.")

            else:
                logging.info("comment doesn't quote the Quran. ignoring...")
        else:
            logging.info("bot's own comment. ignoring...")

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
