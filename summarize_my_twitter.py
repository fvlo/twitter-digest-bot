from get_user_activity import return_user_activity
from send_email import send_email
import openai
import math
from pathlib import Path

def read_secrets(file_path):
    secrets = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split(' = ')
            secrets[key] = value
    return secrets

secrets = read_secrets('secrets.txt')

# Set up your API key
api_key = secrets['OPENAI_API_KEY']
openai.api_key = api_key

PRICE_PER_TOKEN = 0.002 / 1000
WORD_TO_TOKEN_RATIO = 0.5
PROMPT_INSTRUCTION = "you will be given a list of a twitter conversations by a 'focus_tweeter'; \
    your task is to summarize the content as paragraphs of text in an executive summary style; \
    summarize each conversation thread separately; \
    add a URL to the focus_tweeter's last tweet of each conversation; \
    Make it clear what conversation the URL refers to.; \
    only summarize the content given without adding to it; \
    do not use bullet points; \
    use HTML tags to give structure to the text; \
    begin each summary paragraph with a short descriptive title. Wrap the title it in a <h4> tag and the paragraph in a <p>; \
    answer in english; \
    "

def get_config(file_path):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split(' = ')
            config[key] = value
    return config


def split_list(lst, n):
    avg = len(lst) // n
    rem = len(lst) % n
    result = []
    i = 0

    for _ in range(n):
        size = avg + (1 if rem > 0 else 0)
        result.append(lst[i:i + size])
        i += size
        rem -= 1

    return result

# Function to get summary for given users, number of days and maximum number of tweets
def get_summary(users, days, max_tweets=-1):
    
    
    
    if type(users) == str:
        users = [users]
    
    # Get user activity
    user_activies = []
    
    
    # Get the absolute path of the current script's directory
    script_directory = Path(__file__).resolve().parent
    
    print('\n')
    print('Welcome to the Twitter Digest Bot!')
    print(f'The current working directory is {script_directory}')
    print(f'The configuration file is {script_directory}/config.txt')
    print('\n')
    
    print(f"Retrieving tweets for the following users: {*users,}")
    print("Please wait...")
    print('\n')
    for user in users:
        try:
            user_activity, word_count = return_user_activity(user, days, max_tweets)
            user_activies.append((user, user_activity, word_count))
        except:
            print(f"There was an error while retrieving tweets for user {user}")
            user_activity = f"There was an error while retrieving tweets for user {user}"
            word_count = 0
            user_activies.append((user, user_activity, word_count))

    # Estimate cost of summary. Pricing for gpt-3.5-turbo is $0.002 / 1K tokens
    price_per_word = PRICE_PER_TOKEN / WORD_TO_TOKEN_RATIO
    
    # Calculate total word count
    word_count = 0
    for user_activity_and_word_count in user_activies:
        word_count += user_activity_and_word_count[2]
    
    cost_estimate = word_count * price_per_word
    
    # Ask for confirmation as user input
    input_confirmation = input(f"This summary request is expected to cost: {cost_estimate:.4f} dollars (i.e. {cost_estimate*100:.1f} dollar cents) for {len(user_activies)} user summaries. Answer 'y' to continue or with any other key to cancel.")
    print('\n')
    if input_confirmation != 'y':
        print("Summary request cancelled.")
        quit()
        
    
    cost_actual = 0
    summary = '<html>\n'

    
    for data_to_summarize in user_activies:
        try:
            user = data_to_summarize[0]
            user_activity = data_to_summarize[1]
            word_count = data_to_summarize[2]

            summary += f'<h3> <a href="https://www.twitter.com/{user}">@{user}</a> </h3>\n'
            
            if len(user_activity) == 0:
                summary += f"<p>@{user} does not have any twitter activity for the given period.</p>" + '\n\n'
                summary += f'<hr>\n'
                continue

            # If the word count is greater than 1000, split the request into multiple requests
            request_splits =  math.ceil(word_count / 1000)
            ##print(word_count, user_activies)
            user_activity_splits = split_list(user_activity, request_splits)


        
            split_nr = 0

            print(f"Starting summarization process for {user}...")
            
            summary += f'<body>\n'
            
            for split in user_activity_splits:
                # Get summary
                split_nr += 1
                print(f"Working on split {split_nr} of {len(user_activity_splits)}")
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": PROMPT_INSTRUCTION},
                        {"role": "user", "content": f"focus_tweeter: {user} ; {str(split)}" },
                    ],
                    temperature=0.5,
                )
                cost_actual += response.usage.total_tokens * PRICE_PER_TOKEN
                # Get summary
                summary += '<p>' + response.choices[0].message.content + '</p>\n'
            summary += f'</body>\n'
        except:
            print(f"There was an error retrieving the summary for user {data_to_summarize[0]}")
            summary += f"<p>There was an error retrieving the summary for user {data_to_summarize[0]}</p>" + '\n\n'
        
        summary += f'<hr>\n'

    
    summary += f"<p><em>The cost of this summary using OpenAI's API was {cost_actual:.4f} dollars (i.e. {cost_actual*100:.1f} dollar cents).</em></p>"
    summary += '</html>\n'
    
    summary_intro = f"<h1>Lately on twitter</h1>\n"
    summary_intro += f"<p>Here is your summary of the following users' twitter activity for the last {days} days or {max_tweets} most recent tweets:</p>\n"
    for user in users:
        summary_intro += f"<p><a href='https://www.twitter.com/{user}'>@{user}</a></p>\n"
    summary_intro += f'<hr>\n'
    
    summary = summary_intro + summary
    
    print('\n')
    print(f"Summary complete. Actual cost was {cost_actual:.4f} dollars (i.e. {cost_actual*100:.1f} dollar cents)")

    return summary
    

def summarize_my_twitter():
    
    config = get_config("config.txt")

    users = config['users'].split()
    days = int(config['days'])
    max_tweets = int(config['max_tweets'])
    to_email = config['to_email']

    summary = get_summary(users, days, max_tweets)

    subject = "Your summary from TwitterDigestBot"
    body_html = summary


    
    send_email(to_email = to_email, subject = subject, body_html=body_html)

if __name__ == "__main__":
    summarize_my_twitter()