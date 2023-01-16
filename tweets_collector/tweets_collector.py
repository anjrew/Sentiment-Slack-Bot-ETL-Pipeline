# import pymongo
import os
import pymongo
from twitter_stream import TwitterStream
from twitter_poller import TwitterPoller
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=int(os.getenv('LOG_LEVEL',0)))
file_handler=logging.FileHandler(filename=f'{__name__}.log')
file_formatter=logging.Formatter(os.getenv('LOG_FORMAT',''))
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

conn=pymongo.MongoClient(host='mongo_db_container')
db = conn.twitter_sentiment_analysis

# The different document collections
tweets_collection = db.tweets
users_collections = db.users


search_terms = ["#UkraineWar -is:retweet -is:reply lang:en"]


# Creating 
def send_tweet_to_mongo(tweet):
    """The callback that sends formatted tweets to mongo_db_container

    Args:
        tweet (dict): A tweet that has been stripped of its class into a dict
    """
    logger.warning('--------- RECEIVED NEW TWEET --------')
    db.tweets.insert_one(tweet)

is_stream = False if os.getenv('TWITTER_SOURCE_IS_STREAM', 'False') == 'False' else True

stream = TwitterStream(bearer_token=os.getenv('TWITTER_BEARER_TOKEN', ''),  tweet_cb=db.tweets.insert_one) if is_stream else TwitterPoller(bearer_token=os.getenv('TWITTER_BEARER_TOKEN', ''),  tweet_cb=db.tweets.insert_one, poll_rate_secs=int(os.getenv('COLLECTOR_POLLING_REFRESH_RATE_SECS', 1)))
    

# Adding terms to search rules
# It's important to know that these rules don't get deleted when you stop the
# program, so you'd need to use stream.get_rules() and stream.delete_rules()
# to change them, or you can use the optional parameter to stream.add_rules()
# called dry_run (set it to True, and the rules will get deleted after the bot
# stopped running).
stream.add_filter_rules(search_terms)

logger.debug('--------- STARTING TWEET STREAM -------', )
# Starting stream
stream.filter()

