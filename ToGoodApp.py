import requests
import time

class ToGoodApp:

  BASE_URL = "https://apptoogoodtogo.com/api/"
  USER_AGENT = "TooGoodToGo/21.3.0 (935) (iPhone/iPhone 7 (Global); iOS 14.2; Scale/2.00)"
  BASE_HEADER = {
        "Accept" : "*/*",
        "Connection" : "keep-alive",
        "Content-Type" : "application/json",
        "User-Agent" : USER_AGENT,
        "Accept-Encoding" : "gzip;q=1.0, compress;q=0.5"
    }
  DEFAULT_ITEMS_REQUEST = {
    "radius": 5,
        "discover": "false",
        "user_id": None,
        "favorites_only": "false",
        "item_categories": [],
        "origin": {
            "longitude": 0, #float
            "latitude": 0
        },
        "diet_categories": [],
        "hidden_only": "false",
        "page_size": 20,
        "with_stock_only": "true",
        "we_care_only": "false",
        "page": 1,
  }

  def __init__(self,email,password,device="IOS"):
    self.access_token = ""
    self.refresh_token = ""
    self.user_id = ""
    self.is_logged = False
    self.notified_items = []
    self.email = email
    self.password = password
    self.device = device

  @staticmethod
  def get_base_header():
    return ToGoodApp.BASE_HEADER.copy()

  @staticmethod
  def get_default_request():
    return ToGoodApp.DEFAULT_ITEMS_REQUEST.copy()

  def get_auth_header(self):
    header = ToGoodApp.get_base_header()
    header["Authorization"] = f'Bearer {self.access_token}'
    return header

  def login(self):
    if(self.is_logged):
      print("You're already logged in ...")
      return

    url = f'{ToGoodApp.BASE_URL}auth/v2/loginByEmail'
    json = {"email" : self.email, "password" : self.password, "device_type" : self.device}
    res = requests.post(url, headers=ToGoodApp.get_base_header(), json=json)
    if(res.status_code == 200):
      res = res.json()
      self.access_token = res["access_token"]
      self.refresh_token = res["refresh_token"]
      self.user_id = res["startup_data"]["user"]["user_id"]
      self.is_logged = True
      print("Successfully logged in ...")
      return
    else:
      print("An error occur please try again")
      return

  def _refresh_token(self):
    url = f'{ToGoodApp.BASE_URL}app/v1/user_settings'
    headers = self.get_auth_header()
    test_connection = requests.post(url,headers=headers)
    if test_connection.status_code == 200:
      print("Access token valid")
    else:
      print("Access token might have expired")
      print(test_connection.json())
      url = f'{ToGoodApp.BASE_URL}auth/v1/token/refresh'
      headers = ToGoodApp.get_base_header()
      json = {"refresh_token" : self.refresh_token}
      res = requests.post(url,headers=headers,json=json)
      if res.status_code == 200 :
        print("refreshing token")
        self.access_token = res["access_token"]
        self.refresh_token = res["refresh_token"]

  def logout(self):
    self._refresh_token()
    url = f'{ToGoodApp.BASE_URL}auth/v2/logout'
    localtime = time.strftime("%H:%M:%S")
    json = {
      "localtime" : localtime,
      "user_id" : self.user_id
    }
    headers = self.get_auth_header()
    res = requests.post(url, headers=headers, json=json)
    if(res.status_code == 200):
      print("Successfully logged out ...")
      self.is_logged = False
    else:
      print("An error occured please try again ...")
    return

  def items_area(self,request_data):
    self._refresh_token()
    url = f'{ToGoodApp.BASE_URL}item/v7/'
    headers = self.get_auth_header()
    json = request_data
    json["user_id"] = self.user_id
    res = requests.post(url, headers=headers, json=json)
    if(res.status_code == 200):
      res = res.json()["items"]
      res = list(filter(
        lambda item : item["items_available"] > 0,
        res
      ))
      return res
    else:
      print("An error has occured please try again ...")
      return

  def items_available_store(self,store_id,lat,lon):
    self._refresh_token()
    url = f'{ToGoodApp.BASE_URL}item/v7/{store_id}'
    headers = self.get_auth_header()
    json={"user_id":self.user_id,"origin":{"latitude":lat,"longitude":lon}}
    res = requests.post(url,headers=headers,json=json)
    if(res.status_code == 200):
      return res.json()
    else:
      print("An error has occured in ToGoodApp (items_available_store) please try again ...")
      return

    
  def add_notified_item(self,id):
    self.notified_items.append(id)

  def get_notified_items(self):
    return self.notified_items
