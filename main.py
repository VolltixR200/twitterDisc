import discord
import tweepy
import asyncio
import os
if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from dotenv import load_dotenv
load_dotenv()
CHANNEL_ID = os.getenv("CHANNEL_ID")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")


# Twitter settings
TWITTER_USERNAME = 'WatcherGuru'  # Without @

intents = discord.Intents.default()
client = discord.Client(intents=intents)
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

last_tweet_id = None

async def check_tweets():
    global last_tweet_id
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        try:
            tweets = twitter_client.get_users_tweets(
                id=twitter_client.get_user(username=TWITTER_USERNAME).data.id,
                max_results=5
            )

            if tweets.data:
                new_tweets = []
                for tweet in tweets.data:
                    if last_tweet_id is None or tweet.id > last_tweet_id:
                        new_tweets.append(tweet)

                if new_tweets:
                    new_tweets.reverse()
                    for tweet in new_tweets:
                        await channel.send(f"New Tweet from @{TWITTER_USERNAME}:\nhttps://twitter.com/{TWITTER_USERNAME}/status/{tweet.id}")
                        last_tweet_id = tweet.id

        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(60)  # check every minute


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def setup_hook():
    client.loop.create_task(check_tweets())

client.run(DISCORD_TOKEN)
