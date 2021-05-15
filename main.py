import discord
import os
from webserver import keep_alive
from ToGoodApp import ToGoodApp
from ChannelBot import ChannelBot
from config import config


discord_client = discord.Client()

togood_client = ToGoodApp(os.getenv("BOT_APP_EMAIL"),os.getenv("BOT_APP_PASSWORD"))
togood_client.login()


@discord_client.event
async def on_ready():
    print(f'We have logged in as {discord_client.user}')
    guild = discord_client.get_guild(config["server_id"])

    channel_bots = []
    for channel in config["channels"]:
      channel_bots += ChannelBot.channel_factory(togood_client,guild,channel)
    ChannelBot.start_bots(channel_bots)


@discord_client.event
async def on_message(message):
    print("Hi received the message")
    if message.author == discord_client.user:
        return

    if message.content.upper() == "PING" :
        await message.channel.send("pong")

keep_alive()
discord_client.run(os.getenv('BOT_TOKEN'))