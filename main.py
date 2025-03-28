import discord
import tweepy
import asyncio
if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Discord bot token
DISCORD_TOKEN = 'MTM1NDk2NTEyMTkzNTM0Nzg4NA.G4SboC.J_Ze0RRy3sHe1f-bEemobj70_vMg4d4KxOdCbo'
CHANNEL_ID = 1354962858030665963  # e.g., 123456789012345678

# Twitter API credentials
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAABUvwQEAAAAAzxuuj%2F1Ez0ZHC69Rx0CpPGVGlW8%3DjbWxj4mOFoDTacrmnMWXFAXUZeUWu4hh9YjnGPiWBiH7aNv3xD'

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
