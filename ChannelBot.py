from apscheduler.schedulers.asyncio import AsyncIOScheduler
from helpers import get_item_info, info_to_embed
from discord import Embed

class ChannelBot:

  
  def __init__(self,channel,tg_client,override_items_request=None,store_id=None,lat=None,lon=None):
    self.scheduler = AsyncIOScheduler(
      job_defaults = {"misfire_grace_time":None}
    )
    self.channel = channel
    self.tg_client = tg_client
    self.items_data_request = override_items_request
    self.store_id = store_id
    self.items_available_in_store = "0"
    self.lat = lat
    self.lon = lon
    self.build_scheduler()
    
  async def send_item_area(self,togood_client,channel):
    items = togood_client.items_area(self.items_data_request)
    for item in items:
      item_id = item["item"]["item_id"]
      if item_id not in togood_client.get_notified_items():
        togood_client.add_notified_item(item_id)
        await channel.send(embed = info_to_embed(get_item_info(item)))
  
  async def send_item_store(self,togood_client,channel):
    item = togood_client.items_available_store(self.store_id,self.lat,self.lon)
    if str(item["items_available"]) == self.items_available_in_store:
      return
    else:
      self.items_available_in_store = str(item["items_available"])
      if int(self.items_available_in_store) > 0:
        embed = info_to_embed(get_item_info(item))

      else:
        item_info = get_item_info(item)
        embed = Embed(title=f"Panier {item_info['store_name']}", description="Tu as raté ta chance ... il n'y a plus de paniers disponibles", color=0xe32400)
      await channel.send(embed = embed)

  async def send_message(self,tg_client,channel):
    if self.items_data_request != None:
      await self.send_item_area(tg_client,channel)
    elif self.store_id != None:
      await self.send_item_store(tg_client,channel)


  @staticmethod
  def channel_area_factory(tg_client,server,config):
    d_channel = server.get_channel(config["id"])
    channel_bot = ChannelBot(d_channel,tg_client,override_items_request=config["data"]["request"])
    return [channel_bot]
  
  @staticmethod
  def channel_store_factory(tg_client,server,config):
    d_channel = server.get_channel(config["id"])
    channel_bot = []
    for data in config["data"]:
      lat = data["origin"]["lat"]
      lon = data["origin"]["lon"]
      bot = ChannelBot(d_channel,tg_client,store_id=data["store_id"],lat=lat,lon=lon)
      channel_bot.append(bot)
    return channel_bot

  @staticmethod
  def channel_factory(tg_client,server,channel_config):
    if channel_config["type"] == "AREA":
      return ChannelBot.channel_area_factory(tg_client,server,channel_config)
    elif channel_config["type"] == "STORE":
      return ChannelBot.channel_store_factory(tg_client,server,channel_config)

  @staticmethod
  def start_bots(bot_list):
    for bot in bot_list:
      bot.start()
    
  def build_scheduler(self):
    self.scheduler.add_job(self.send_message,'interval',minutes=2,args=(self.tg_client,self.channel))
  
  def start(self):
    self.scheduler.start()