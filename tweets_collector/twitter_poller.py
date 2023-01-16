import tweepy
import logging
import time
from tweets_source import TweetsSource

class TwitterPoller(TweetsSource):
    """A class that provides a stream of tweets by polling for tweets from the twitter api"""
        
    def __init__(self, bearer_token: str, tweet_cb, poll_rate_secs=1, lang='en'):
        """The constructor for the Twitter Poller client

        Args: tweet_cb : The function invoked when getting a new tweet
        Args: poll_rate_secs : The interval at which to poll for tweets
        Args: lang : The language of the tweets to get
        """
        self.__current_tweet = None
        self.__tweet_cb = tweet_cb
        self.__poll_rate_secs = int(poll_rate_secs)
        self.language = lang
        
        #################
        # Authentication #
        #################
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            wait_on_rate_limit=True,
        )


    # This function gets called when a tweet passes the stream
    def on_tweet(self, tweet: tweepy.Tweet) -> dict:
        self.__tweet_cb(self._add_user_details(dict(tweet)))
        time.sleep(0.5)
    
    
    def filter(self):
        
        max_tweets = 1
        
        while True:
        
            cursor = tweepy.Paginator(
                method=self.client.search_recent_tweets,
                query=' OR '.join(self.search_query),
                tweet_fields=['author_id', 'created_at', 'public_metrics'],
            ).flatten(limit=max_tweets)
        
            results = list(map(lambda tweet: tweet,cursor))
            
            if len(results) == max_tweets:
                
                if self.__current_tweet is None:
                    self.__current_tweet = results[0]
                    self.on_tweet(self.__current_tweet)
                    logging.info('--- First tweet received ---')
                else:    
                    if self.__current_tweet.id != results[0].id:
                        result_tweet = results[0]
                        self.__current_tweet = result_tweet
                        self.on_tweet(result_tweet)
                        
                    else:
                        logging.debug('--- Tweet already received ---')
                    
            elif len(results) < max_tweets:
                logging.debug('--- No new tweets found ---')
                
            else:
                logging.error('--- Too many new tweets found ---')
        
            time.sleep(self.__poll_rate_secs)
    
          
    def add_filter_rules(self, rules):
        self.search_query = rules        
    
    
    def _add_user_details(self, tweet: tweepy.Tweet) -> tweepy.Tweet:
        user_id = tweet['author_id']
        response = self.client.get_user(id=user_id)
        tweet['user_info'] = dict(response.data)
        return tweet
        