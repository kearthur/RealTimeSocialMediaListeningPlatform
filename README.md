# StreamingTwitterMap
This project uses Twitter public streams to aanalyze tweets for specific keywords and hashtags. We will show you how to deploy the Amazon Web Services managed services tools Kinesis Stream, Kinesis Firehose, Amazon Elastic Search, and Kibana, to create a discovery platform for near-real-time Twitter data.  

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

#Insert code from stream.py file in repository. 
```

5. On AWS, create an Elastic Search domain, a Kinesis stream (called "Twitter_data" in our code), and a Firehose connected to your Kinesis stream. 

6. Use Git Bash to run stream.py, which will start feeding streaming Twitter data into your Kinesis stream.

```
python stream.py
```
