'''
Jenny Han
Deeplocal Coding Challenge
11/15/2019

This code looks at the 2017 hashtags tweeted by @deeplocal and counts them. 
Also, it runs a sentiment analysis on all tweets in 2017 and calculates the positive,
neutral, and negative percentages for these tweets.
'''

import re
import tweepy, datetime
from tweepy import OAuthHandler 
from textblob import TextBlob 
from collections import defaultdict
from tabulate import tabulate

consumer_key = 'DpWaQwCEsNibAbYZnOmAN3cgh'
consumer_secret = 'ZXOdzffjQhe3RVyJv8AweYem4hjhpo5zznexZZ3j9pQGtns3VN'
access_token = '1195429075352985600-AZsukmnS5Re8Mb3OAMDP9vz7bZJwmr'
access_token_secret = 'VRDa52hER7cYNCuNl8y5DH1BY9xuwVI9a07cCVVH7UZs6'
username = "deeplocal"
year = "2017"

positive_tweets = 0
negative_tweets = 0
neutral_tweets = 0

'''
This function authenticates the connection to the Twitter API
'''
def authenticate():
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        apiTweepy = tweepy.API(auth)
        return apiTweepy
    except:
        print("Error in Authentication") 
        return

'''
This function looks for tweets within the given date range.
If found, the function adds it to a dictionary of seen hashtags
'''
def find_tweets(apiTweepy,last_id, aggregate_hashtag, inRange_tweets,sentiment_tweets):
    #find all tweets given the username given, max count is 200
    all_tweets = apiTweepy.user_timeline(screen_name = username, count = 200, max_id=last_id)

    #loop through tweets to find matching year
    for tweet in all_tweets:
        found_year = str(tweet.created_at)[0:4] 

        if found_year == year:
            inRange_tweets.append(tweet)
            sentiment_tweets.append(tweet)
            #extract all things that have a hashtag in front of it
            hashtags = re.findall(r"#(\w+)", tweet.text) 

            for hashtag in hashtags:
                #put hashtags into dictionary with key as hashtag and value as count
                aggregate_hashtag[hashtag] += 1

    if found_year <= str(int(year)-1): #found all of the year's worth of tweets
        return False

    #did not find all of the years tweets, return current tweet to keep an index
    return tweet
  
'''
This function takes a list of hashtags and sorts it into an ordered list
with the most common hashtag at the start of the list.
'''
def sort_hashtags(aggregate_hashtag):
    res = [] #collects resulting 
    for hashtag in aggregate_hashtag:
      val = [aggregate_hashtag[hashtag],hashtag]
      res.append(val)

    #order hastag by number of appearances
    res.sort()
    return res[::-1] 

'''
This function checks the sentiment of a tweet and increments the 
positive, negative, or neutral global count
'''
def sort_sentiments(sentiment_tweets):
    global positive_tweets,negative_tweets,neutral_tweets

    for tweet in sentiment_tweets:        
        #clean tweet for processing
        tweet_cleaned = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet.text).split()) 
        #get analysis of text from Textblob
        analysis = TextBlob(tweet_cleaned)
        if analysis.sentiment[0]>0:
           positive_tweets += 1
        elif analysis.sentiment[0]<0:
           negative_tweets += 1
        else:
           neutral_tweets += 1

'''
Main calls functions to authenticate, gather tweets within the given year, 
and sort the hashtags/sentiments found. This function prints all information 
into the terminal.
'''
def main(): 
    # try to authenticate tweepy
    apiTweepy = authenticate()

    inRange_tweets = [] #list of valid tweets within date range
    sentiment_tweets = [] #tweet text to find sentiments
    aggregate_hashtag = defaultdict(int)
    found_all_flag = False #False if still searching for all tweets within the year
                           #True if found all tweets within the year
    last_id = None

    #Twitter API only allows for 200 tweets to be searched at once, so loop 200 until found all
    #tweets in date range
    while not found_all_flag: 
      tweet = find_tweets(apiTweepy,last_id,aggregate_hashtag,inRange_tweets, sentiment_tweets)
      if tweet == False:
        break
      last_id = tweet.id

    #order hashtag based on count
    res = sort_hashtags(aggregate_hashtag)

    print("\nTable for",year,"hashtags used by @"+username)
    print("\n"+tabulate(res, headers=['count', 'hashtag'])) #print table in terminal

    #calculate percentage of positive, negative, neutral tweets 
    sort_sentiments(sentiment_tweets)
    positive_tweet_percentage = (positive_tweets/len(sentiment_tweets)) * 100
    negative_tweet_percentage = (negative_tweets/len(sentiment_tweets)) * 100
    neutral_tweet_percentage = (neutral_tweets/len(sentiment_tweets)) * 100

    #print some data on sentiments of tweets during given year
    print("\nThere were", str(len(inRange_tweets)),"tweets in",year)
    print("Out of those,",positive_tweets,"were positive at %2.1f%%" % positive_tweet_percentage)
    print("             ",negative_tweets,"were negative at %2.1f%%" % negative_tweet_percentage)
    print("             ",neutral_tweets,"were neutral at %2.1f%%" % neutral_tweet_percentage)

#run main
if __name__ == "__main__": 
    main() 