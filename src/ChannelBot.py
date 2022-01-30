from helpers import get_store_details, info_to_embed, login
import discord


from config import config

class ChannelBot:


  def __init__(self,channel_id:int):
    from settings import DISCORD_CLIENT

    self.channel_id = channel_id
    self.config = config["channels"][self.channel_id].copy()
    self.channel = DISCORD_CLIENT.get_channel(channel_id)
    
  # async def send_item_area(self,togood_client,channel):
  #   items = togood_client.items_area(self.items_data_request)
  #   for item in items:
  #     item_id = item["item"]["item_id"]
  #     if item_id not in togood_client.get_notified_items():
  #       togood_client.add_notified_item(item_id)
  #       await channel.send(embed = info_to_embed(get_item_info(item)))
  
  async def send_item_store(self):
    from settings import TOGOOD_CLIENT

    

    data = self.config["data"]
    for store in data:
      item_string = TOGOOD_CLIENT.fetch_store_id(store["store_id"],store["origin"]["lat"],store["origin"]["lon"])
      item_dict = get_store_details(item_string)
      nb_items = item_dict["nb_items"]
      if nb_items == store["items"]:
        print("no change in baskets")
        return
      else:
        store["items"] = nb_items
        if nb_items > 0:
          embed = info_to_embed(item_dict)
        else:
          embed = discord.Embed(title=f"Panier {item_dict['store_name']}", description="Tu as raté ta chance ... il n'y a plus de paniers disponibles", color=0xe32400)
        await self.channel.send(embed = embed)
