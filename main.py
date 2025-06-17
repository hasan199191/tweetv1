import os
import sys
import time
import json
import random
import logging
import schedule
import traceback
import re  # Akıllı içerik bölme için eklendi
# import openai  # Bu satırı tamamen kaldırın
import importlib  # importlib import'u eklendi
import google.generativeai as genai
from dotenv import load_dotenv  # Eksik import eklendi
from twitter_client import login, post_tweet, post_tweet_thread_v2, post_manual_thread, reply_to_tweet, browse_tweets_v2, human_like_delay, cleanup_browser, initialize_browser
from datetime import datetime, timedelta

# Logging configuration
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("web3bot.log"), 
                             logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# OpenAI yapılandırma kodunu kaldırın
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if OPENAI_API_KEY:
#     openai.api_key = OPENAI_API_KEY

# Configure Gemini API  
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Global browser and page objects
browser = None
page = None

# Twitter accounts to monitor
MONITORED_ACCOUNTS = [
    "0x_ultra", "0xBreadguy", "beast_ico", "mdudas", "lex_node", 
    "jessepollak", "0xWenMoon", "ThinkingUSD", "udiWertheimer", 
    "vohvohh", "NTmoney", "0xMert_", "QwQiao", "DefiIgnas", 
    "notthreadguy", "Chilearmy123", "Punk9277", "DeeZe", "stevenyuntcap",
    "chefcryptoz", "ViktorBunin", "ayyyeandy", "andy8052", "Phineas_Sol",
    "MoonOverlord", "NarwhalTan", "theunipcs", "RyanWatkins_", 
    "aixbt_agent", "ai_9684xtpa", "icebergy_", "Luyaoyuan1", 
    "stacy_muur", "TheOneandOmsy", "jeffthedunker", "JoshuaDeuk", 
    "0x_scientist", "inversebrah", "dachshundwizard", "gammichan",
    "sandeepnailwal", "segall_max", "blknoiz06", "0xmons", "hosseeb",
    "GwartyGwart", "JasonYanowitz", "Tyler_Did_It", "laurashin",
    "Dogetoshi", "benbybit", "MacroCRG", "Melt_Dem"
]

# Keywords to look for in tweets
KEYWORDS = [
    "0G", "Allora", "ANIME", "Aptos", "Arbitrum", "Berachain", "Boop", 
    "Caldera", "Camp Network", "Corn", "Defi App", "dYdX", "Eclipse", 
    "Fogo", "Frax", "FUEL", "Huma", "Humanity Protocol", "Hyperbolic", 
    "Initia", "Injective", "Infinex", "IQ", "Irys", "Kaia", "Kaito", 
    "Katana", "Kinto", "Lombard", "MANTRA", "Mantle", "MapleStory Universe", 
    "MegaETH", "Mitosis", "Monad", "Movement", "Multibank", "Multipli", 
    "Near", "Newton", "Novastro", "OpenLedger", "PARADEX", "PENGU", 
    "Polkadot", "Portal to BTC", "PuffPaw", "Pyth", "QUAI", "SatLayer", 
    "Sei", "Sidekick", "Skate", "Somnia", "Soon", "Soph Protocol", 
    "Soul Protocol", "Starknet", "Story", "Succinct", "Symphony", 
    "Theoriq", "Thrive Protocol", "Union", "Virtuals Protocol", "Wayfinder", 
    "XION", "YEET", "Zcash"
]

# Projects for content creation
PROJECTS = [
    {"name": "Allora", "twitter": "@AlloraNetwork", "website": "allora.network"},
    {"name": "Caldera", "twitter": "@Calderaxyz", "website": "caldera.xyz"},
    {"name": "Camp Network", "twitter": "@campnetworkxyz", "website": "campnetwork.xyz"},
    {"name": "Eclipse", "twitter": "@EclipseFND", "website": "eclipse.builders"},
    {"name": "Fogo", "twitter": "@FogoChain", "website": "fogo.io"},
    {"name": "Humanity Protocol", "twitter": "@Humanityprot", "website": "humanity.org"},
    {"name": "Hyperbolic", "twitter": "@hyperbolic_labs", "website": "hyperbolic.xyz"},
    {"name": "Infinex", "twitter": "@infinex", "website": "infinex.xyz"},
    {"name": "Irys", "twitter": "@irys_xyz", "website": "irys.xyz"},
    {"name": "Katana", "twitter": "@KatanaRIPNet", "website": "katana.network"},
    {"name": "Lombard", "twitter": "@Lombard_Finance", "website": "lombard.finance"},
    {"name": "MegaETH", "twitter": "@megaeth_labs", "website": "megaeth.com"},
    {"name": "Mira Network", "twitter": "@mira_network", "website": "mira.network"},
    {"name": "Mitosis", "twitter": "@MitosisOrg", "website": "mitosis.org"},
    {"name": "Monad", "twitter": "@monad_xyz", "website": "monad.xyz"},
    {"name": "Multibank", "twitter": "@multibank_io", "website": "multibank.io"},
    {"name": "Multipli", "twitter": "@multiplifi", "website": "multipli.fi"},
    {"name": "Newton", "twitter": "@MagicNewton", "website": "newton.xyz"},
    {"name": "Novastro", "twitter": "@Novastro_xyz", "website": "novastro.xyz"},
    {"name": "Noya.ai", "twitter": "@NetworkNoya", "website": "noya.ai"},
    {"name": "OpenLedger", "twitter": "@OpenledgerHQ", "website": "openledger.xyz"},
    {"name": "PARADEX", "twitter": "@tradeparadex", "website": "paradex.trade"},
    {"name": "Portal to BTC", "twitter": "@PortaltoBitcoin", "website": "portaltobitcoin.com"},
    {"name": "Puffpaw", "twitter": "@puffpaw_xyz", "website": "puffpaw.xyz"},
    {"name": "SatLayer", "twitter": "@satlayer", "website": "satlayer.xyz"},
    {"name": "Sidekick", "twitter": "@Sidekick_Labs", "website": "N/A"},
    {"name": "Somnia", "twitter": "@Somnia_Network", "website": "somnia.network"},
    {"name": "Soul Protocol", "twitter": "@DigitalSoulPro", "website": "digitalsoulprotocol.com"},
    {"name": "Succinct", "twitter": "@succinctlabs", "website": "succinct.xyz"},
    {"name": "Symphony", "twitter": "@SymphonyFinance", "website": "app.symphony.finance"},
    {"name": "Theoriq", "twitter": "@theoriq_ai", "website": "theoriq.ai"},
    {"name": "Thrive Protocol", "twitter": "@thriveprotocol", "website": "thriveprotocol.com"},
    {"name": "Union", "twitter": "@union_build", "website": "union.build"},
    {"name": "YEET", "twitter": "@yeet", "website": "yeet.com"}
]

def reload_modules():
    """Reload modules for development"""
    try:
        importlib.reload(importlib.import_module('twitter_client'))
        logger.info("Modules reloaded")
    except Exception as e:
        logger.error(f"Module reload error: {e}")

def initialize_browser():
    """Initialize browser and set global variables"""
    global browser, page
    
    try:
        if browser is None:
            logger.info("Initializing browser...")
            browser, page = login()
            logger.info("Browser initialized and logged in to Twitter")
        else:
            logger.info("Browser already running")
            
            # Check if page is still open
            try:
                # Simple check - get URL
                current_url = page.url
                logger.info(f"Current page URL: {current_url}")
            except Exception as e:
                logger.warning(f"Page check error: {e}")
                logger.info("Opening new page...")
                page = browser.new_page()
                page.goto("https://twitter.com/home")
    except Exception as e:
        logger.error(f"Browser initialization error: {e}")
        # Clean up old session and restart
        try:
            cleanup_browser()
            browser, page = login()
            logger.info("Browser restarted")
        except Exception as restart_e:
            logger.error(f"Failed to restart browser: {restart_e}")
            raise  # Re-raise to handle in main
        
    return browser, page

def cleanup_browser():
    """Close browser cleanly"""
    global browser, page
    
    try:
        if browser is not None:
            logger.info("Closing browser...")
            browser.close()
            browser = None
            page = None
            logger.info("Browser closed")
    except Exception as e:
        logger.error(f"Browser closing error: {e}")
        browser = None
        page = None

def check_tweets_and_reply():
    """Check tweets from all specified accounts and reply to recent ones"""
    try:
        logger.info("Starting tweet monitoring and reply task...")
        
        # Initialize browser or use existing session
        browser, page = initialize_browser()
        
        # Track which tweets we've already replied to
        replied_tweets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replied_tweets.json")
        
        # Load previously replied tweets
        replied_tweets = {}
        try:
            if os.path.exists(replied_tweets_file):
                with open(replied_tweets_file, 'r') as f:
                    replied_tweets = json.load(f)
                    
                # Keep tweets from last 24 hours only
                current_time = time.time()
                for tweet_url, reply_time in list(replied_tweets.items()):
                    if current_time - reply_time > 24 * 3600:  # 24 hours in seconds
                        del replied_tweets[tweet_url]
        except Exception as e:
            logger.error(f"Error loading replied tweets: {e}")
            replied_tweets = {}
        
        # Get one hour ago timestamp for checking recent tweets
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        # Process each monitored account
        for account in MONITORED_ACCOUNTS:
            logger.info(f"Checking tweets from {account}...")
            
            # Get recent tweets (limit to 10)
            tweets = browse_tweets_v2(page, account, limit=10)
            
            if not tweets:
                logger.warning(f"No tweets found for {account}")
                continue
            
            # Find tweets from the last hour that we haven't replied to yet
            new_tweets = []
            for tweet in tweets:
                if 'url' in tweet and tweet['url'] not in replied_tweets:
                    # Try to parse the tweet timestamp
                    tweet_time = None
                    if 'timestamp' in tweet:
                        try:
                            tweet_time = datetime.strptime(tweet['timestamp'], "%Y-%m-%dT%H:%M:%S")
                        except:
                            # If timestamp parsing fails, assume it's recent
                            tweet_time = datetime.now()
                    
                    # If we can't determine time or it's recent, include it
                    if tweet_time is None or tweet_time > one_hour_ago:
                        new_tweets.append(tweet)
            
            # Reply to new tweets
            if new_tweets:
                logger.info(f"Found {len(new_tweets)} new tweets from {account} in the last hour")
                
                for tweet in new_tweets:
                    # Generate reply for the tweet using Gemini (OpenAI değil)
                    reply_text = generate_web3_reply(tweet['text'])  # _with_gemini kaldırıldı
                    logger.info(f"Generated reply for {account}: {reply_text}")
                    
                    # Send the reply
                    if 'url' in tweet:
                        success = reply_to_tweet(page, tweet['url'], reply_text)
                        if success:
                            logger.info(f"Reply successfully sent to {account}: {tweet['url']}")
                            # Mark this tweet as replied
                            replied_tweets[tweet['url']] = time.time()
                        else:
                            logger.error(f"Reply failed for {account}: {tweet['url']}")
                        
                        # Avoid detection by adding delay
                        human_like_delay(15000, 30000)  # Longer delay between replies
                    else:
                        logger.error(f"No URL found for {account}'s tweet, can't reply")
            else:
                logger.info(f"No new tweets found for {account} in the last hour")
            
            # Small delay between checking different accounts
            human_like_delay(3000, 5000)
            
        # Save updated replied tweets
        try:
            # Make sure directory exists
            os.makedirs(os.path.dirname(replied_tweets_file), exist_ok=True)
            with open(replied_tweets_file, 'w') as f:
                json.dump(replied_tweets, f)
        except Exception as e:
            logger.error(f"Error saving replied tweets: {e}")
        
    except Exception as e:
        logger.error(f"Tweet check error: {e}")
        traceback.print_exc()

def post_web3_content():
    """Post a tweet about a random Web3 project"""
    try:
        # Choose a random project from our list
        project = random.choice(PROJECTS)
        logger.info(f"Selected project for posting: {project['name']}")
        
        # Get content using Gemini
        content = generate_web3_content(project)  # Artık bir tweet listesi döndürür
        
        # Check if we have a valid page
        global browser, page
        if page is None:
            logger.warning("Page is None, initializing browser...")
            browser, page = initialize_browser()
        
        # Post the tweet(s)
        logger.info(f"Posting tweet about {project['name']}")
        
        # If there's only one tweet, use post_tweet
        if len(content) == 1:
            success = post_tweet(page, content[0])
        # If multiple tweets (a thread), use post_tweet_thread_v2
        else:
            success = post_tweet_thread_v2(page, content)
        
        if success:
            logger.info(f"Successfully posted tweet(s) about {project['name']}")
        else:
            logger.error(f"Failed to post tweet(s) about {project['name']}")
            
        return success
    except Exception as e:
        logger.error(f"Error in post_web3_content: {e}")
        traceback.print_exc()
        return False

def debug_thread():
    """Debug function to test thread creation"""
    try:
        # Initialize browser
        browser, page = initialize_browser()
        
        # Create test content
        test_tweets = [
            "This is tweet #1 in our test thread. Testing Twitter's thread functionality with Playwright automation. #Testing #Automation",
            "This is tweet #2 in our thread. The problem is with finding and clicking the '+ Add' button to create a thread. Let's see if our improved code works!",
            "This is tweet #3, the final one in our test thread. If you're seeing this as part of a thread, the fix was successful!"
        ]
        
        # Try to create a thread
        success = post_tweet_thread_v2(page, test_tweets)
        
        if success:
            logger.info("Thread test appears successful!")
        else:
            logger.error("Thread test failed")
            
    except Exception as e:
        logger.error(f"Thread debug error: {e}")
        traceback.print_exc()
    finally:
        # Clean up when script exits
        cleanup_browser()

def split_content_intelligently(content, max_length=280):
    """Split content into tweets at appropriate sentence boundaries without any numbering"""
    if len(content) <= max_length:
        return [content]
    
    # Split by paragraph first
    paragraphs = content.split('\n\n')
    tweets = []
    current_tweet = ""
    
    for paragraph in paragraphs:
        # If a single paragraph is too long, need to split it by sentences
        if len(paragraph) > max_length:
            # Split into sentences (consider multiple punctuation marks)
            sentences = []
            for sent in re.split(r'(?<=[.!?])\s+', paragraph):
                if sent:
                    sentences.append(sent)
            
            for sentence in sentences:
                # If single sentence is too long (rare but possible)
                if len(sentence) > max_length:
                    # Split by commas or other natural breaks
                    fragments = []
                    for fragment in re.split(r'(?<=[:;,])\s+', sentence):
                        if fragment:
                            fragments.append(fragment)
                    
                    for fragment in fragments:
                        if len(current_tweet + (" " if current_tweet else "") + fragment) <= max_length:
                            if current_tweet:
                                current_tweet += " "
                            current_tweet += fragment
                        else:
                            tweets.append(current_tweet)
                            current_tweet = fragment
                else:
                    # Normal sentence
                    if len(current_tweet + (" " if current_tweet else "") + sentence) <= max_length:
                        if current_tweet:
                            current_tweet += " "
                        current_tweet += sentence
                    else:
                        tweets.append(current_tweet)
                        current_tweet = sentence
        else:
            # Whole paragraph might fit
            if len(current_tweet + ("\n\n" if current_tweet else "") + paragraph) <= max_length:
                if current_tweet:
                    current_tweet += "\n\n"
                current_tweet += paragraph
            else:
                tweets.append(current_tweet)
                current_tweet = paragraph
    
    # Don't forget the last tweet
    if current_tweet:
        tweets.append(current_tweet)
    
    # Clean up any empty tweets
    tweets = [t for t in tweets if t.strip()]
    
    # Final length check - make sure no tweet exceeds max_length
    for i, tweet in enumerate(tweets):
        if len(tweet) > max_length:
            # If a tweet is still too long, truncate at max_length-3 and add ellipsis
            tweets[i] = tweet[:max_length-3] + "..."
    
    return tweets

def generate_web3_content(project):
    """Generate intelligent content about a Web3 project using Gemini"""
    try:
        # Get project details
        name = project["name"]
        twitter = project.get("twitter", "")
        website = project.get("website", "")
        
        # Create detailed prompt
        prompt = f"""As a Web3/crypto expert, create an insightful, educational tweet about {name} ({twitter}, {website}).
        
        DO NOT simply say "Check out {name}" or just mention their website.
        
        Instead, focus on:
        1. A specific innovative technical feature they're developing
        2. Recent achievements or milestones they've reached
        3. How they're solving a particular problem in the crypto/web3 ecosystem
        4. Their competitive advantage compared to similar projects
        5. Recent partnerships or integrations worth noting
        
        Make it sound like you've actually researched and understand the project deeply.
        Include relevant technical terms that show expertise.
        Mention at least one specific feature or aspect of the project that's not obvious.
        If appropriate, include a thought-provoking question at the end.
        
        IMPORTANT: ALWAYS include the project's Twitter handle {twitter} in your tweet.
        Add relevant hashtags.
        
        Keep it conversational but informative - like a knowledgeable friend explaining something interesting.
        DO NOT use generic descriptions or cliché phrases like "innovative project in Web3 space".
        
        The tweet should be valuable to both newcomers and experienced crypto users.
        Focus on being EDUCATIONAL and INSIGHTFUL rather than promotional.
        
        IMPORTANT: Keep your content under 280 characters total if possible.
        """
        
        # Use Gemini 2.0 Flash model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Model system prompt to instruct the model about its role
        system_instruction = """You are a senior blockchain researcher and Web3 expert with deep technical knowledge of crypto projects.
        Your goal is to create educational, insightful content that demonstrates genuine expertise.
        Never be generic or promotional. Never use numbering like (1/2), and avoid basic phrases like 'Check out this project'.
        Keep your content concise and under Twitter's 280 character limit if possible.
        
        IMPORTANT: Always include the project's Twitter handle in your tweet.
        """
        
        # Configure generation settings (equivalent to temperature, etc.)
        generation_config = {
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 32,
            "max_output_tokens": 600,
        }
        
        # Create the chat session with system instructions
        chat = model.start_chat(history=[])
        
        # Generate content with system instruction
        response = chat.send_message(
            f"{system_instruction}\n\n{prompt}",
            generation_config=generation_config
        )
        
        # Extract content
        content = response.text.strip()
        
        # Clean up the text
        content = re.sub(r'\(\d+\/\d+\)', '', content)
        content = re.sub(r'\d+\/\d+', '', content)
        content = re.sub(r'This is a single tweet.*?characters\.', '', content, flags=re.IGNORECASE)
        content = re.sub(r'No need for a thread\.', '', content, flags=re.IGNORECASE)
        
        # Force include Twitter handle if not present
        if twitter and twitter not in content:
            if len(content) <= 250:
                content = f"{content} {twitter}"
            else:
                # If already too long, try to replace a mention of the project name with the Twitter handle
                name_pattern = re.compile(re.escape(name), re.IGNORECASE)
                if name_pattern.search(content):
                    content = name_pattern.sub(twitter, content, count=1)
        
        # Check if content exceeds Twitter's character limit and split if needed
        if len(content) > 280:
            logger.info(f"Content too long ({len(content)} chars), splitting into thread...")
            split_tweets = split_content_intelligently(content)
            return split_tweets
        
        return [content]  # Return as list for consistency
    except Exception as e:
        logger.error(f"Error generating content with Gemini: {e}")
        # Fallback content
        fallback = f"{name}'s {twitter} approach to {random.choice(['scaling', 'security', 'interoperability', 'data availability', 'decentralized computing'])} addresses key challenges in the ecosystem. Visit {website} for technical details. #Web3 #{name}"
        return [fallback]  # Return as list for consistency

def generate_web3_reply(original_tweet_text):
    """Generate an insightful, expert-level reply to a tweet related to Web3 using Gemini"""
    try:
        # Create a detailed prompt for AI
        prompt = f"""As a Web3/crypto expert, write an insightful, thoughtful reply to this tweet:
        
        "{original_tweet_text}"
        
        Follow these guidelines:
        
        1. Show deep knowledge of the crypto/Web3 ecosystem
        2. Bring up a specific related point that wasn't mentioned in the original tweet
        3. If appropriate, mention relevant technology, token economics, or governance aspects
        4. Be conversational but demonstrate expertise
        5. If possible, reference broader industry trends or how this relates to other projects
        6. Ask a thoughtful question that adds to the discussion (not just "what do you think?")
        7. Keep under 280 characters
        8. DO NOT introduce yourself or mention you're an AI
        9. Never use generic phrases like "interesting project" or "great potential"
        10. DO NOT add any numbering like (1/2) or notes about character limits
        
        Make your reply technically accurate, insightful and valuable to the conversation.
        """
        
        # Use a more advanced model if available
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a senior blockchain developer and Web3 expert with years of hands-on experience building crypto projects. You provide technically accurate, insightful comments that demonstrate deep understanding. Never be generic, promotional, or obvious."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.8,
            presence_penalty=0.6,
            frequency_penalty=0.6
        )
        
        # Extract and clean the content
        content = response.choices[0].message["content"].strip()
        content = re.sub(r'\(\d+\/\d+\)', '', content)
        content = re.sub(r'\d+\/\d+', '', content)
        content = re.sub(r'This is a single tweet.*?characters\.', '', content, flags=re.IGNORECASE)
        content = re.sub(r'No need for a thread\.', '', content, flags=re.IGNORECASE)
        
        # Ensure the reply is not too long
        if len(content) > 280:
            # Try to smartly truncate at a sentence boundary
            sentences = re.split(r'(?<=[.!?])\s+', content)
            truncated_content = ""
            for sentence in sentences:
                if len(truncated_content + sentence) <= 270:  # Leave room for ellipsis
                    truncated_content += sentence + " "
                else:
                    break
            content = truncated_content.strip() + "..."
        
        return content
    
    except Exception as e:
        logger.error(f"Error generating reply: {e}")
        # More thoughtful fallback replies
        fallback_replies = [
            "The intersection of your point with zk-proofs and data availability layer tech is fascinating. Have you seen similar approaches in other L2s?",
            "This aligns with recent governance experiments in DeFi. The balance between decentralization and execution speed remains challenging.",
            "Your analysis overlooks the composability aspects. How do you see this working with cross-chain protocols?",
            "MEV implications here are significant. Would be interesting to see how sandwich attack resistance develops in this model.",
            "The tokenomics you're describing has parallels to recent research on sustainable validator incentives. Worth exploring further."
        ]
        return random.choice(fallback_replies)

def perform_browser_health_check():
    """Check browser health and restart if necessary"""
    global browser, page
    
    try:
        logger.info("Performing browser health check...")
        
        # Check if browser is still responsive
        if browser is None or page is None:
            logger.warning("Browser or page is None, restarting...")
            cleanup_browser()
            browser, page = initialize_browser()
            return
        
        # Try to navigate to a simple page
        try:
            page.goto("https://twitter.com/home", timeout=30000)
            current_url = page.url
            logger.info(f"Browser check: Current URL is {current_url}")
            
            # Check if we're still logged in
            if "login" in current_url.lower():
                logger.warning("No longer logged in, re-initializing...")
                cleanup_browser()
                browser, page = initialize_browser()
                return
                
        except Exception as e:
            logger.error(f"Browser navigation error: {e}")
            logger.warning("Restarting browser due to navigation issues...")
            cleanup_browser()
            browser, page = initialize_browser()
            return
            
        logger.info("Browser health check completed: Browser is healthy")
        
    except Exception as e:
        logger.error(f"Browser health check error: {e}")
        # Try to recover
        try:
            cleanup_browser()
            browser, page = initialize_browser()
            logger.info("Browser reinitialized after health check failure")
        except Exception as recover_e:
            logger.error(f"Recovery after health check failed: {recover_e}")

def main():
    try:
        # Global variables for browser session
        global playwright, browser, page
        
        logger.info("Browser initialization attempt 1 of 3")
        logger.info("Initializing browser...")
        
        # Get playwright instance along with browser and page
        playwright, browser, page = login()
        
        if browser and page:
            logger.info("Browser initialized and logged in to Twitter")
            logger.info("Starting scheduled operation...")
            
            # Post content at specific hours to maximize engagement
            schedule.every().day.at("08:00").do(post_web3_content)  # Morning post
            schedule.every().day.at("12:30").do(post_web3_content)  # Lunch time post
            schedule.every().day.at("17:00").do(post_web3_content)  # Evening post
            schedule.every().day.at("20:00").do(post_web3_content)  # Night post
            
            # Check and reply to tweets every 2 hours
            for hour in range(0, 24, 2):
                schedule.every().day.at(f"{hour:02d}:15").do(check_tweets_and_reply)
            
            # Browser health check every 12 hours
            schedule.every(12).hours.do(perform_browser_health_check)
            
            # Initial run on startup
            post_web3_content()
            human_like_delay(5000, 10000)
            check_tweets_and_reply()
            
            # Main loop
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(60)
                except Exception as loop_e:
                    logger.error(f"Schedule loop error: {loop_e}")
                    # Try to recover
                    try:
                        cleanup_browser()
                        initialize_browser()
                        logger.info("Browser restarted after loop error")
                    except Exception as recover_e:
                        logger.error(f"Recovery failed: {recover_e}")
                        # Wait before next attempt
                        time.sleep(300)
    
        else:
            logger.error("Failed to initialize browser")
            
    except Exception as e:
        logger.error(f"Main error: {e}")
    
    finally:
        if 'browser' in globals() and browser:
            try:
                browser.close()
            except Exception as e:
                logger.error(f"Browser close error: {e}")
        if 'playwright' in globals() and playwright:
            try:
                playwright.stop()
            except Exception as e:
                logger.error(f"Playwright stop error: {e}")

# For testing different functions individually
def test_mode():
    test_feature = "combined"  # "browse", "check", "post", or "combined"
    
    try:
        # Initialize browser
        initialize_browser()
        
        if test_feature == "browse":
            # Just test tweet browsing
            logger.info("Starting tweet browsing test...")
            account = "elonmusk"  # Popular account with guaranteed tweets
            logger.info(f"Checking tweets from {account}...")
            tweets = browse_tweets_v2(page, account, limit=3)
            
            # Show found tweets
            for i, tweet in enumerate(tweets):
                logger.info(f"Tweet {i+1}: {tweet.get('text', '')[:100]}...")
                if 'url' in tweet:
                    logger.info(f"URL: {tweet['url']}")
            
        elif test_feature == "check":
            # Test tweet checking and replying
            logger.info("Starting tweet monitoring and reply test...")
            check_tweets_and_reply()
        elif test_feature == "post":
            # Test content posting
            logger.info("Starting content posting test...")
            post_web3_content()
        elif test_feature == "combined":
            # Test all functionality
            logger.info("Starting combined test...")
            post_web3_content()
            human_like_delay(10000, 20000)
            check_tweets_and_reply()
        else:
            logger.warning(f"Invalid test type: {test_feature}")
            
    except Exception as e:
        logger.error(f"Test error: {e}")
        traceback.print_exc()
    finally:
        # Optionally close browser after testing
        cleanup_browser()

if __name__ == "__main__":
    # Set to False for testing individual functions
    production_mode = True
    
    # For production deployment:
    if production_mode:
        main()
    else:
        test_mode()