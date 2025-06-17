const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const fs = require('fs');

// Read tweet content from file
async function postTweet(tweetContent) {
    console.log('Starting tweet posting process...');
    const browser = await puppeteer.launch({
        headless: "new",
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--window-size=1280,720',
        ]
    });

    try {
        console.log('Browser launched');
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 720 });

        // Set user agent
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36');

        // Go to Twitter login
        console.log('Going to Twitter login page...');
        await page.goto('https://twitter.com/i/flow/login', { waitUntil: 'networkidle0' });

        // Take screenshot
        await page.screenshot({ path: 'js_login_page.png' });

        // Login
        console.log('Logging in...');
        await page.waitForSelector('input[autocomplete="username"]', { visible: true, timeout: 15000 });
        await page.type('input[autocomplete="username"]', process.env.TWITTER_USER || 'chefcryptoz', { delay: 150 });

        // Click Next
        const nextButton = await page.$('div[role="button"]:has-text("Next")');
        if (nextButton) {
            await nextButton.click();
        } else {
            await page.keyboard.press('Enter');
        }

        // Wait for password field
        await page.waitForTimeout(3000);

        // Check if verification needed
        const verificationField = await page.$('input[data-testid="ocfEnterTextTextInput"]');
        if (verificationField) {
            console.log('Verification required');
            await verificationField.type(process.env.TWITTER_EMAIL || 'hasanacikgoz91@gmail.com', { delay: 150 });

            // Click Next
            const verifyNextButton = await page.$('div[role="button"]:has-text("Next")');
            if (verifyNextButton) {
                await verifyNextButton.click();
            } else {
                await page.keyboard.press('Enter');
            }

            await page.waitForTimeout(3000);
        }

        // Enter password
        await page.waitForSelector('input[name="password"]', { visible: true, timeout: 15000 });
        await page.type('input[name="password"]', process.env.TWITTER_PASS || 'Nuray1965+', { delay: 150 });

        // Click login
        const loginButton = await page.$('div[role="button"]:has-text("Log in")');
        if (loginButton) {
            await loginButton.click();
        } else {
            await page.keyboard.press('Enter');
        }

        // Wait for login to complete
        await page.waitForTimeout(8000);
        await page.screenshot({ path: 'js_after_login.png' });

        // Go to compose tweet
        console.log('Going to tweet compose page...');
        await page.goto('https://twitter.com/compose/tweet', { waitUntil: 'networkidle0' });
        await page.waitForTimeout(5000);
        await page.screenshot({ path: 'js_compose_page.png' });

        // Find and fill tweet input
        console.log('Entering tweet content...');
        const tweetInput = await page.$('div[role="textbox"][contenteditable="true"], div[data-testid="tweetTextarea_0"]');
        if (tweetInput) {
            await tweetInput.click();
            await page.waitForTimeout(1000);
            await tweetInput.type(tweetContent, { delay: 50 });
            await page.waitForTimeout(2000);

            // Click tweet button
            console.log('Looking for tweet button...');
            const tweetButton = await page.$('div[data-testid="tweetButtonInline"]');
            if (tweetButton) {
                await tweetButton.click();
                console.log('Tweet sent!');
            } else {
                console.log('Tweet button not found');
                await page.screenshot({ path: 'js_tweet_button_missing.png' });
            }

            await page.waitForTimeout(5000);
        } else {
            console.log('Tweet input area not found');
            await page.screenshot({ path: 'js_tweet_input_missing.png' });
        }
    } catch (error) {
        console.error('Error:', error);
        await page.screenshot({ path: 'js_error.png' });
    } finally {
        await browser.close();
        console.log('Browser closed');
    }
}

// Read tweet content from arguments or file
const tweetContent = process.argv[2] || 'Test tweet from puppeteer-extra with stealth mode!';
postTweet(tweetContent);