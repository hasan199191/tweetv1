import os
import openai
from tweet_bot.twitter_client import login, reply_to_tweet
from tweet_bot.scraper import get_tweets

openai.api_key = os.getenv("GEMINI_API_KEY")

PROMPT_REPLY = """
You are a Web3 analyst and Twitter engager. Your job is to write a unique, insightful, human-like, informative, and professional reply to the following tweet about Web3. Be concise and engaging.
"""

def generate_reply(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": PROMPT_REPLY + "\n\nTweet: " + text}
        ]
    )
    return response.choices[0].message.content.strip()

def run_replier():
    browser, page = login()
    for tweet in get_tweets():
        reply = generate_reply(tweet['text'])
        reply_to_tweet(page, tweet['url'], reply)
    browser.close()