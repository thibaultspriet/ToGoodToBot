from ToGoodApp import ToGoodApp
import os

lille_boulangerie_data = ToGoodApp.get_default_request()
lille_boulangerie_data["origin"] = {
  "longitude": 3.051717,
  "latitude": 50.634859
}
lille_boulangerie_data["item_categories"] = ["BAKED_GOODS"]

cergy_meal_data = ToGoodApp.get_default_request()
cergy_meal_data["origin"] = {
  "longitude": 2.067221,
  "latitude": 49.038868
}
cergy_meal_data["item_categories"] = ["BAKED_GOODS"]


config = {
  "server_id" : int(os.getenv("SERVER_ID")),
  "channels" : [
    {
      "id" : int(os.getenv("CHANNEL_LILLE_BOULANGERIE")),
      "type" : "AREA",
      "data" : {
        "request" : lille_boulangerie_data
      }
    },
    {
      "id" : int(os.getenv("CHANNEL_CERGY_MEAL")),
      "type" : "AREA",
      "data" : {
        "request" : cergy_meal_data
      }
    },
    {
      "id" : int(os.getenv("CHANNEL_LILLE_PAPILLON")) ,
      "type" : "STORE",
      "data" :
        [
          {
            "store_id" : 331982,
            "origin" : {
              "lon" : 3.051717,
              "lat" : 50.634859
            }
          },
          {
            "store_id" : 256142,
            "origin" : {
              "lon" : 3.051717,
              "lat" : 50.634859
            }
          },
          {
            "store_id" : 35738,
            "origin" : {
              "lon" : 3.051717,
              "lat" : 50.634859
            }
          }
        ]
    }
  ]
}