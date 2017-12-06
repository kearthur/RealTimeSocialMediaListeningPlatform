# StreamingTwitterMap
This project uses Twitter public streams to analyze tweets for specific keywords and hashtags. We will show you how to deploy the Amazon Web Services managed services tools Kinesis Stream, Kinesis Firehose, Amazon Elastic Search, and Kibana, to create a discovery platform for near-real-time Twitter data.  

The dashboard contains -- --

##Getting Started

1. Create an AWS account.

2. Set up a Developer API account with Twitter and create an application to get credentials (requires a Twitter account).
	Create an application to get credentials at https://apps.twitter.com/. In stream.py, you will need to use your Consumer Key, Consumer Secret, Access Token, Access Token Secret.


## Instructions

1. Start an EC2 instance at AWS. Make note of your cluster's public DNS. 

2. Use Git Bash to SSH into your  EC2 instance.

```
$ ssh -i "<your .pem key file path>" ec2-user@<your EC2 cluster public DNS>
```

3. Use Git Bash to install Python Boto3, Twitter, Twitter API, and upgrades.

```
$ sudo pip install boto3
$ sudo pip install twitter
$ sudo pip install TwitterAPI
$ sudo pip install --upgrade requests
```

4. Use the code in stream.py to create stream.py in Git Bash.

```
vi stream.py
```
The code in stream.py is the following:

```
import json
import credentials
from TwitterAPI import TwitterAPI
import json
import boto3
import re
from bs4 import BeautifulSoup

## twitter credentials
consumer_key = credentials.consumer_key
consumer_secret = credentials.consumer_secret
access_token_key = credentials.access_token_key
access_token_secret = credentials.access_token_secret
aws_access_key_id=credentials.aws_access_key_id
aws_secret_access_key=credentials.aws_secret_access_key
stream = credentials.stream



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

```

5. On AWS, create an Elasticsearch domain, a Kinesis stream (called "Twitter_data" in our code), and a Firehose connected to your that picks up data from your Kinesis Stream and directs data to your Elasticsearch domain. 

When you create your Elasticsearch domain, you will need to name the index that it infers. Name this index "twitter."

6. Use Git Bash to run stream.py, which will start feeding streaming Twitter data into your Kinesis stream.

```
python stream.py
```
After running this script, your Kinesis Stream should now be collecting tweets to pass to Firehose and on to your Elasticsearch domain. You can click the "Monitoring" tab on either your Stream or Firehose to see visualizations of the amount of data coming in to your Kinesis pipelines. 

7. Check the "Index" tab of your Elasticsearch domain. There is a default index called ".kibana." Once you see your index named "twitter" appear, this means that your domain has started to recive an index data. 

8. Now that data is being indexed under the schema named "twitter" that Elasticsearch is inferring, you can click the link to Kibana in your Elasticsearch service console. This will take you to the Kibana application that is running on top of the current Elasticsearch domain. 

9. Unfortunately, the schema that Elasticsearch is inferring automatically will not assign the correct types to our coordinate and time stamp fields. We need to change the types of these fields in order to use them to make meaningful visualizations. In order to do this, we will use the Developer Tools shell in Kibana. To access this shell, click on "Developer Tools" in the left toolbar.

In the console, enter and run the following two chunks of code. 

The first chunk creates a new index called "my_index," which correctly indexes the time stamp as a date and the coordinates as a geo_pint type. 

The second chunk takes all of the Twitter data that was indexed under your "twitter" index and copies it to the new "my_index" index. We have to copy this data over because no changes can be made to an existing index. 

```
PUT my_index
{
"settings": {
    "index.mapping.ignore_malformed": true 
  },
  "mappings": {
    "doc": { 
      "properties": 
				  {"timestamp_ms": {
                                  "type": "date"
                                  },
                     "text": {
                                  "type": "string"
                              },
                     "coordinates": {
                          "properties": {
                             "coordinates": {
                                "type": "geo_point"
                             },
                             "type": {
                               "type": "string",
                                "index" : "not_analyzed"
                            }
                          }
                     },
                     "user": {
                          "properties": {
                             "id": {
                                "type": "long"
                             },
                             "name": {
                                "type": "string"
                            }
                          }
                     }
                    }
				}
        }
      }


POST _reindex
{
  "source": {
    "index": "twitter"
  },
  "dest": {
    "index": "my_index"
  }
}	
```
