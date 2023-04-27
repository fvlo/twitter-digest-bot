# Twitter Summary Bot 🤖🐦

Twitter Summary Bot is a Python script that generates an executive summary of specified users' Twitter activity for the past few days or their most recent tweets. It uses OpenAI's GPT-3.5-turbo to produce the summaries and emails the results to the specified email address.

## Features 🚀

- Fetches Twitter activity for specified users
- Summarizes Twitter conversations using OpenAI's GPT-3.5-turbo
- Estimates cost of GPT-3.5-turbo usage
- Sends the summary to an email address

## Installation 🛠️

1. Clone this repository:

```bash
git clone https://github.com/your_username/twitter-summary-bot.git
```
2. Install the required packages:

```bash
pip install -r requirements.txt
```


## Structure 📂

The project consists of three files:

1. `summarize_my_twitter.py`: The main script responsible for gathering user activity data, generating summaries using OpenAI's GPT-3.5-turbo model, and sending the summaries via email.
2. `get_user_activity.py`: Contains functions for fetching user activity data from Twitter.
3. `send_email.py`: Contains functions for sending an email using Gmail's SMTP server.

## Setup ⚙️

1. Create a secrets.txt file with your OpenAI API Key, Twitter API Key and Secret, Twitter Access Token and Secret, and Gmail account credentials:

```
OPENAI_API_KEY = your_openai_api_key
TWITTER_API_KEY = your_twitter_api_key
TWITTER_API_KEY_SECRET = your_twitter_api_key_secret
TWITTER_ACCESS_TOKEN = your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET = your_twitter_access_token_secret
SENDER_GMAIL_ACCOUNT = your_gmail_account
SENDER_GMAIL_APP_PASSWORD = your_gmail_app_password
```

2. Create a config.txt file with the users you want to summarize, the number of days to look back, the maximum number of tweets, and the recipient's email address:

```
users = user1 user2 user3
days = 2
max_tweets = 10
to_email = recipient@example.com
```

## Usage 🖥️

1. Run the script:

```bash
python summarize_my_twitter.py
```

2. Follow the prompts to confirm the estimated cost and wait for the summary to be generated and sent to the specified email address.


## License 📄

[MIT](LICENSE)