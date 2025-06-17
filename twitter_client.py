import os
import random
import time
import json
import pathlib
from playwright.sync_api import sync_playwright
import re  # Import re for regular expression operations
from email_reader import EmailReader
import logging

# Create directory to store browser session data
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_profile")
os.makedirs(USER_DATA_DIR, exist_ok=True)

logger = logging.getLogger(__name__)

def human_like_delay(min_ms=500, max_ms=1500):
    """Wait for a random amount of time like a human would"""
    delay = random.uniform(min_ms, max_ms) / 1000.0
    time.sleep(delay)

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

def cleanup_browser(browser):
    """Clean up browser instance"""
    try:
        if browser:
            browser.close()
            logger.info("Browser cleaned up successfully")
    except Exception as e:
        logger.error(f"Browser cleanup error: {e}")

def login(headless=False):
    """Login to Twitter with headless option"""
    try:
        p = sync_playwright().start()
        browser = p.chromium.launch_persistent_context(
            "./browser_data",
            headless=headless,
            viewport={'width': 1280, 'height': 720}
        )
        
        page = browser.new_page()
        logger.info("Checking login status...")
        
        page.goto("https://twitter.com/home", timeout=30000)
        time.sleep(3)
        
        if "home" in page.url and not "login" in page.url:
            logger.info("Already logged in")
            return browser, page
            
        # ... rest of login code ...
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        if 'browser' in locals():
            cleanup_browser(browser)
        return None, None

def post_tweet_thread_v2(page, content):
    """Post a thread of tweets"""
    try:
        print(f"Posting first tweet: {content[:50]}...")
        
        # Navigate to compose tweet
        page.goto("https://twitter.com/compose/tweet", wait_until="domcontentloaded")
        time.sleep(2)
        
        # Find and fill tweet input
        tweet_input = page.locator("div[data-testid='tweetTextarea_0']")
        if not tweet_input:
            print("Could not find text area for first tweet")
            return False
            
        tweet_input.fill(content)
        time.sleep(1)
        
        # Click tweet button
        post_button = page.locator("[data-testid='tweetButton']")
        if post_button:
            post_button.click()
            time.sleep(3)
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error posting thread: {e}")
        return False