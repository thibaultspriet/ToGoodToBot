from email import header
import logging
from discord import Embed
from ToGoodApp import ToGoodApp
import re
from settings import MAIL_READER, TOGOOD_CLIENT, PROD, DISCORD_CLIENT
from datetime import datetime
import os
import requests

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

def _login_with_email():
  print("login with email")
  now = datetime.now()
  try:
    MAIL_READER.authenticate()
    TOGOOD_CLIENT._authByEmail()
    email = MAIL_READER.get_login_email(now,120,2)
    pin = MAIL_READER.get_pin(email)
    TOGOOD_CLIENT._authByRequestPin(pin)
  except Exception as e:
    logging.error(f"error while trying to login with email\n{e}")
    alert_admin(f"error while trying to login with email\n{e}")
  if PROD:
    url = "https://api.heroku.com/apps/togood-backend/config-vars"
    data = {"AUTH_TOKEN":TOGOOD_CLIENT.access_token,"USER_ID":TOGOOD_CLIENT.user_id}
    headers = {"Content-Type": "application/json","Accept": "application/vnd.heroku+json; version=3","Authorization":f"Bearer {os.getenv('HEROKU_API_TOKEN')}"}
    res = requests.patch(url,json=data,headers=headers)
    if res.status_code == 200:
      logging.info("Successfully updated config vars for login")
    else:
      logging.error(f"Failed to update config vars for login\nerror message : {res.text}")
  else:
    from settings import DOTENV_FILE
    import dotenv
    os.environ["AUTH_TOKEN"] = TOGOOD_CLIENT.access_token
    os.environ["USER_ID"] = TOGOOD_CLIENT.user_id
    # Write changes to .env file.
    dotenv.set_key(DOTENV_FILE, "AUTH_TOKEN", os.environ["AUTH_TOKEN"])
    dotenv.set_key(DOTENV_FILE, "USER_ID", os.environ["USER_ID"])


def login():
  if os.getenv("AUTH_TOKEN") and os.getenv("USER_ID"):
    TOGOOD_CLIENT.access_token = os.getenv("AUTH_TOKEN")
    TOGOOD_CLIENT.user_id = os.getenv("USER_ID")
    try:
      TOGOOD_CLIENT.get_user()
      logging.info("tokens valid")
    except:
      _login_with_email()
  else:
    _login_with_email()


async def alert_admin(message:str,channel_id=os.getenv("ADMIN_CHANNEL")):
  print("alert admin")
  channel = DISCORD_CLIENT.get_channel(int(channel_id))
  print(channel_id,channel)
  await channel.send(message)

