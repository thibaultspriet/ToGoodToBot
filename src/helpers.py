from discord import Embed
from ToGoodApp import ToGoodApp
import re
from settings import MAIL_READER, TOGOOD_CLIENT
from datetime import datetime

def get_store_details(details:str):
    info = {
      "store_name" : re.search(ToGoodApp.RE_STORE_NAME,details).group(1),
      "store_logo" : re.search(ToGoodApp.RE_STORE_LOGO_URL,details).group(1),
      "store_location" : re.search(ToGoodApp.RE_STORE_ADDRESS,details).group(1),
      "store_url" : re.search(ToGoodApp.RE_STORE_URL,details).group(1),
      "nb_items" : int(re.search(ToGoodApp.RE_NB_ITEMS,details).group(1))
    }
    return info

def info_to_string(json_item):
  basket = "paniers disponibles" if json_item["nb_items"] > 1 else "panier disponible"
  string = f'{json_item["nb_items"]} {basket} chez {json_item["store_name"]}\nà retirer ici : {json_item["store_location"]}'
  return string

def info_to_embed(json_item):
  basket = "paniers disponibles" if json_item["nb_items"] > 1 else "panier disponible"
  embed=Embed(title=f"Panier {json_item['store_name']}", url=json_item["store_url"], description=f"{json_item['nb_items']} {basket}", color=0x4f7a28)
  embed.set_author(name="ToGoodToBot", icon_url="https://www.seo.fr/wp-content/uploads/2019/04/robots-txt-1024x945.png")
  embed.set_thumbnail(url=json_item["store_logo"])
  embed.add_field(name="Adresse", value=json_item["store_location"], inline=False)
  return embed

def login():
  now = datetime.now()
  TOGOOD_CLIENT._authByEmail()
  email = MAIL_READER.get_login_email(now,120,2)
  pin = MAIL_READER.get_pin(email)
  TOGOOD_CLIENT._authByRequestPin(pin)

