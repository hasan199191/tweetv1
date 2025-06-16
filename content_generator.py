import os
import random
from dotenv import load_dotenv
import google.generativeai as genai
import textwrap

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Fallback content to use in case of API errors
FALLBACK_REPLIES = [
    "Excellent point about #Web3! The technology's evolution is truly reshaping digital ownership and finance. What aspects are you most excited about?",
    "I've been following this project closely. The use cases for this technology are compelling, especially in DeFi. Thoughts on adoption timeline?",
    "This is an insightful take on the current state of blockchain technology. Have you considered how this might impact traditional finance systems?",
    "The intersection of #crypto and real-world applications continues to expand. This particular development seems promising for mainstream adoption.",
    "Interesting perspective! The innovation happening in this space is remarkable. I'm curious about scalability challenges moving forward."
]

FALLBACK_CONTENT = [
    "The evolution of {project} (@{handle}) demonstrates how Web3 is maturing. Their approach to solving {problem} through decentralized systems shows promise. Worth watching their development in coming months! #Web3 #Crypto #{hashtag}",
    
    "Thread on @{handle}'s recent progress: 1/3\n\nTheir innovative solution for {problem} is gaining traction among developers. The technical architecture combines scalability with security in a way few projects have achieved.",
    
    "Just explored @{handle}'s website and impressed by their vision. They're addressing real challenges in the {sector} sector with blockchain technology. Their approach to {problem} could be game-changing if adoption continues. #Web3 #{hashtag}",
    
    "@{handle} is one to watch in the evolving Web3 landscape. Their focus on {problem} addresses a critical need, and their technical execution appears solid. Interested to see their ecosystem growth in Q3/Q4. #Blockchain #Innovation #{hashtag}"
]

def generate_web3_reply(tweet_text, keyword=None):
    """Generate a reply to a tweet, optionally focused on a keyword"""
    
    prompt = f"""
    You are an expert Web3 analyst, community engager, and Twitter content creator specializing in blockchain, DeFi, and crypto projects.
    
    Generate a unique, insightful, natural, and human-like reply comment to the following tweet:
    
    TWEET: {tweet_text}
    
    Your reply should be:
    - Written in clear, fluent English.
    - Concise enough to fit as a single tweet reply (280 characters max).
    - Original and not copied or generic.
    - Informative, providing analysis, opinion, or relevant context.
    - Engaging and encouraging further discussion.
    - Professional but approachable in tone.
    - Include 1-2 relevant hashtags.
    
    Provide ONLY the reply text, with no additional explanations.
    """
    
    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()
        
        # Check for Twitter's character limit
        if len(reply) > 280:
            reply = textwrap.shorten(reply, width=277, placeholder="...")
        
        return reply
    except Exception as e:
        print(f"Gemini API reply generation error: {e}")
        # Use fallback content
        reply = random.choice(FALLBACK_REPLIES)
        return reply

def generate_web3_content(project):
    """Generate original content about a Web3 project"""
    
    # Extract project data
    project_name = project.get('name', 'Web3 project')
    twitter_handle = project.get('twitter', '@web3project').replace('@', '')
    website = project.get('website', 'project.com')
    
    # Problem or sector options
    problems = ["scalability", "interoperability", "security", "user onboarding", "data privacy", "transaction costs", "governance"]
    sectors = ["DeFi", "gaming", "NFT", "social media", "identity", "data storage", "infrastructure"]
    
    prompt = f"""
    You are an expert Web3 analyst and Twitter content creator specializing in blockchain, DeFi, and crypto projects.
    
    Generate an original, well-researched, and engaging Twitter post about {project_name} (Twitter: @{twitter_handle}, Website: {website}).
    
    Your content should:
    - Start by mentioning the project's Twitter handle: @{twitter_handle}
    - Educate and inform about recent developments, trends, or insights related to this project
    - Use clear, human-like language that is accessible but professional
    - Include examples, use cases, or recent news where relevant
    - Be formatted to respect Twitter's 280 character limit per tweet
    - Avoid clichés, jargon, and generic content
    - Inspire community engagement and thoughtful discussion
    - Include 1-2 relevant hashtags
    
    If the content is longer than 280 characters, organize it as a numbered thread (e.g., 1/3, 2/3, etc.), with each tweet under 280 characters.
    
    Provide ONLY the tweet content, with clear indications of tweet breaks if it's a thread.
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Ensure correct thread format if needed
        # If not and longer than 280 chars, split it
        if len(content) > 280 and "1/" not in content:
            tweets = split_into_tweets(content)
            content = "\n\n".join(tweets)
        
        return content
    except Exception as e:
        print(f"Gemini API content generation error: {e}")
        
        # Use fallback content
        random_problem = random.choice(problems)
        random_sector = random.choice(sectors)
        
        template = random.choice(FALLBACK_CONTENT)
        content = template.format(
            project=project_name,
            handle=twitter_handle,
            problem=random_problem,
            sector=random_sector,
            hashtag=project_name.replace(" ", "")
        )
        
        return content

def split_into_tweets(text, max_length=280):
    """Split a long text into multiple tweets"""
    if len(text) <= max_length:
        return [text]
    
    # Split text into words and distribute into tweets
    words = text.split()
    tweets = []
    current_tweet = ""
    
    for word in words:
        if len(current_tweet) + len(word) + 1 <= max_length - 6:  # Reserve 6 chars for " (1/n)"
            if current_tweet:
                current_tweet += " " + word
            else:
                current_tweet = word
        else:
            tweets.append(current_tweet)
            current_tweet = word
    
    if current_tweet:
        tweets.append(current_tweet)
    
    # Number the tweets in the thread
    numbered_tweets = []
    for i, tweet in enumerate(tweets):
        numbered_tweets.append(f"{tweet} ({i+1}/{len(tweets)})")
    
    return numbered_tweets