from pytz import timezone
from settings import init
init()

from webserver import keep_alive
from ChannelBot import ChannelBot
from config import config


from settings import *

from helpers import login
login()

@DISCORD_CLIENT.event
async def on_ready():
    print(f'We have logged in as {DISCORD_CLIENT.user}')
    for channel_id in config["channels"].keys():
        bot = ChannelBot(channel_id)
        CHANNEL_BOT[channel_id]=bot
        SCHEDULER.add_job(bot.send_item_store,"cron",second="0",hour="6-21",timezone=timezone('Europe/Paris'))
    SCHEDULER.start()
    

@DISCORD_CLIENT.event
async def on_message(message):
    if message.author == DISCORD_CLIENT.user:
        return

    if message.content.upper() == "PING" :
        await message.channel.send("pong")
    
    if message.content.upper() == "FETCH" :
        channel_id = message.channel.id
        await CHANNEL_BOT[channel_id].send_item_store()

if PROD : keep_alive()
DISCORD_CLIENT.run(os.getenv('BOT_TOKEN'))