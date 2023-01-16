import os
import time
from sqlalchemy import create_engine
import logging
import requests

poll_rate_secs = int(os.getenv('SLACK_POLLING_REFRESH_RATE_SECS', 0))
is_simulation_mode = os.getenv('SLACK_BOT_IS_SIMULATION') == 'True'

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

# logger.setLevel(level=int(os.getenv('LOG_LEVEL',0)))
file_handler=logging.FileHandler(filename=f'{__name__}.log')
file_formatter=logging.Formatter(os.getenv('LOG_FORMAT',''))
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

time.sleep(10)  # seconds

pg = create_engine(
	'postgresql://admin:admin@postgresdb:5432/sentiment_db', echo=True)

webhook_url = os.getenv('SLACK_WEBHOOK_URL','')

neutral_text = 'See the latest updates from the current situation'
positive_text = 'The tide of war is turning! Things are looking good 🥳'
negative_text = 'It is looking not so great right now 🥺. Russia seems to have the upper hand.'

iteration = 0

current_sentiment_is_positive = None

while True:

	results = pg.execute('''
		SELECT
		id, text, pos_score, neg_score, neu_score, username
		FROM tweets
		ORDER BY id DESC
		LIMIT 1;
	''')
	results = list(results)

	if len(results)  == 0:
		logger.debug('No tweets found in postgresql database')
		time.sleep(poll_rate_secs)
		continue
	elif len(results) < 1:
		logger.error(
			'Too many tweets found in result postgresql database')
		time.sleep(poll_rate_secs)
		continue
	
	is_first_iteration = iteration != 0

	results = list(results)[0]
	tweet_id = results['id']
	pos_score = results['pos_score']
	neg_score = results['neg_score']
	neu_score = results['neu_score']
	username = results['username']
	tweet_text = results['text']
	sentiment_text = ''
	new_sentiment_is_positive = None
	if pos_score > neg_score and pos_score > neu_score:
		new_sentiment_is_positive = True
		sentiment_text = positive_text
	elif neg_score > pos_score and neg_score > neu_score:
		new_sentiment_is_positive = False
		sentiment_text = negative_text
	else:
		if is_first_iteration == True:
			sentiment_text = positive_text if pos_score > neg_score else negative_text
		else:
			sentiment_text=neutral_text
  
  
  
	neutral_sentiment = new_sentiment_is_positive == None
	no_new_news =  current_sentiment_is_positive == new_sentiment_is_positive
	if is_first_iteration == False and (neutral_sentiment or no_new_news):
		logger.debug(f'Continuing because conditions {is_first_iteration} {neutral_sentiment} {no_new_news} {is_first_iteration == False and (neutral_sentiment or no_new_news)}')
		time.sleep(poll_rate_secs)
		iteration += 1
		continue



	slack_post_data = {
		"blocks": [
			{
				"type": "header",
				"text": {
						"type": "plain_text",
						"text": "🇺🇦 Ukraine Breaking news!",
				}
			},
			{
				"type": "section",
				"text": {
						"type": "mrkdwn",
						"text": f"**{sentiment_text}\nView the latest tweet below"
				}
			},
			{
				"type": "divider"
			},
			{
				"type": "section",
				"text": {
						"type": "mrkdwn",
						"text": f"{tweet_text}"
				}
			},
		]
	}
 
	if is_simulation_mode is True:
		logger.critical('Simulate post', slack_post_data)
	else:
		requests.post(url=webhook_url, json = slack_post_data)
 
 
	iteration += 1
	time.sleep(poll_rate_secs)
