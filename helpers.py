from discord import Embed

def get_item_info(item):
    info = {
      "store_name" : item["display_name"],
      "store_logo" : item["item"]["logo_picture"]["current_url"],
      "store_location" : item["store"]["store_location"]["address"]["address_line"],
      "store_url" : item["store"]["website"],
      "nb_items" : item["items_available"]
    }
    return info

def info_to_string(json_item):
  basket = "paniers disponibles" if json_item["nb_items"] > 1 else "panier disponible"
  string = f'{json_item["nb_items"]} {basket} chez {json_item["store_name"]}\nà retirer ici : {json_item["store_location"]}'
  return string

def info_to_embed(json_item):
  print(json_item)
  basket = "paniers disponibles" if json_item["nb_items"] > 1 else "panier disponible"
  embed=Embed(title=f"Panier {json_item['store_name']}", url=json_item["store_url"], description=f"{json_item['nb_items']} {basket}", color=0x4f7a28)
  embed.set_author(name="ToGoodToBot", icon_url="https://www.seo.fr/wp-content/uploads/2019/04/robots-txt-1024x945.png")
  embed.set_thumbnail(url=json_item["store_logo"])
  embed.add_field(name="Adresse", value=json_item["store_location"], inline=False)
  return embed
