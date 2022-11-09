import tweepy
import configparser
import json
from datetime import date
from kafka import KafkaProducer
import boto3

# We import our Twitter credentials from a external file
# This improves safety and ease of use, in case that we change them
config_twitter = configparser.ConfigParser()
config_twitter.read('twitter_config.cfg')
bearer_token = config_twitter['CREDENTIALS']['bearer_token']

client = tweepy.StreamingClient(bearer_token)

# Here we define our Kafka producer
KAFKA_TOPIC = '<INSERT_TOPIC_NAME>'
KAFKA_BOOTSTRAP_SERVER = '<IP:PORT>'
producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('utf-8'), bootstrap_servers=KAFKA_BOOTSTRAP_SERVER)


# Same with AWS credentials as we did with Twitter's
config_aws = configparser.ConfigParser()
config_aws.read('aws_config.cfg')
aws_access_key_id = config_aws['CREDENTIALS']['aws_key_id']
aws_secret_access_key = config_aws['CREDENTIALS']['aws_secret_key']
region_name = config_aws['REGION']['default_region']

bucketname = '<NAME_OF_YOUR_S3_BUCKET>'

s3 = boto3.client('s3', region_name=region_name, 
                        aws_access_key_id=aws_access_key_id, 
                        aws_secret_access_key=aws_secret_access_key)


# In order to open a Twitter streaming with tweepy, we need to extend the StreamingClient class
class MyStream(tweepy.StreamingClient):
    tweets_list = []
    file_name = 'tweets_' + str(date.today()) + '.json'

    # Just a message to know that the stream connected successfully
    def on_connect(self):
        print('Connected')

    # For each tweet, we append it to a list and send it to the Kafka producer
    def on_tweet(self, tweet):
        if tweet.referenced_tweets == None:
            producer.send(KAFKA_TOPIC, value=tweet.data)
            MyStream.tweets_list.append(tweet.data)

    # When the stream ends, we save that list to a file and upload it to S3
    # This is our copy of raw data
    def on_disconnect(self):
        with open(MyStream.file_name, 'a', encoding="utf-8") as f:
                    for item in MyStream.tweets_list:
                        print(json.dumps(item), file=f)
        s3.upload_file(MyStream.file_name, bucketname, 'Tweets/' + MyStream.file_name)



stream = MyStream(bearer_token=bearer_token)
###################################################################################################
#                We define the rules that dictate which tweets are requested                      
###################################################################################################
#                For more info about how to define rules, take a look at:                         
# https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule 
#
# For our case, we'll search for tweets in english that contain the terms "Twitter" and "Elon Musk"
###################################################################################################
rule = '"Twitter" "Elon Musk" lang:en'
stream.add_rules(tweepy.StreamRule(rule))


# Finally, we start the stream, requesting a number of tweet fields
# More info: https://developer.twitter.com/en/docs/twitter-api/fields
stream.filter(tweet_fields=['referenced_tweets', 'public_metrics', 'created_at'])
