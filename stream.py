import json

from TwitterAPI import TwitterAPI
import json
import boto3
import re
from bs4 import BeautifulSoup

## twitter credentials
consumer_key = your consumerkey
consumer_secret = your consumer_secret
access_token_key = your access_token_key
access_token_secret = your access_token_secret
aws_access_key_id= your aws_access_key_id
aws_secret_access_key=c your aws_secret_access_key
stream = your Kinesis stream name



id_field = 'id_str'

def get_tweet(doc):
    tweet = {}
    tweet[id_field] = doc[id_field]
    tweet['hashtags'] = map(lambda x: x['text'],doc['entities']['hashtags'])
    # print doc.keys()
    tweet['coordinates'] = doc['coordinates']
    tweet['timestamp_ms'] = doc['timestamp_ms']
    tweet['source'] = BeautifulSoup(doc['source']).find('a').text
    #tweet['source'] = re.findall(r'Twitter for\w*',a)
    tweet['place'] = doc['place']['name']
    tweet['replies'] = doc['reply_count']
    tweet['text'] = doc['text']
    tweet['user'] = {'id': doc['user']['id'], \
                     'name': doc['user']['name'], \
                     'followers': doc['user']['followers_count'],\
                     'favourites':doc['user']['favourites_count'],\
                     'total_tweets':doc['user']['statuses_count']}
    tweet['mentions'] = re.findall(r'@\w*', doc['text'])
    tweet['language'] = doc['lang']
    return tweet

api = TwitterAPI(consumer_key, consumer_secret, access_token_key,access_token_se
cret)
kinesis = boto3.client('kinesis',region_name='us-east-1',aws_access_key_id=aws_a
ccess_key_id,aws_secret_access_key=aws_secret_access_key )

r = api.request('statuses/filter', {'locations':'-90, -90, 90, 90'})
tweets = []
count = 0


for item in r:
        if 'coordinates' in item.keys():
                if item['coordinates'] is not None:
                        try:
                                        k = get_tweet(item)
                                        jsonItem = json.dumps(k)
                                        tweets.append({'Data':jsonItem, 'Partiti
onKey':"filler"})
                                        count += 1
                        except:
                                        count += 1
                        if count == 100:
                                           print tweets
                                           kinesis.put_records(StreamName="twitt
er", Records=tweets)
                                           count = 0
                                           tweets = []
