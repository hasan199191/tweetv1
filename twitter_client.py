import os
import random
import time
import json
import pathlib
from playwright.sync_api import sync_playwright, expect
import re  # Import re for regular expression operations
from email_reader import EmailReader
import logging
import traceback

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

def login(headless=False):
    """
    Login to Twitter with optional headless mode
    """
    try:
        p = sync_playwright().start()
        browser = p.chromium.launch_persistent_context(
            "./browser_data",
            headless=headless,  # Now accepts headless parameter
            viewport={'width': 1280, 'height': 720}
        )
        
        # Open a new page
        page = browser.new_page()
        
        # First navigate to Twitter homepage
        try:
            print("Checking if already logged in...")
            page.goto("https://twitter.com/home", timeout=30000)
            human_like_delay(3000, 5000)
            
            # Check for home view indicators
            logged_in = False
            
            # Check URL first - fastest method
            if "home" in page.url or page.url.endswith("twitter.com") or page.url.endswith("x.com") or "x.com/home" in page.url:
                print(f"Current URL: {page.url} - looks like a logged-in URL")
                
                # Take screenshot for debugging
                try:
                    page.screenshot(path="debug_login_check.png")
                    print("Debug screenshot saved")
                except Exception as e:
                    print(f"Screenshot error: {e}")
            
                # Further verify by checking for tweet compose button
                try:
                    compose_selectors = [
                        "a[data-testid='SideNav_NewTweet_Button']",
                        "div[role='button'][data-testid='tweetButtonInline']",
                        "a[href='/compose/tweet']"
                    ]
                    
                    for selector in compose_selectors:
                        if page.query_selector(selector):
                            print(f"Found tweet compose button: {selector}")
                            logged_in = True
                            break
                except Exception as e:
                    print(f"Error checking compose button: {e}")
                
                # Check for profile elements 
                try:
                    profile_selectors = [
                        "div[data-testid='AppTabBar_Profile_Link']",
                        "a[data-testid='AppTabBar_Profile_Link']",
                        "a[aria-label='Profile']"
                    ]
                    
                    for selector in profile_selectors:
                        if page.query_selector(selector):
                            print(f"Found profile element: {selector}")
                            logged_in = True
                            break
                except Exception as e:
                    print(f"Error checking profile elements: {e}")
                
                # Check for Twitter header
                try:
                    if page.query_selector("header[role='banner']"):
                        print("Found Twitter header")
                        
                        # Check if there's a logout button in sidebar
                        sidebar_text = page.query_selector("div[data-testid='sidebarColumn']")
                        if sidebar_text and "Log out" in sidebar_text.inner_text():
                            print("Found 'Log out' text in sidebar")
                            logged_in = True
                except Exception as e:
                    print(f"Error checking header: {e}")
            
            # If we're logged in, return the browser and page
            if logged_in:
                print("Already logged in, skipping login process")
                return browser, page
            
            print("Not logged in or couldn't confirm login status, proceeding with login...")
            
        except Exception as e:
            print(f"Error checking login status: {e}")
            # Continue with login process
        
        # Login process
        try:
            print("Navigating to login page...")
            page.goto("https://twitter.com/i/flow/login", timeout=30000)
            human_like_delay(2000, 3000)
            
            # First step - enter username instead of email
            print("Entering username...")
            page.wait_for_selector("input[name='text']", state="visible", timeout=15000)
            human_like_delay()
            
            # Use username from env
            username = os.getenv("TWITTER_USER", "chefcryptoz")
            print(f"Entering username: {username}")
            type_like_human(page, "input[name='text']", username)
            human_like_delay(1000, 2000)
            
            # Click Next button
            print("Looking for Next button...")
            next_button_selectors = [
                "div[role='button']:has-text('Next')",
                "div[data-testid='LoginForm_Forward_Button']"
            ]
            
            next_button_found = False
            for selector in next_button_selectors:
                try:
                    button = page.query_selector(selector)
                    if button:
                        print(f"Next button found: {selector}")
                        button.click()
                        next_button_found = True
                        break
                except Exception as e:
                    print(f"This selector couldn't be clicked {selector}: {e}")
            
            if not next_button_found:
                # Alternative - press enter
                print("Next button not found, trying enter key...")
                page.press("input[name='text']", "Enter")
            
            human_like_delay(3000, 5000)
            
            # Check for verification code prompt
            verify_selectors = [
                "input[data-testid='ocfEnterTextTextInput']",
                "div:has-text('Verification code')"
            ]
            
            for selector in verify_selectors:
                try:
                    if page.query_selector(selector):
                        print("Email verification code requested!")
                        # Access email to get verification code
                        verification_code = input("Please enter the verification code from your email: ")
                        
                        # Enter verification code
                        code_input_selectors = [
                            "input[data-testid='ocfEnterTextTextInput']",
                            "input[type='text']"
                        ]
                        
                        for input_selector in code_input_selectors:
                            try:
                                if page.query_selector(input_selector):
                                    type_like_human(page, input_selector, verification_code)
                                    page.press(input_selector, "Enter")
                                    break
                            except:
                                continue
                        
                        human_like_delay(3000, 5000)
                        break
                except:
                    continue
            
            # Password entry
            print("Entering password...")
            try:
                page.wait_for_selector("input[name='password']", state="visible", timeout=15000)
                human_like_delay()
                password = os.getenv("TWITTER_PASS", "Nuray1965+")
                type_like_human(page, "input[name='password']", password)
                human_like_delay(1000, 2000)
                
                # Click login button
                login_button_selectors = [
                    "div[data-testid='LoginForm_Login_Button']",
                    "div[role='button']:has-text('Log in')"
                ]
                
                login_button_found = False
                for selector in login_button_selectors:
                    try:
                        button = page.query_selector(selector)
                        if button:
                            button.click()
                            login_button_found = True
                            break
                    except:
                        pass
                
                if not login_button_found:
                    # Alternative - press enter
                    page.press("input[name='password']", "Enter")
                
                # Wait for homepage to load
                print("Waiting for homepage to load...")
                try:
                    page.wait_for_url(["**/home", "https://twitter.com", "https://x.com/home"], timeout=30000)
                    print("Twitter session successfully opened")
                except Exception as e:
                    print(f"Homepage couldn't load: {e}")
                    # Take screenshot
                    try:
                        page.screenshot(path="login_error.png")
                        print("Error screenshot saved: login_error.png")
                    except Exception as scr_e:
                        print(f"Could not save screenshot: {scr_e}")
            except Exception as e:
                print(f"Password entry error: {e}")
        
        except Exception as e:
            print(f"Login error: {e}")
            try:
                page.screenshot(path="login_process_error.png")
                print("Error screenshot saved: login_process_error.png")
            except Exception as scr_e:
                print(f"Could not save screenshot: {scr_e}")
        
        return browser, page
    except Exception as e:
        logger.error(f"Login error: {e}")
        return None, None

def get_verification_code():
    """Access email to get verification code"""
    print("\n*** VERIFICATION CODE NEEDED ***")
    print("Please check your email and enter the verification code manually.")
    code = input("Enter verification code: ")
    return code


def post_tweet(page, tweet_text):
    """Post a single tweet with human-like typing behavior"""
    print("Looking for tweet compose area...")
    
    # Click on tweet button
    tweet_button_selectors = [
        "a[data-testid='SideNav_NewTweet_Button']",
        "div[role='button'][data-testid='tweetButtonInline']",
        "a[href='/compose/tweet']"
    ]
    
    button_clicked = False
    for selector in tweet_button_selectors:
        try:
            button = page.query_selector(selector)
            if button:
                button.click()
                button_clicked = True
                print(f"Tweet button found: {selector}")
                break
        except Exception as e:
            print(f"Tweet button click error: {e}")
    
    if not button_clicked:
        print("Could not find tweet button")
        return False
    
    # Wait for tweet textbox
    human_like_delay(2000, 3000)
    
    print("Writing tweet...")
    
    # Type tweet content with human-like typing behavior
    textarea_selectors = [
        "div[data-testid='tweetTextarea_0']",
        "div[role='textbox'][contenteditable='true']",
        "div[aria-label='Post text']"
    ]
    
    text_area_found = False
    for selector in textarea_selectors:
        try:
            textarea = page.query_selector(selector)
            if textarea:
                # Use human-like typing function instead of direct typing
                type_like_human(page, selector, tweet_text)
                text_area_found = True
                break
        except Exception as e:
            print(f"Tweet text area error: {e}")
    
    if not text_area_found:
        print("Could not find tweet textarea")
        return False
    
    print("Sending tweet...")
    
    # Submit tweet
    submit_button_selectors = [
        "div[data-testid='tweetButton']", 
        "div[role='button'][data-testid='tweetButton']"
    ]
    
    submit_button_clicked = False
    for selector in submit_button_selectors:
        try:
            submit_button = page.query_selector(selector)
            if submit_button:
                # Wait a bit before submitting, like a human would review
                human_like_delay(500, 2000)
                submit_button.click()
                submit_button_clicked = True
                print(f"Submit button clicked with selector: {selector}")
                break
        except Exception as e:
            print(f"Submit button error with selector {selector}: {e}")
    
    # If standard click methods fail, try JavaScript
    if not submit_button_clicked:
        try:
            submit_button_clicked = page.evaluate("""() => {
                const buttons = Array.from(document.querySelectorAll('div[role="button"], button'));
                const tweetButton = buttons.find(button => {
                    const text = button.textContent.toLowerCase();
                    return text.includes('tweet') || text.includes('post') || 
                           button.getAttribute('data-testid') === 'tweetButton';
                });
                if (tweetButton) {
                    tweetButton.click();
                    return true;
                }
                return false;
            }""")
            if submit_button_clicked:
                print("Submit button clicked using JavaScript")
                human_like_delay(2000, 3000)
        except Exception as e:
            print(f"JavaScript submit error: {e}")

    # If submit button still not found, take screenshot and try keyboard shortcut
    if not submit_button_clicked:
        print("Submit button not found, taking screenshot and trying keyboard shortcut...")
        try:
            page.screenshot(path="submit_button_error.png")
            page.keyboard.press("Control+Enter")
            submit_button_clicked = True
            print("Tweet submitted with keyboard shortcut")
            human_like_delay(2000, 3000)
        except Exception as e:
            print(f"Keyboard shortcut error: {e}")
            return False

    # Verify tweet was posted
    try:
        success_check = page.wait_for_selector('[data-testid="toast"]', timeout=5000)
        if success_check:
            print("Tweet posted successfully!")
            return True
    except Exception as e:
        print(f"Could not verify tweet posting: {e}")
        return False

def post_tweet_thread_v2(page, tweets_content):
    """Post a series of tweets as a thread"""
    if not tweets_content:
        print("No content provided for thread")
        return False
    
    # If only one tweet, post as a single tweet
    if len(tweets_content) == 1:
        return post_tweet(page, tweets_content[0])
    
    try:
        # Initial tweet handling
        first_tweet = tweets_content[0]
        print(f"Posting first tweet: {first_tweet[:50]}...")
        
        # Navigate to Twitter compose
        page.goto("https://twitter.com/compose/tweet", timeout=30000)
        human_like_delay(5000, 7000)  # Daha uzun bekleme
        
        # Enter first tweet text - multiple ways to find text area
        text_area_found = False
        
        # Daha fazla seçici ile deneme
        textarea_selectors = [
            "div[data-testid='tweetTextarea_0']",
            "div[role='textbox'][contenteditable='true']",
            "div[aria-label='Post text']",
            "div[aria-label='Tweet text']",
            "div[aria-label='Gönderi metni']",  # Türkçe arayüz için
            "div.public-DraftEditor-content",
            "div.DraftEditor-root div[contenteditable='true']"
        ]
        
        for selector in textarea_selectors:
            try:
                # Daha güvenilir bir seçici kullanım yöntemi
                page.wait_for_selector(selector, state='visible', timeout=10000)
                text_area = page.query_selector(selector)
                if text_area:
                    # Önce tıkla
                    text_area.click()
                    human_like_delay(1000, 2000)
                    
                    # Temizle ve içeriği gir
                    text_area.fill("")
                    human_like_delay(500, 1000)
                    
                    # İçeriği gir
                    text_area.fill(first_tweet)
                    text_area_found = True
                    print(f"First tweet content entered with selector: {selector}")
                    break
            except Exception as e:
                print(f"Textarea error with selector {selector}: {e}")
        
        # JavaScript ile deneme
        if not text_area_found:
            try:
                text_area_found = page.evaluate("""() => {
                    // Tüm potansiyel text area'ları ara
                    const textboxes = document.querySelectorAll('div[role="textbox"], div[contenteditable="true"]');
                    console.log('Found potential textareas:', textboxes.length);
                    
                    if (textboxes.length > 0) {
                        for (const textbox of textboxes) {
                            try {
                                textbox.focus();
                                textbox.click();
                                // İçeriği temizle
                                textbox.innerHTML = '';
                                return true;
                            } catch (e) {
                                console.error('Error focusing textbox:', e);
                            }
                        }
                    }
                    return false;
                }""")
                
                if text_area_found:
                    print("Found and focused textarea using JavaScript")
                    # Şimdi içeriği gir
                    page.keyboard.type(first_tweet)
                    human_like_delay(1000, 2000)
                    print("First tweet content entered using JavaScript keyboard input")
                else:
                    print("No textarea found even with JavaScript")
            except Exception as js_error:
                print(f"JavaScript error: {js_error}")
        
        if not text_area_found:
            print("Could not find text area for first tweet")
            return False
        
        # Add explicit character count check for each tweet before posting
        for i, tweet_text in enumerate(tweets_content):
            if len(tweet_text) > 280:
                print(f"Warning: Tweet {i+1} exceeds 280 characters ({len(tweet_text)} chars)")
                # Truncate to preserve thread flow
                tweets_content[i] = tweet_text[:277] + "..."
                print(f"Tweet {i+1} truncated to: {tweets_content[i][:50]}...")
        
        # For tweets after the first one, first add the "EKLE" button
        if len(tweets_content) > 1:
            # Use MULTIPLE different approaches to ensure we find and click the Add button
            # Approach 1: Standard selectors with more options
            add_button_selectors = [
                "div[aria-label='Add to thread']",
                "div[aria-label='Thread\'e ekle']",
                "div[aria-label='Gönderi ekle']",
                "div[data-testid='addButton']",
                "a[data-testid='addButton']",
                "div[data-testid='addTweetButton']",
                "button[data-testid='addButton']",
                "button[aria-label='Add to thread']",
                "button[aria-label='Thread\'e ekle']",
                "button[aria-label='Gönderi ekle']"
            ]
            
            add_button_clicked = False
            for selector in add_button_selectors:
                try:
                    # Wait for button to be visible with explicit wait
                    page.wait_for_selector(selector, state="visible", timeout=3000)
                    button = page.query_selector(selector)
                    if button:
                        print(f"Found Add button with selector: {selector}")
                        human_like_delay(500, 1000)
                        button.click()
                        add_button_clicked = True
                        print(f"Add button clicked with selector: {selector}")
                        # Wait for UI to update
                        human_like_delay(1000, 2000)
                        break
                except Exception as e:
                    print(f"Add button error with selector {selector}: {e}")
            
            # Approach 2: Try JavaScript to find and click the button
            if not add_button_clicked:
                try:
                    print("Trying JavaScript method to find Add button...")
                    add_button_clicked = page.evaluate("""() => {
                        // Try to find by role and label
                        const buttons = document.querySelectorAll('[role="button"]');
                        for (const button of buttons) {
                            // Look for Add to Thread text or aria-label
                            if (button.textContent && (
                                button.textContent.includes('Add') || 
                                button.textContent.includes('Ekle') ||
                                button.ariaLabel && (
                                    button.ariaLabel.includes('Add') ||
                                    button.ariaLabel.includes('Ekle')
                                )
                            )) {
                                console.log('Found button by text content or aria-label', button);
                                button.click();
                                return true;
                            }
                            
                            // Look for + icon
                            const svg = button.querySelector('svg');
                            if (svg) {
                                const path = svg.querySelector('path');
                                if (path && path.getAttribute('d') && (
                                    path.getAttribute('d').includes('M11 11V7h2v4h4v2h-4v4h-2v-4H7v-2h4z') ||
                                    path.getAttribute('d').includes('M19 11h-6V5h-2v6H5v2h6v6h2v-6h6z')
                                )) {
                                    console.log('Found button by + icon', button);
                                    button.click();
                                    return true;
                                }
                            }
                        }
                        
                        // Try to find any element with testid=addButton
                        const addButton = document.querySelector('[data-testid="addButton"]');
                        if (addButton) {
                            console.log('Found button by data-testid', addButton);
                            addButton.click();
                            return true;
                        }
                        
                        return false;
                    }""")
                    
                    if add_button_clicked:
                        print("Add button clicked with JavaScript method")
                        human_like_delay(1000, 2000)
                    else:
                        print("Could not find Add button with JavaScript")
                except Exception as e:
                    print(f"JavaScript error: {e}")
            
            # Approach 3: Try to find the button by XPath
            if not add_button_clicked:
                try:
                    print("Trying XPath to find Add button...")
                    
                    # XPath expressions to find the button
                    xpaths = [
                        "//div[@role='button']//span[text()='Add']/..",
                        "//div[@role='button']//span[text()='Ekle']/..",
                        "//button[contains(@aria-label, 'Add')]",
                        "//button[contains(@aria-label, 'Ekle')]",
                        "//button[contains(@aria-label, 'Thread')]",
                        "//button[contains(@aria-label, 'Gönderi')]",
                        "//*[@data-testid='addButton']",
                        "//div[contains(@class, 'addButton')]"
                    ]
                    
                    for xpath in xpaths:
                        try:
                            element = page.query_selector(f"xpath={xpath}")
                            if element:
                                print(f"Found Add button with XPath: {xpath}")
                                element.click()
                                add_button_clicked = True
                                print(f"Add button clicked with XPath: {xpath}")
                                human_like_delay(1000, 2000)
                                break
                        except Exception as xe:
                            print(f"XPath error with {xpath}: {xe}")
                except Exception as e:
                    print(f"XPath method error: {e}")
            
            # Approach 4: Take screenshot to debug if previous methods failed
            if not add_button_clicked:
                try:
                    print("Taking screenshot to debug Add button issue...")
                    page.screenshot(path="add_button_missing.png")
                    print("Screenshot saved as add_button_missing.png")
                except Exception as e:
                    print(f"Screenshot error: {e}")
                
                # Still try to continue by using keyboard shortcut
                try:
                    print("Trying keyboard shortcut to add to thread...")
                    page.keyboard.press("Alt+n")  # Some versions of Twitter use Alt+n as shortcut
                    human_like_delay(1000, 2000)
                    
                    # Check if a new textarea appeared
                    new_textareas = page.query_selector_all("div[data-testid='tweetTextarea_0']")
                    if len(new_textareas) > 1:
                        print("New textarea appeared after keyboard shortcut")
                        add_button_clicked = True
                except Exception as e:
                    print(f"Keyboard shortcut error: {e}")
            
            # If we couldn't add to thread, try posting as individual tweets instead
            if not add_button_clicked:
                print("WARNING: Could not add to thread, falling back to posting as individual tweets")
                # Cancel this attempt
                try:
                    page.keyboard.press("Escape")
                    human_like_delay(1000, 2000)
                except:
                    pass
                
                # Use alternative method
                return post_as_numbered_tweets(page, tweets_content)
        
        # Now add content for all additional tweets
        for i in range(1, len(tweets_content)):
            print(f"Posting tweet #{i+1}...")
            tweet_text = tweets_content[i]
            
            # After clicking add button, find the new textarea
            text_area_found = False
            textareas = page.query_selector_all("div[data-testid='tweetTextarea_0']")
            print(f"Found {len(textareas)} textareas")
            
            if len(textareas) > i:
                try:
                    textarea = textareas[i]  # Use the appropriate textarea by index
                    textarea.click()
                    human_like_delay(500, 1000)
                    textarea.fill(tweet_text)
                    text_area_found = True
                    print(f"Tweet {i+1} content entered into textarea #{i+1}")
                except Exception as e:
                    print(f"Error entering text in textarea #{i+1}: {e}")
            
            # Try alternative selectors
            if not text_area_found:
                try:
                    # Try to find the most recently added textarea
                    selector = "div[role='textbox'][contenteditable='true']"
                    textareas = page.query_selector_all(selector)
                    
                    if len(textareas) > i:
                        textarea = textareas[i]
                        textarea.click()
                        human_like_delay(500, 1000)
                        textarea.fill(tweet_text)
                        text_area_found = True
                        print(f"Tweet {i+1} content entered using alternative selector")
                except Exception as e:
                    print(f"Alternative textarea error: {e}")
            
            # Try JavaScript as last resort
            if not text_area_found:
                try:
                    text_area_found = page.evaluate("""(tweetText, index) => {
                        // Find all textareas
                        const textareas = document.querySelectorAll('div[role="textbox"][contenteditable="true"]');
                        console.log('Found', textareas.length, 'textareas via JS');
                        
                        if (textareas.length > index) {
                            const textarea = textareas[index];
                            textarea.focus();
                            textarea.innerHTML = tweetText;
                            return true;
                        }
                        return false;
                    }""", tweet_text, i)
                    
                    if text_area_found:
                        print(f"Tweet {i+1} content entered using JavaScript")
                    else:
                        print(f"Could not find text area for tweet {i+1} even with JavaScript")
                except Exception as e:
                    print(f"JavaScript textarea error: {e}")
            
            # If we still can't find a textarea for this tweet, need to add another
            if not text_area_found and i < len(tweets_content) - 1:
                print(f"Need to add another tweet for content {i+1}")
                add_button_clicked = False
                
                for selector in add_button_selectors:
                    try:
                        button = page.query_selector(selector)
                        if button:
                            button.click()
                            add_button_clicked = True
                            print(f"Additional Add button clicked with selector: {selector}")
                            # Wait for UI to update
                            human_like_delay(2000, 3000)
                            break
                    except Exception as e:
                        print(f"Additional Add button error with selector {selector}: {e}")
                
                if not add_button_clicked:
                    print(f"Could not add tweet #{i+2} to thread, aborting")
                    break
        
        # Submit the thread
        human_like_delay(3000, 5000)
        print("Sending thread...")
        
        # Try to click the submit button
        submit_button_selectors = [
            "div[data-testid='tweetButton']",
            "div[role='button'][data-testid='tweetButton']",
            "div[role='button']:has-text('Tweet')",
            "div[role='button']:has-text('Post')",
            "button[data-testid='tweetButton']",
            "button[data-testid='tweetButton']"
        ]
        
        submit_button_clicked = False
        for selector in submit_button_selectors:
            try:
                submit_button = page.query_selector(selector)
                if submit_button:
                    submit_button.click()
                    submit_button_clicked = True
                    print(f"Submit button clicked with selector: {selector}")
                    break
            except Exception as e:
                print(f"Submit button error with selector {selector}: {e}")
        
        # Try JavaScript if standard selectors fail
        if not submit_button_clicked:
            try:
                submit_button_clicked = page.evaluate("""() => {
                    // Try standard tweet button
                    let tweetButton = document.querySelector("[data-testid='tweetButton']");
                    if (tweetButton) {
                        tweetButton.click();
                        return true;
                    }
                    
                    // Try any button that looks like a submit button
                    const buttons = document.querySelectorAll("[role='button']");
                    for (const button of buttons) {
                        if (button.textContent && (
                            button.textContent.includes("Tweet") || 
                            button.textContent.includes("Post"))) {
                            button.click();
                            return true;
                        }
                    }
                    
                    return false;
                }""")
                
                if submit_button_clicked:
                    print("Submit button clicked with JavaScript method")
            except Exception as e:
                print(f"JavaScript submit error: {e}")
        
        if not submit_button_clicked:
            print("Submit button not found, trying keyboard shortcut...")
            try:
                page.keyboard.press("Control+Enter")
                submit_button_clicked = True
                print("Thread submitted with keyboard shortcut")
            except Exception as e:
                print(f"Keyboard shortcut error: {e}")
                return False
        
        # Wait for confirmation
        human_like_delay(3000, 5000)
        return True
    except Exception as e:
        print(f"Error posting thread: {e}")
        traceback.print_exc()
        return False

def post_as_numbered_tweets(page, tweets_content):
    """Post a series of tweets without numbering them"""
    print("Posting as sequential tweets...")
    
    success = True
    for i, tweet in enumerate(tweets_content):
        # Remove any potential numbering from the tweets
        cleaned_tweet = re.sub(r'\(\d+\/\d+\)', '', tweet)
        cleaned_tweet = re.sub(r'\d+\/\d+', '', cleaned_tweet)
        # Remove notes about character limits
        cleaned_tweet = re.sub(r'This is a single tweet.*?characters\.', '', cleaned_tweet, flags=re.IGNORECASE)
        cleaned_tweet = re.sub(r'No need for a thread\.', '', cleaned_tweet, flags=re.IGNORECASE)
        cleaned_tweet = cleaned_tweet.strip()
        
        # Post tweet content as is, without adding numbering
        post_success = post_tweet(page, cleaned_tweet)
        if not post_success:
            success = False
        human_like_delay(5000, 8000)
    
    return success

def reply_to_tweet(page, tweet_url, reply_text):
    """Reply to a specific tweet using human-like typing"""
    print(f"Navigating to tweet URL: {tweet_url}")
    page.goto(tweet_url)
    human_like_delay(3000, 5000)
    
    # Look for reply button using more robust methods
    print("Looking for reply button...")
    
    # First try standard selectors
    reply_button_selectors = [
        "div[data-testid='reply']", 
        "div[aria-label='Reply']",
        "div[role='button'][data-testid='reply']",
        "button[data-testid='reply']",
        "button[aria-label*='Reply']",
        "button[aria-label*='Yanıt']"
    ]
    
    reply_button_clicked = False
    for selector in reply_button_selectors:
        try:
            reply_button = page.query_selector(selector)
            if reply_button:
                reply_button.click()
                reply_button_clicked = True
                print(f"Reply button clicked with selector: {selector}")
                break
        except Exception as e:
            print(f"Reply button not found with selector {selector}: {e}")
    
    # If standard selectors fail, try advanced JavaScript
    if not reply_button_clicked:
        print("Trying advanced JavaScript selectors for reply button...")
        try:
            # Use JavaScript to find the reply button by its characteristics
            reply_button_clicked = page.evaluate("""() => {
                // Try to find by standard attributes first
                let replyButton = document.querySelector("[data-testid='reply']");
                if (replyButton) {
                    replyButton.click();
                    return true;
                }
                
                // Try to find by SVG path (the reply icon)
                const buttons = document.querySelectorAll("button");
                for (const button of buttons) {
                    // Look for SVG with reply icon path pattern
                    const svg = button.querySelector("svg");
                    if (svg) {
                        const path = svg.querySelector("path");
                        if (path && path.getAttribute("d") && path.getAttribute("d").includes("M1.751 10")) {
                            button.click();
                            return true;
                        }
                    }
                    
                    // Check if button text includes "Reply" or "Yanıt"
                    if (button.textContent && (button.textContent.includes("Reply") || button.textContent.includes("Yanıt"))) {
                        button.click();
                        return true;
                    }
                }
                
                // Try all elements with role="button" that might be the reply button
                const roleButtons = document.querySelectorAll("[role='button']");
                for (const btn of roleButtons) {
                    const svg = btn.querySelector("svg");
                    if (svg) {
                        const path = svg.querySelector("path");
                        if (path && path.getAttribute("d") && path.getAttribute("d").includes("M1.751 10")) {
                            btn.click();
                            return true;
                        }
                    }
                }
                
                return false;
            }""")
            
            if reply_button_clicked:
                print("Reply button clicked with JavaScript method")
            else:
                print("Reply button not found with JavaScript method")
        except Exception as e:
            print(f"JavaScript reply button error: {e}")
    
    if not reply_button_clicked:
        print("Reply button not found, taking screenshot for debugging")
        try:
            page.screenshot(path="reply_button_missing.png")
        except Exception as e:
            print(f"Screenshot error: {e}")
        return False
    
    # Wait for reply textbox
    human_like_delay(2000, 3000)
    
    # Type reply
    textarea_selectors = [
        "div[data-testid='tweetTextarea_0']",
        "div[role='textbox'][contenteditable='true']",
        "div[aria-label='Post text']",
        "div[aria-label='Tweet text']"
    ]
    
    text_area_found = False
    for selector in textarea_selectors:
        try:
            text_area = page.query_selector(selector)
            if text_area:
                # Clear first
                text_area.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Delete")
                
                # Then type
                page.keyboard.type(reply_text)
                text_area_found = True
                print(f"Reply text entered using selector: {selector}")
                break
        except Exception as e:
            print(f"Reply text area error with selector {selector}: {e}")
    
    # If standard selectors fail, try JavaScript
    if not text_area_found:
        try:
            text_area_found = page.evaluate("""(replyText) => {
                // Find any editable div that accepts text
                const textareas = document.querySelectorAll('div[role="textbox"][contenteditable="true"]');
                if (textareas.length > 0) {
                    const textarea = textareas[0];
                    textarea.focus();
                    textarea.innerHTML = replyText;
                    return true;
                }
                return false;
            }""", reply_text)
            
            if text_area_found:
                print("Reply text entered using JavaScript method")
        except Exception as e:
            print(f"JavaScript text area error: {e}")
    
    if not text_area_found:
        print("Could not find reply text area")
        return False
    
    # Send reply - try multiple methods
    reply_submit_selectors = [
        "div[data-testid='tweetButton']",
        "div[role='button'][data-testid='tweetButton']",
        "div[role='button']:has-text('Reply')",
        "div[role='button']:has-text('Yanıtla')"
    ]
    
    reply_submitted = False
    for selector in reply_submit_selectors:
        try:
            submit_button = page.query_selector(selector)
            if submit_button:
                submit_button.click()
                reply_submitted = True
                print(f"Reply submitted with selector: {selector}")
                break
        except Exception as e:
            print(f"Reply submit error with selector {selector}: {e}")
    
    # Try JavaScript if standard selectors fail
    if not reply_submitted:
        try:
            reply_submitted = page.evaluate("""() => {
                // Try standard tweet/reply button
                let replyButton = document.querySelector("[data-testid='tweetButton']");
                if (replyButton) {
                    replyButton.click();
                    return true;
                }
                
                // Try any button that looks like a submit button
                const buttons = document.querySelectorAll("[role='button']");
                for (const button of buttons) {
                    if (button.textContent && (
                        button.textContent.includes("Reply") || 
                        button.textContent.includes("Yanıtla") ||
                        button.textContent.includes("Tweet") ||
                        button.textContent.includes("Post"))) {
                        button.click();
                        return true;
                    }
                }
                
                return false;
            }""")
            
            if reply_submitted:
                print("Reply submitted with JavaScript method")
        except Exception as e:
            print(f"JavaScript submit error: {e}")
    
    if not reply_submitted:
        print("Reply submit button not found, trying keyboard shortcut...")
        try:
            page.keyboard.press("Control+Enter")
            reply_submitted = True
            print("Reply submitted with keyboard shortcut")
        except Exception as e:
            print(f"Reply keyboard shortcut error: {e}")
            return False
    
    # Wait for confirmation
    human_like_delay(3000, 5000)
    return reply_submitted

def browse_tweets_v2(page, account, limit=5):
    """Browse a user's tweets and return their content"""
    print(f"Checking tweets from {account} account...")
    
    # Go to user's profile
    page.goto(f"https://twitter.com/{account}")
    
    # Wait for tweets to load
    human_like_delay(3000, 5000)
    
    # Extract tweet data using JavaScript
    tweets = page.evaluate("""() => {
        const tweets = [];
        const articles = document.querySelectorAll('article[data-testid="tweet"]');
        console.log(`Found ${articles.length} tweet elements`);
        
        let count = 0;
        for (const article of articles) {
            if (count >= 10) break;  // Limit to prevent excessive processing
            
            try {
                // Extract tweet text
                const textElement = article.querySelector('div[data-testid="tweetText"]');
                if (!textElement) continue;
                
                const tweetText = textElement.textContent;
                console.log(`Tweet found: ${tweetText.substring(0, 50)}...`);
                
                // Extract tweet URL
                const timeElement = article.querySelector('time');
                let tweetUrl = null;
                let timestamp = null;
                
                if (timeElement) {
                    const linkElement = timeElement.closest('a');
                    if (linkElement) {
                        tweetUrl = linkElement.href;
                        // Also grab the datetime attribute for timestamp
                        if (timeElement.hasAttribute('datetime')) {
                            timestamp = timeElement.getAttribute('datetime');
                        }
                    }
                }
                
                tweets.push({
                    text: tweetText,
                    url: tweetUrl,
                    timestamp: timestamp
                });
                
                count++;
            } catch (e) {
                console.log(`Error extracting tweet: ${e}`);
            }
        }
        
        console.log(`Found ${tweets.length} tweets`);
        return tweets;
    }""")
    
    print(f"Found {len(tweets)} tweets")
    return tweets

def post_manual_thread(page, tweets_content):
    """Post a thread manually by replying to your own tweets"""
    print("Posting thread using manual reply method...")
    
    if not tweets_content or len(tweets_content) == 0:
        print("Tweet content is empty!")
        return False
        
    # Post first tweet
    first_tweet_posted = post_tweet(page, tweets_content[0])
    if not first_tweet_posted:
        print("Failed to post first tweet")
        return False
        
    print("First tweet posted, waiting to get its URL...")
    human_like_delay(5000, 8000)
    
    try:
        # Go to profile to find the tweet we just posted
        username = os.getenv("TWITTER_USER", "chefcryptoz")
        page.goto(f"https://twitter.com/{username}")
        human_like_delay(3000, 5000)
        
        # Get the first (most recent) tweet
        first_tweet_url = None
        try:
            articles = page.query_selector_all("article")
            if len(articles) > 0:
                # Get URL of first article (most recent tweet)
                first_tweet_url = page.evaluate("""(article) => {
                    const timeElement = article.querySelector('time');
                    if (!timeElement) return null;
                    
                    const linkElement = timeElement.closest('a');
                    if (!linkElement) return null;
                    
                    return linkElement.href;
                }""", articles[0])
                
                print(f"Found first tweet URL: {first_tweet_url}")
            else:
                print("No tweets found on profile")
                return False
        except Exception as e:
            print(f"Error finding first tweet: {e}")
            return False
        
        # Now reply to the first tweet with the thread content
        human_like_delay(3000, 5000)
        print("Replying to first tweet with thread content...")
        
        # For each subsequent tweet, reply to the previous one
        for i in range(1, len(tweets_content)):
            print(f"Replying with tweet #{i+1}...")
            
            # Construct the reply URL (navigating to the previous tweet's URL)
            reply_url = first_tweet_url
            for j in range(i):
                reply_url = reply_url.replace("/status/", "/reply/")
            
            print(f"Navigating to reply URL: {reply_url}")
            page.goto(reply_url)
            human_like_delay(3000, 5000)
            
            # Look for reply button using more robust methods
            print("Looking for reply button...")
            
            # First try standard selectors
            reply_button_selectors = [
                "div[data-testid='reply']", 
                "div[aria-label='Reply']",
                "div[role='button'][data-testid='reply']",
                "button[data-testid='reply']",
                "button[aria-label*='Reply']",
                "button[aria-label*='Yanıt']"
            ]
            
            reply_button_clicked = False
            for selector in reply_button_selectors:
                try:
                    reply_button = page.query_selector(selector)
                    if reply_button:
                        reply_button.click()
                        reply_button_clicked = True
                        print(f"Reply button clicked with selector: {selector}")
                        break
                except Exception as e:
                    print(f"Reply button not found with selector {selector}: {e}")
            
            # If standard selectors fail, try advanced JavaScript
            if not reply_button_clicked:
                print("Trying advanced JavaScript selectors for reply button...")
                try:
                    # Use JavaScript to find the reply button by its characteristics
                    reply_button_clicked = page.evaluate("""() => {
                        // Try to find by standard attributes first
                        let replyButton = document.querySelector("[data-testid='reply']");
                        if (replyButton) {
                            replyButton.click();
                            return true;
                        }
                        
                        // Try to find by SVG path (the reply icon)
                        const buttons = document.querySelectorAll("button");
                        for (const button of buttons) {
                            // Look for SVG with reply icon path pattern
                            const svg = button.querySelector("svg");
                            if (svg) {
                                const path = svg.querySelector("path");
                                if (path && path.getAttribute("d") && path.getAttribute("d").includes("M1.751 10")) {
                                    button.click();
                                    return true;
                                }
                            }
                            
                            // Check if button text includes "Reply" or "Yanıt"
                            if (button.textContent && (button.textContent.includes("Reply") || button.textContent.includes("Yanıt"))) {
                                button.click();
                                return true;
                            }
                        }
                        
                        // Try all elements with role="button" that might be the reply button
                        const roleButtons = document.querySelectorAll("[role='button']");
                        for (const btn of roleButtons) {
                            const svg = btn.querySelector("svg");
                            if (svg) {
                                const path = svg.querySelector("path");
                                if (path && path.getAttribute("d") && path.getAttribute("d").includes("M1.751 10")) {
                                    btn.click();
                                    return true;
                                }
                            }
                        }
                        
                        return false;
                    }""")
                    
                    if reply_button_clicked:
                        print("Reply button clicked with JavaScript method")
                    else:
                        print("Reply button not found with JavaScript method")
                except Exception as e:
                    print(f"JavaScript reply button error: {e}")
            
            # If reply button is clicked, type the reply text
            if reply_button_clicked:
                # Wait for reply textbox
                human_like_delay(2000, 3000)
                
                # Type reply
                textarea_selectors = [
                    "div[data-testid='tweetTextarea_0']",
                    "div[role='textbox'][contenteditable='true']",
                    "div[aria-label='Post text']",
                    "div[aria-label='Tweet text']"
                ]
                
                text_area_found = False
                for selector in textarea_selectors:
                    try:
                        text_area = page.query_selector(selector)
                        if text_area:
                            # Clear first
                            text_area.click()
                            page.keyboard.press("Control+A")
                            page.keyboard.press("Delete")
                            
                            # Then type
                            page.keyboard.type(tweets_content[i])
                            text_area_found = True
                            print(f"Reply text entered using selector: {selector}")
                            break
                    except Exception as e:
                        print(f"Reply text area error with selector {selector}: {e}")
                
                # If standard selectors fail, try JavaScript
                if not text_area_found:
                    try:
                        text_area_found = page.evaluate("""(replyText) => {
                            // Find any editable div that accepts text
                            const textareas = document.querySelectorAll('div[role="textbox"][contenteditable="true"]');
                            if (textareas.length > 0) {
                                const textarea = textareas[0];
                                textarea.focus();
                                textarea.innerHTML = replyText;
                                return true;
                            }
                            return false;
                        }""", tweets_content[i])
                        
                        if text_area_found:
                            print(f"Tweet {i+1} content entered using JavaScript")
                        else:
                            print(f"Could not find text area for tweet {i+1}")
                    except Exception as e:
                        print(f"JavaScript textarea error: {e}")
                
                # Send reply - try multiple methods
                reply_submit_selectors = [
                    "div[data-testid='tweetButton']",
                    "div[role='button'][data-testid='tweetButton']",
                    "div[role='button']:has-text('Reply')",
                    "div[role='button']:has-text('Yanıtla')"
                ]
                
                reply_submitted = False
                for selector in reply_submit_selectors:
                    try:
                        submit_button = page.query_selector(selector)
                        if submit_button:
                            submit_button.click()
                            reply_submitted = True
                            print(f"Reply submitted with selector: {selector}")
                            break
                    except Exception as e:
                        print(f"Reply submit error with selector {selector}: {e}")
                
                # Try JavaScript if standard selectors fail
                if not reply_submitted:
                    try:
                        reply_submitted = page.evaluate("""() => {
                            // Try standard tweet/reply button
                            let replyButton = document.querySelector("[data-testid='tweetButton']");
                            if (replyButton) {
                                replyButton.click();
                                return true;
                            }
                            
                            // Try any button that looks like a submit button
                            const buttons = document.querySelectorAll("[role='button']");
                            for (const button of buttons) {
                                if (button.textContent && (
                                    button.textContent.includes("Reply") || 
                                    button.textContent.includes("Yanıtla") ||
                                    button.textContent.includes("Tweet") ||
                                    button.textContent.includes("Post"))) {
                                    button.click();
                                    return true;
                                }
                            }
                            
                            return false;
                        }""")
                        
                        if reply_submitted:
                            print("Reply submitted with JavaScript method")
                    except Exception as e:
                        print(f"JavaScript submit error: {e}")
                
                if not reply_submitted:
                    print("Reply submit button not found, trying keyboard shortcut...")
                    try:
                        page.keyboard.press("Control+Enter")
                        reply_submitted = True
                        print("Reply submitted with keyboard shortcut")
                    except Exception as e:
                        print(f"Reply keyboard shortcut error: {e}")
                        return False
            
            # Wait for confirmation
            human_like_delay(3000, 5000)
        
        print("Thread posted successfully")
        return True
    except Exception as e:
        print(f"Error posting thread: {e}")
        return False

def cleanup_browser(browser):
    """
    Cleanup browser instance
    """
    try:
        if browser:
            browser.close()
    except Exception as e:
        logger.error(f"Browser cleanup error: {e}")

# Main method for direct execution
def initialize_browser():
    """Initialize or return existing browser instance"""
    global browser, page
    
    if browser is not None and page is not None:
        print("Browser already running")
        return browser, page
    
    browser, page = login()
    return browser, page