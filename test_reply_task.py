import logging
from datetime import datetime, timedelta
from main import initialize_browser
from twitter_client import browse_tweets_v2, reply_to_tweet, human_like_delay
from replier import generate_reply
import time

# Logging configuration
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# Track replied tweets persistently
replied_tweets = set()

def track_replied_tweets(tweet_url):
    """Add replied tweet URL to the tracking set."""
    replied_tweets.add(tweet_url)

async def reply_to_latest_tweet(account, browser, page):
    """Reply to the latest tweet of a single account."""
    try:
        logger.info(f"Navigating to profile of account: {account}")
        await page.goto(f"https://twitter.com/{account}")
        await human_like_delay(3000, 5000)

        # Locate the latest tweet
        tweets = await browse_tweets_v2(page, account, limit=1)
        if not tweets:
            logger.info(f"No tweets found for account: {account}")
            return

        latest_tweet = tweets[0]
        try:
            logger.info(f"Navigating to latest tweet URL: {latest_tweet['url']}")
            await page.goto(latest_tweet['url'])
            await human_like_delay(3000, 5000)

            # Generate reply
            reply_text = generate_reply(latest_tweet['text'])
            logger.info(f"Generated reply: {reply_text[:50]}...")

            # Post reply
            success = await reply_to_tweet(page, latest_tweet['url'], reply_text)
            if success:
                logger.info(f"Successfully replied to tweet from {account}")
            else:
                logger.error(f"Failed to reply to tweet from {account}")
        except Exception as tweet_error:
            logger.error(f"Error processing latest tweet from {account}: {tweet_error}")

    except Exception as e:
        logger.error(f"Error in reply_to_latest_tweet for account {account}: {e}")

if __name__ == "__main__":
    import asyncio

    async def main():
        try:
            browser, page = await initialize_browser()
            if not browser or not page:
                logger.error("Failed to initialize browser")
                return

            for account in MONITORED_ACCOUNTS:
                try:
                    await reply_to_latest_tweet(account, browser, page)
                    await human_like_delay(5000, 8000)  # Add delay between accounts
                except Exception as e:
                    logger.error(f"Error processing account {account}: {e}")
                    continue

            await browser.close()
        except Exception as e:
            logger.error(f"Main execution error: {e}")

    asyncio.run(main())
