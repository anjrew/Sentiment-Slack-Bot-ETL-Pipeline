import os
import pymongo
import time
from sqlalchemy import create_engine
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from cleaning_text import clean_tweet

logger = logging.getLogger(__name__)
logger.setLevel(level=int(os.getenv('LOG_LEVEL',0)))
file_handler=logging.FileHandler(filename=f'{__name__}.log')
file_formatter=logging.Formatter(os.getenv('LOG_FORMAT',''))
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

BULK_TRANSFORM_AMOUNT = int(os.getenv('BULK_TRANSFORM_AMOUNT', 1))
POLL_RATE_SEC = int(os.getenv('ETL_POLL_RATE_SEC', 10))

time.sleep(5)  # seconds

s = SentimentIntensityAnalyzer()

# Establish a connection to the MongoDB server
client = pymongo.MongoClient(host="mongo_db_container", port=27017)

pg = create_engine('postgresql://admin:admin@postgresdb:5432/sentiment_db', echo=True)


# PRIMARY KEY UNIQUE
pg.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        id BIGSERIAL PRIMARY KEY,
        text VARCHAR(500),
        compound_score NUMERIC,
        pos_score NUMERIC,
        neg_score NUMERIC,
        neu_score NUMERIC,
        cleaned_text VARCHAR(500),
        username VARCHAR(20),
        user_id BIGSERIAL
    );
''')
     

# Select the database you want to use withing the MongoDB server
mongo_sentiment_analysis_collection = client.twitter_sentiment_analysis


last_tweet_index = 0
last_tweet_id = None

while True:

    # Extract the tweets
    docs = list(mongo_sentiment_analysis_collection.tweets.find(
        limit=BULK_TRANSFORM_AMOUNT).skip(last_tweet_index))

    if len(docs) == BULK_TRANSFORM_AMOUNT:
        last_tweet_index += BULK_TRANSFORM_AMOUNT

        # Transform
        for doc in docs:
            logger.debug('Found tweet text', doc)
            
            #cleaning the tweets*

            cleaned_text=clean_tweet(doc['text'])

            # assuming your JSON docs have a text field
            sentiment = s.polarity_scores(cleaned_text)
            logger.warning(sentiment)

            # replace placeholder from the ETL chapter
            compound = sentiment['compound']
            pos = sentiment['pos']
            neg = sentiment['neg']
            neu = sentiment['neu']
            tweet_id = doc['id']

            user_info = doc['user_info']

            text = doc['text']
            
            if last_tweet_id==tweet_id:
                continue

            query = """INSERT INTO tweets 
            (id, text, compound_score, pos_score, neg_score, neu_score, cleaned_text, username, user_id)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;"""

            pg.execute(query, (tweet_id, text, compound, pos, neg, neu, cleaned_text,user_info['username'], user_info['id'])) 
            last_tweet_id=tweet_id

    elif len(docs) > BULK_TRANSFORM_AMOUNT:
        logger.error(
            f'There should never be more than {BULK_TRANSFORM_AMOUNT} tweets because of the BULK_TRANSFORM_AMOUNT variable')

    else:
        logger.debug(
            f'Not enough tweets to process sentiment. Only received {len(docs)} tweets')

    time.sleep(POLL_RATE_SEC)
