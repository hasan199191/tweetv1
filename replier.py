import os
import requests
import json
from dotenv import load_dotenv
from logging import getLogger
import time
from config import MONITORED_ACCOUNTS
from twitter_client import login, reply_to_tweet, browse_tweets_v2
from datetime import datetime, timedelta

# Initialize logger
logger = getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Gemini 2.0 Flash API endpoint
GEMINI_FLASH_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

PROMPT_REPLY = """
You are a Web3 analyst and Twitter engager. Generate a unique, engaging, and contextual reply to the following tweet about Web3.

Guidelines:
- Keep the reply under 240 characters
- Be specific to the tweet's content
- Add value to the discussion
- Be professional but friendly
- Use relevant technical terms when appropriate
- Never repeat previous replies
- Never use generic responses
- Reference specific points from the tweet
- Ask thoughtful questions when relevant
"""

def generate_reply(text):
    """Generate a contextual reply using Gemini 2.0 Flash API"""
    try:
        prompt = f"{PROMPT_REPLY}\n\nTweet: {text}\n\nGenerate a reply that directly addresses the specific content and context of this tweet."
        
        # Prepare the request payload
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        # Make the API request
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            GEMINI_FLASH_ENDPOINT,
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        
        if not result or 'candidates' not in result or not result['candidates']:
            logger.error("Empty response from Gemini API")
            return None
            
        # Extract the generated text
        generated_text = result['candidates'][0]['content']['parts'][0]['text']
        
        if not generated_text:
            logger.error("No text in Gemini API response")
            return None

        reply = generated_text.strip()
        logger.info(f"Generated reply for tweet: {reply}")
        return reply[:240]  # Ensure we stay within Twitter's limit

    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error generating reply: {e}")
        return None

def run_replier():
    browser, page = login()
    for tweet in get_tweets():
        reply = generate_reply(tweet['text'])
        if reply:
            reply_to_tweet(page, tweet['url'], reply)
        time.sleep(3)  # Add delay between replies
    browser.close()

def reply_to_tracked_accounts(page):
    """Reply to monitored Twitter accounts"""
    try:
        for account in MONITORED_ACCOUNTS:
            logger.info(f"Checking tweets from {account}...")
            tweets = browse_tweets_v2(page, account)
            if tweets:
                for tweet in tweets:
                    reply = generate_reply(tweet['text'])
                    if reply:
                        reply_to_tweet(page, tweet['url'], reply)
                        time.sleep(3)  # Add delay between replies
    except Exception as e:
        logger.error(f"Error replying to tracked accounts: {e}")

def get_tweets():
    """Fetch tweets from monitored accounts."""
    try:
        # Placeholder logic for fetching tweets
        # Replace with actual implementation using `browse_tweets_v2`
        tweets = [
            {"text": "Example tweet text", "url": "https://twitter.com/example/status/12345", "timestamp": "2025-06-17T12:00:00"}
        ]
        return tweets
    except Exception as e:
        logger.error(f"Error fetching tweets: {e}")
        return []