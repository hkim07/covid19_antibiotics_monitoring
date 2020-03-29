import tweepy
import re, json, sqlite3
from unidecode import unidecode
import time, datetime
from config import ckey, csec, akey, asec
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
sbert = SentenceTransformer('bert-base-nli-mean-tokens')


import tweepy
auth = tweepy.OAuthHandler(ckey, csec)
auth.set_access_token(akey, asec)
api = tweepy.API(auth, wait_on_rate_limit_notify=True, wait_on_rate_limit=True)

conn = sqlite3.connect(r"covid_antibiotics.sqlite")
c = conn.cursor()
def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS tweets(parent_id TEXT, parent_created TEXT, parent_text TEXT, reply_id TEXT, reply_created TEXT, reply_text TEXT, similarity REAL)")
    conn.commit()
create_table()

who_official = 'No, antibiotics do not work against viruses, only bacteria. The new coronavirus (2019-nCoV) is a virus and, therefore, antibiotics should not be used as a means of prevention or treatment. However, if you are hospitalized for the 2019-nCoV, you may receive antibiotics because bacterial co-infection is possible.'
who_embs = sbert.encode([who_official], show_progress_bar=False)
threshold = 0

class MyStreamListener(tweepy.StreamListener):

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False

    def on_status(self, status):
        try:
            tweet = status._json
            if (tweet['lang']=='en') & (tweet['in_reply_to_status_id']!=None):
                if 'extended_tweet' in tweet:
                    tweet_extended = tweet['extended_tweet']
                    text = unidecode(tweet['extended_tweet']['full_text'])
                else:
                    text = unidecode(tweet['text'])

                if len(re.findall(r"corona|virus|coronavirus|covid19|covid-19|2019-nCoV|wuhanvirus", text))!=0:
                    sims = cosine_similarity(who_embs, sbert.encode([text]))
                    if sims[0][0]>threshold:
                        try:
                            parent = api.get_status(id=tweet['in_reply_to_status_id'], tweet_mode='extended')._json
                        except:
                            next
                        if parent['user']['id'] != tweet['user']['id']:
                            c.execute("INSERT INTO tweets (parent_id, parent_created, parent_text, reply_id, reply_created, reply_text, similarity) VALUES (?,?,?,?,?,?,?)", (parent['id'], parent['created_at'], parent['full_text'], tweet['id'], tweet['created_at'], text, float(sims[0][0])))
                            conn.commit()
                            print(parent['id'], parent['created_at'], parent['full_text'])
                            print(tweet['id'], tweet['created_at'], text, sims[0][0], '\n')

        except KeyError as e:
            print(str(e))
        return(True)

while True:
    try:
        auth = tweepy.OAuthHandler(ckey, csec)
        auth.set_access_token(akey, asec)
        twitterStream = tweepy.Stream(auth, MyStreamListener(), language='en', tweet_mode='extended')
        #Use track to find keywords and follow to find users
        twitterStream.filter(track=['antibiotic', 'antibiotics'])
    except Exception as e:
        print(str(e))
        time.sleep(4)
