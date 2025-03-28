import discord
import tweepy
import asyncio
import os
from datetime import datetime
if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from dotenv import load_dotenv
load_dotenv()

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Twitter settings - list of accounts to monitor
TWITTER_ACCOUNTS = [
    "WatcherGuru",
    "Ashcryptoreal",
    "realDonaldTrump"
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

# Dictionary to store last tweet ID for each account
last_tweet_ids = {account: None for account in TWITTER_ACCOUNTS}

def create_tweet_embed(tweet, username, user_data):
    embed = discord.Embed(
        description=tweet.text,
        color=0x1DA1F2,  # Twitter blue color
        url=f"https://twitter.com/{username}/status/{tweet.id}",
        timestamp=datetime.now()
    )

    embed.set_author(
        name=f"@{username}",
        icon_url=user_data.profile_image_url,
        url=f"https://twitter.com/{username}"
    )

    embed.set_footer(text="Twitter", icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")
    return embed

async def check_tweets():
    global last_tweet_ids
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        for username in TWITTER_ACCOUNTS:
            try:
                user = twitter_client.get_user(
                    username=username,
                    user_fields=['profile_image_url']
                ).data

                tweets = twitter_client.get_users_tweets(
                    id=user.id,
                    max_results=5,
                    tweet_fields=['created_at']
                )

                if tweets.data:
                    new_tweets = []
                    for tweet in tweets.data:
                        if last_tweet_ids[username] is None or tweet.id > last_tweet_ids[username]:
                            new_tweets.append(tweet)

                    if new_tweets:
                        new_tweets.reverse()
                        for tweet in new_tweets:
                            embed = create_tweet_embed(tweet, username, user)
                            await channel.send(embed=embed)
                            last_tweet_ids[username] = tweet.id

            except Exception as e:
                print(f"Error checking tweets for {username}: {e}")

        await asyncio.sleep(300)  # check every 5 minutes (5 * 60 seconds)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    print(f'Monitoring tweets from: {", ".join(TWITTER_ACCOUNTS)}')

@client.event
async def setup_hook():
    client.loop.create_task(check_tweets())

client.run(DISCORD_TOKEN)
