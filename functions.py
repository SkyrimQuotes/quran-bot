#!/usr/bin/python

import re
import requests
import logging


def checktext(li):
    """checktext(li): li is the text you want to check if it quotes the Qur'an.
    It can be either a list of strings or a string."""
    foundlist = []
    # Regular expression for detecting quotes from the Qur'an
    pattern = "(qur'?an|koran)(\s*[a-z]*.*?[a-z]*\s*)(\d+):(\d+)-?(\d+)?"

    if type(li) == list:
        for text in li:
            text = text.lower()
            found = re.findall(pattern, text)
            if found:
                for i in found:
                    foundlist.append(i[2:])
        return foundlist

    elif type(li) == str:
        text = li.lower()
        found = re.findall(pattern, text)
        if found:
            for i in found:
                foundlist.append(i[2:])
        return foundlist


def checkrepliesforposts(post):
    """checkrepliesforposts(post): post is a PRAW submission object.
    This function checks if the bot already replied to a post which has quoted the Qur'an."""
    comments = post.comments
    for comment in comments:
        cauthor = comment.author
        if cauthor == "QuranBot":
            return [True, comment]
    # return a one item list for consistency.
    return [False]


def checkrepliesforcomments(comment):
    """checkrepliesforcomments(comment): comment is a PRAW comment object.
    This function checks if the bot already replied to a coment which has quoted the Qur'an"""
    comment.refresh()
    comments = comment.replies
    comments.replace_more()
    for comment in comments:
        cauthor = comment.author
        if cauthor == "QuranBot":
            return [True, comment]
    # return a one item list for consistency.
    return [False]


def getverse(verse):
    """getverse(verse): verse is the verse number in the format: s:v,
    where s is surah number, and v is verse number."""
    resp = requests.get("http://api.alquran.cloud/ayah/{}/en.sahih".format(verse))
    if resp.status_code == 400:
        return "Non-existent verse"
    respp = resp.json()
    data = respp.get("data")
    aya = data.get("text")
    edition = data.get("edition")
    tr = edition.get("englishName") + " " + edition.get("type")
    surah = data.get("surah")
    en = surah.get("englishName")
    # Return aya, which is the verse text, tr, which is the translation name,
    # and en, which is the surah's name in English.
    return [aya, tr, en]


def makeversetext(foundlist: list):
    """makeversetext(foundlist: list): foundlist is a list of verses which are to be included in the reply.
    This function forms each verse's segment, and returns it
    alongside a list of nonexistant verses which were requested."""
    replytem = """The Holy Qur'an, Surah {en}, {tr}, Chapter {c}, Verse {v} ({cv}):\n\n>{aya}\n\n*****"""

    nonexistentlist = []
    verli = []

    for verse in foundlist:
        li = getverse(verse)
        if li == "Non-existent verse":
            nonexistentlist.append(verse)
            continue
        aya = li[0]
        tr = li[1]
        en = li[2]
        lii = verse.split(":")
        # c is surah number, v is verse number, cv is both of them in the format c:v
        c = lii[0]
        v = lii[1]
        cv = verse
        reply = replytem
        reply = reply.format(en = en, tr = tr, c = c, v = v, cv = cv, aya = aya)
        verli.append(reply)
    return [verli, nonexistentlist]


def makerply(foundlist: list):
    """makerply(foundlist: list): foundlist is a list of verses which are to be included in the reply.
    This function forms the actual reply string, and returns that."""
    replyheader = "I'm a bot, beep boop."
    replymetadata = "^^[.](http://BEGIN.{met}.END/)"
    replyfooter = "A bot by u/SkyrimQuotes"

    vertext = makeversetext(foundlist)
    verli = vertext[0]
    nonex = vertext[1]

    met = str(foundlist).replace(" ", "")
    # metadata is a little dot link, which includes the verses in the reply. used for comparison purposes.
    metadata = replymetadata.format(met = met)
    replystr = replyheader + "\n" * 2
    for i in verli:
        replystr += i + "\n" * 2
    if nonex:
        x = "The verse(s) ({}) do not exist.\n\n*****".format(nonex) + "\n" * 2
        x = x.replace("'", "")
        x = x.replace("[", "")
        x = x.replace("]", "")
        replystr += x
    replystr += metadata + " "
    replystr += replyfooter
    return replystr


def checkmetadata(botcomtext, reqlist):
    """checkmetadata(botcomtext, reqlist): botcomtext is the bot's comment's text, and reqlist is the requested list
    of verses. This function compares the two, to make sure the bot isn't repeatedly deleting it's replies and replying
    again."""
    metapattern = "(\^\^\[\.\]\(http://BEGIN\.\[')(.*)?('\]\.END/\))"
    metadatafull = re.search(metapattern, botcomtext)
    metadata = metadatafull.group(2)
    metadata = metadata.replace("'", "")
    metadata = metadata.split(",")
    if set(metadata) == set(reqlist):
        return

    return list(reqlist)


def processlist(ls):
    """processlist(ls): ls is the verse and surah number extracted from reddit, in the format ['a', 'b', 'c']
    This function returns a list of all the verses between, and including, b and c.
    or in the format ['a', 'b', ''], in which case it's simply returned as-is."""
    returnlist = []
    for i in ls:
        for y in range(0, len(i)):
            # remove empty strings.
            if i[y] == "":
                i = i[:y]
        # if i has 2 strings: it's not a range, in the format ['a', 'b'] (after the empty strings got removed)
        if len(i) == 2:
            a = i[0]
            b = i[1]
            v = "{}:{}".format(a, b)
            returnlist.append(v)
        # if i has 3 strings: it's a range, in the format ['a', 'b', 'c']
        elif len(i) == 3:
            a = i[0]
            b = i[1]
            c = i[2]
            li = []
            # plus one because range() doesn't include the stopping integer.
            for x in range(int(b), int(c) + 1):
                t = "{}:{}".format(a, x)
                li.append(t)
            returnlist.extend(li)

    return returnlist


def procsubmission(subm):
    """procsubmission(subm): subm is the submission to be processed. This function does all the heavy lifting."""
    title = str(subm.title)
    selftext = str(subm.selftext)
    logging.info("found post: " + str(title))
    requestedlist = checktext([title, selftext])
    # if it quoted the Qur'an:
    if requestedlist:
        logging.info("post passed check: " + str(title))
        hasposted = checkrepliesforposts(subm)
        proclist = processlist(requestedlist)
        # if the bot hasn't replied yet:
        if not hasposted[0]:
            logging.info("haven't posted a reply yet.")
            replystr = makerply(proclist)
            subm.reply(replystr)
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
                logging.info("---------------")
            else:
                logging.info("quotes unchanged.")
                logging.info("---------------")
    else:
        logging.info("post doesn't quote the Quran. ignoring...")
        logging.info("---------------")


def proccomment(com):
    """proccomment(com): com is the comment to be processed. This function does all the heavy lifting."""
    selftext = com.body
    author = str(com.author.name)
    logging.info("found comment by " + author)
    # so it doesn't reply to itself. otherwise, look above. mostly the same code.
    if author != "QuranBot":
        requestedlist = checktext(selftext)
        if requestedlist:
            logging.info(author + "'s comment passed check.")
            hasposted = checkrepliesforcomments(com)
            proclist = processlist(requestedlist)
            if not hasposted[0]:
                logging.info("haven't posted a reply yet.")
                replystr = makerply(proclist)
                com.reply(replystr)
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
                    logging.info("---------------")
                else:
                    logging.info("quotes unchanged.")
                    logging.info("---------------")

        else:
            logging.info("comment doesn't quote the Quran. ignoring...")
            logging.info("---------------")
    else:
        logging.info("bot's own comment. ignoring...")
        logging.info("---------------")


def proceditcom(com):
    """proceditcom(com): com is the edited comment to be processed. This function does all the heavy lifting."""
    hasposted = checkrepliesforcomments(com)
    if not hasposted[0]:
        return
    selftext = com.body
    author = str(com.author.name)
    logging.info("found comment by " + author)
    if author != "QuranBot":
        requestedlist = checktext(selftext)
        if requestedlist:
            logging.info(author + "'s comment passed check.")
            proclist = processlist(requestedlist)
            botcomment = hasposted[1]
            botcomtext = botcomment.body
            inputlist = set(proclist)
            editedlist = checkmetadata(botcomtext, inputlist)
            if editedlist:
                logging.info("comment was edited with more quotes. updating reply...")
                replystr = makerply(editedlist)
                botcomment.edit(replystr)
                logging.info("updated.")
                logging.info("---------------")
            else:
                logging.info("quotes unchanged.")
                logging.info("---------------")

        else:
            logging.info("comment doesn't quote the Quran anymore. deleting reply...")
            botcomment = hasposted[1]
            botcomment.delete()
            logging.info("deleted.")
            logging.info("---------------")
    else:
        logging.info("bot's own comment. ignoring...")
        logging.info("---------------")


def proceditsub(subm):
    """proceditsub(subm): subm is the edited submission to be processed. This function does all the heavy lifting."""
    hasposted = checkrepliesforposts(subm)
    if not hasposted[0]:
        return
    title = str(subm.title)
    selftext = str(subm.selftext)
    logging.info("found post: " + str(title))
    requestedlist = checktext([title, selftext])
    if requestedlist:
        logging.info("post passed check: " + str(title))
        proclist = processlist(requestedlist)
        botcomment = hasposted[1]
        botcomtext = botcomment.body
        inputlist = set(proclist)
        editedlist = checkmetadata(botcomtext, inputlist)
        if editedlist:
            logging.info("post was edited with more quotes. updating reply...")
            replystr = makerply(editedlist)
            botcomment.edit(replystr)
            logging.info("updated.")
            logging.info("---------------")
        else:
            logging.info("quotes unchanged.")
            logging.info("---------------")
    else:
        logging.info("post doesn't quote the Quran anymore. deleting reply...")
        botcomment = hasposted[1]
        botcomment.delete()
        logging.info("deleted.")
        logging.info("---------------")
