import praw

client_id = "vFde6gfmmO4HIA"
client_secret = "mHBRyCr2j_898niCmRa9AHj9S_c"
user_agent = "Qur'anBot by u/SkyrimQuotes: Posts quotes from the Qur'an"
username = "QuranBot"
password = "smart micro shoebox"


def login():

    r = praw.Reddit(client_id = client_id,
                    client_secret = client_secret,
                    user_agent = user_agent,
                    username = username,
                    password = password)

    if r.user.me() == "QuranBot":
        return r
    else:
        return
