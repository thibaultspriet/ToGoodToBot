import os

config = {
  "server_id" : int(os.getenv("SERVER_ID")),
  "channels" : {
    int(os.getenv("CHANNEL_LILLE_PAPILLON")):{
      "type" : "STORE",
      "data" :[
        {
            "store_id" : 331982,
            "origin" : {
              "lon" : 3.051717,
              "lat" : 50.634859
            },
            "items":0
          },
          {
            "store_id" : 256142,
            "origin" : {
              "lon" : 3.051717,
              "lat" : 50.634859
            },
            "items":0
          },
          {
            "store_id" : 35738,
            "origin" : {
              "lon" : 3.051717,
              "lat" : 50.634859
            },
            "items":0
          }
      ]
    }
  }
}