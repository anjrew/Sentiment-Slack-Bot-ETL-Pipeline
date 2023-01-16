import tweepy
import time
from tweets_source import TweetsSource

# Bot searches for tweets containing certain keywords
class TwitterStream(tweepy.StreamingClient, TweetsSource):
    """A class that provides a stream of tweets for the given

    Args:
        tweepy (_type_): _description_
    """
        
    def __init__(self, bearer_token: str, tweet_cb):
        """The constructor for the Twitter streaming client

        Args: tweet_cb : The function invoked when getting a new tweet
            
        """
        super(TwitterStream, self).__init__(bearer_token)
        self.tweet_cb = tweet_cb

    def on_connect(self):
        """ This function gets called when the stream is working"""
        print("Connected twitter stream")


    # This function gets called when a tweet passes the stream
    def on_tweet(self, tweet):

        # Displaying tweet in console
        if tweet.referenced_tweets == None:
            print(tweet.data)
            self.tweet_cb:(tweet.data)
            # Delay between tweets
            time.sleep(0.5)
    
          
    def add_filter_rules(self, rules):
        self.add_rules(list(map(lambda term:tweepy.StreamRule(term), rules)), dry_run=True)
        
