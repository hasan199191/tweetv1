import os
import random
import time
import json
import pathlib
from playwright.async_api import async_playwright
import re  # Import re for regular expression operations
from email_reader import EmailReader
import logging
import traceback
import asyncio

# Create directory to store browser session data
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_profile")
os.makedirs(USER_DATA_DIR, exist_ok=True)

logger = logging.getLogger(__name__)

async def human_like_delay(min_ms=500, max_ms=1500):
    """Simulate human-like delay between actions"""
    delay = random.randint(min_ms, max_ms) / 1000.0
    await asyncio.sleep(delay)

def type_like_human(page, selector, text):
    """Type text with human-like delays and patterns"""
    try:
        print("Using human-like typing...")
        # First click the element to focus it
        page.click(selector)
        
        # Clear existing text first (if any)
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        
        # Add a short pause before starting to type
        time.sleep(random.uniform(0.5, 1.5))
        
        # Split the text into words
        words = text.split()
        
        # Type each word with varying speed
        for i, word in enumerate(words):
            # Type the word with variable speed per character
            for char in word:
                # Typing speed varies: sometimes fast, sometimes slow
                delay = random.choice([
                    random.uniform(50, 100),  # Fast typing
                    random.uniform(100, 200),  # Medium speed
                    random.uniform(200, 350),  # Slower typing
                ])
                
                # Even slower for special characters to simulate "searching for the key"
                if char in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?":
                    delay *= 1.5
                
                page.keyboard.press(char)
                time.sleep(delay/1000.0)  # Convert to seconds
            
            # Add a space after each word (except the last one)
            if i < len(words) - 1:
                page.keyboard.press(" ")
                
                # Occasionally pause a bit longer between words
                if random.random() < 0.15:  # 15% chance
                    time.sleep(random.uniform(0.2, 0.7))
            
            # Occasionally pause a bit longer as if thinking
            if len(words) > 5 and random.random() < 0.05:  # 5% chance for longer texts
                time.sleep(random.uniform(0.8, 2.0))
        
        # Occasionally add a typo and correct it
        if len(text) > 25 and random.random() < 0.2:  # 20% chance of adding a typo
            # Go back a random number of characters
            chars_back = random.randint(5, min(15, len(text)))
            for _ in range(chars_back):
                page.keyboard.press("ArrowLeft")
            
            # Type a random wrong character
            wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")
            page.keyboard.press(wrong_char)
            
            # Wait a moment as if noticing the mistake
            time.sleep(random.uniform(0.3, 0.8))
            
            # Delete the wrong character
            page.keyboard.press("Backspace")
            
            # Type the correct character
            page.keyboard.press(text[-chars_back])
            
            # Move cursor back to end
            for _ in range(chars_back - 1):
                page.keyboard.press("ArrowRight")
        
        print(f"Human-like typing completed for text: {text[:30]}...")
        
    except Exception as e:
        print(f"Human-like typing error: {e}")
        # Fall back to regular typing
        try:
            page.fill(selector, "")  # Clear the field
            page.type(selector, text, delay=100)  # Type with some delay
        except Exception as fallback_e:
            print(f"Even fallback typing failed: {fallback_e}")

# Global variables for browser instance
browser = None
page = None

async def login(headless=False):
    """
    Login to Twitter with optional headless mode using Async API
    """
    try:
        p = await async_playwright().start()
        browser = await p.chromium.launch_persistent_context(
            "./browser_data",
            headless=headless,
            viewport={'width': 1280, 'height': 720}
        )

        # Open a new page
        page = await browser.new_page()
        await page.set_default_timeout(45000)  # Increase timeout to 45 seconds

        logger.info("Checking login status...")
        await page.goto("https://twitter.com/home", wait_until="networkidle")
        await asyncio.sleep(5)

        if "home" in page.url and not "login" in page.url:
            logger.info("Already logged in!")
            return browser, page

        # Login process
        try:
            logger.info("Navigating to login page...")
            await page.goto("https://twitter.com/i/flow/login", timeout=45000, wait_until="networkidle")
            await asyncio.sleep(3)

            # First step - enter username
            logger.info("Entering username...")
            username_input = await page.wait_for_selector("input[name='text']", state="visible", timeout=30000)
            if not username_input:
                raise Exception("Username input field not found")

            username = os.getenv("TWITTER_USERNAME", "chefcryptoz")
            logger.info(f"Entering username: {username}")
            await username_input.fill(username)
            await asyncio.sleep(2)

            # Click Next button
            logger.info("Looking for Next button...")
            next_button_selectors = [
                "div[role='button']:has-text('Next')",
                "div[data-testid='LoginForm_Forward_Button']",
                "div[role='button']",
                "span:has-text('Next')"
            ]

            if not await wait_for_and_click(page, next_button_selectors):
                logger.info("Next button not found, trying enter key...")
                await page.press("input[name='text']", "Enter")

            await asyncio.sleep(5)

            # Password entry
            logger.info("Entering password...")
            try:
                password_input = await page.wait_for_selector("input[name='password']", state="visible", timeout=30000)
                if not password_input:
                    raise Exception("Password input field not found")

                await human_like_delay(1000, 2000)
                password = os.getenv("TWITTER_PASSWORD", "Nuray1965+")
                await password_input.fill(password)
                await human_like_delay(1000, 2000)

                # Click login button
                login_button_selectors = [
                    "div[data-testid='LoginForm_Login_Button']",
                    "div[role='button']:has-text('Log in')",
                    "span:has-text('Log in')"
                ]

                if not await wait_for_and_click(page, login_button_selectors):
                    logger.info("Login button not found, trying enter key...")
                    await page.press("input[name='password']", "Enter")

                # Wait for homepage to load
                logger.info("Waiting for homepage to load...")
                try:
                    await page.wait_for_url(["**/home", "**/x.com/home"], timeout=45000)
                    await asyncio.sleep(5)
                    logger.info("Twitter session successfully opened")
                except Exception as e:
                    logger.warning(f"Homepage couldn't load: {e}")
                    await take_error_screenshot(page, "login_error.png")
            except Exception as e:
                logger.error(f"Password entry error: {e}")
                await take_error_screenshot(page, "password_error.png")
                raise e

            return browser, page

        except Exception as e:
            logger.error(f"Login error: {e}")
            await take_error_screenshot(page, "login_process_error.png")
            raise e

    except Exception as e:
        logger.error(f"Error during login: {e}")
        if 'page' in locals():
            await take_error_screenshot(page, "fatal_error.png")
        raise e

async def take_error_screenshot(page, filename):
    """Take a screenshot with proper error handling"""
    try:
        await page.screenshot(path=filename)
        logger.info(f"Error screenshot saved: {filename}")
    except Exception as e:
        logger.warning(f"Could not save screenshot {filename}: {e}")

async def cleanup_browser(browser):
    """Clean up browser instance and playwright"""
    try:
        if browser:
            await browser.close()
            logger.info("Browser instance closed")
    except Exception as e:
        logger.error(f"Browser cleanup error: {e}")

async def wait_for_and_click(page, selectors, timeout=5000):
    """Try multiple selectors to find and click a button"""
    for selector in selectors:
        try:
            button = await page.wait_for_selector(selector, timeout=timeout)
            if button:
                await button.click()
                return True
        except Exception:
            continue
    return False

async def post_tweet_thread_v2(page, content):
    """Post a tweet or thread of tweets with modern selectors"""
    try:
        # Click on tweet button
        tweet_button_selectors = [
            "[data-testid='SideNav_NewTweet_Button']",
            "[data-testid='tweetButtonInline']",
            "[href='/compose/tweet']"
        ]
        
        logger.info("Looking for tweet compose button...")
        if not await wait_for_and_click(page, tweet_button_selectors, timeout=10000):
            logger.error("Could not find tweet compose button")
            await take_error_screenshot(page, "compose_button_error.png")
            return False

        await asyncio.sleep(2)

        # Wait for and click the text area
        logger.info("Looking for tweet textarea...")
        textarea_selectors = [
            "[data-testid='tweetTextarea_0']",
            "div[role='textbox']",
            "[contenteditable='true']"
        ]

        textarea = None
        for selector in textarea_selectors:
            try:
                textarea = await page.wait_for_selector(selector, timeout=10000)
                if textarea:
                    logger.info(f"Found textarea with selector: {selector}")
                    break
            except Exception:
                continue

        if not textarea:
            logger.error("Could not find tweet textarea")
            await take_error_screenshot(page, "textarea_missing.png")
            return False

        # If content is a string, convert it to a list
        if isinstance(content, str):
            content = [content]

        # Post each tweet in the thread
        for i, tweet_text in enumerate(content):
            try:
                logger.info(f"Posting tweet {i+1} of {len(content)}")
                
                # Clear existing text
                await textarea.click()
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
                await asyncio.sleep(1)

                # Type tweet text
                await textarea.fill(tweet_text)
                await asyncio.sleep(2)

                # Look for and click the tweet/post button
                post_button_selectors = [
                    "[data-testid='tweetButton']",
                    "div[role='button']:has-text('Post')",
                    "div[role='button']:has-text('Tweet')"
                ]

                if not await wait_for_and_click(page, post_button_selectors, timeout=10000):
                    logger.error("Could not find post button")
                    await take_error_screenshot(page, f"post_button_error_{i}.png")
                    return False

                # Wait between tweets in a thread
                await asyncio.sleep(3)

                # If there are more tweets, look for and click the Add button
                if i < len(content) - 1:
                    add_button_selectors = [
                        "[data-testid='addButton']",
                        "div[role='button']:has-text('Add')",
                        "span:has-text('Add')"
                    ]

                    if not await wait_for_and_click(page, add_button_selectors, timeout=10000):
                        logger.error("Could not find add button for thread")
                        await take_error_screenshot(page, f"add_button_error_{i}.png")
                        return False

                    await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error posting tweet {i+1}: {e}")
                await take_error_screenshot(page, f"tweet_error_{i}.png")
                return False

        logger.info("Successfully posted all tweets")
        return True

    except Exception as e:
        logger.error(f"Error in post_tweet_thread_v2: {e}")
        await take_error_screenshot(page, "tweet_thread_error.png")
        return False