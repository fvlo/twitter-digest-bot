import tweepy
import pytz
from datetime import datetime, timedelta

def read_secrets(file_path):
    secrets = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split(' = ')
            secrets[key] = value
    return secrets

secrets = read_secrets('secrets.txt')

api_key = secrets['TWITTER_API_KEY']
api_secret = secrets['TWITTER_API_KEY_SECRET']
access_token = secrets['TWITTER_ACCESS_TOKEN']
access_token_secret = secrets['TWITTER_ACCESS_TOKEN_SECRET']
auth = tweepy.OAuth1UserHandler(
   api_key, api_secret,
   access_token, access_token_secret
)
api = tweepy.API(auth)

def get_conversation(tweet_id, conversation, parsed_tweets):
    if len(conversation) > 20:
        conversation.append("THERE ARE MORE THAN 20 TWEETS IN THIS CONVERSATION...")
        return
    try:
        tweet = api.get_status(tweet_id, tweet_mode='extended')
        conversation.append(tweet.user.screen_name + ", " + tweet.id_str + ": " + tweet.full_text)
        parsed_tweets.append(tweet.id)
        if tweet.in_reply_to_status_id:
            get_conversation(tweet.in_reply_to_status_id, conversation, parsed_tweets)

    except:
        conversation.append("THERE WAS AN ERROR FETCHING THIS TWEET")
        pass


# Get tweets for the past n days. Return tweets in a list of conversations
# and total word count
def get_tweets_for_past_n_days(username, timewindowdays=1, max_tweets=-1):
    now = datetime.now(pytz.utc)
    cutoff_time = now - timedelta(days=timewindowdays)
    all_tweets = []
    parsed_tweets = []

    # Flag to check whether the tweets are still within the time window
    within_time_window = True

    # Get user tweet timeline for n days including retweets
    tweet_nr = 0
    for tweet in tweepy.Cursor(api.user_timeline, screen_name=username, tweet_mode='extended', include_rts=True).items():
        tweet_nr += 1
        if within_time_window:
            if max_tweets > 0 and tweet_nr > max_tweets:
                break
            if tweet.id not in parsed_tweets:
                if tweet.created_at > cutoff_time:
                    parsed_tweets.append(tweet.id)
                    
                    # If tweet is a quote, get the quoted tweet full text
                    if tweet.is_quote_status:
                        quoted_tweet = api.get_status(tweet.quoted_status_id, tweet_mode='extended')
                        conversation = [tweet.user.screen_name + ", " + tweet.id_str + ": " + tweet.full_text + " (quoted tweet: " + quoted_tweet.user.screen_name + ", " + quoted_tweet.full_text + ")"]

                    else:
                        conversation = [tweet.user.screen_name + ", " + tweet.id_str + ": " + tweet.full_text]

                    
                    if tweet.in_reply_to_status_id:
                        get_conversation(tweet.in_reply_to_status_id, conversation, parsed_tweets)

                    all_tweets.append(conversation[::-1])  # Reverse the conversation order (oldest to newest)
                else:
                    # Set the flag to False when a tweet's created_at is older than the cutoff_time
                    within_time_window = False
        else:
            break
    
    text_length = 0
    for conversation in all_tweets:
        for tweet in conversation:
            text_length += len(tweet.split())

    return all_tweets, text_length

def print_conversation(conversation_list):
    for conversation in conversation_list:
        if(len(conversation) > 1):
            for tweet in conversation:
                print(tweet)
        else:
            print(conversation[0])
        print('\n--- End of conversation ---\n')

def print_user_activity(username, timewindowdays=1, max_tweets=-1):
    tweets = get_tweets_for_past_n_days(username, timewindowdays, max_tweets)
    print_conversation(tweets)

def return_user_activity(username, timewindowdays=1, max_tweets=-1):
    tweets, word_count = get_tweets_for_past_n_days(username, timewindowdays, max_tweets)
    return tweets, word_count
