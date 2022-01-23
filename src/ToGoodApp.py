import requests
import time
import re
import logging

class ToGoodApp:

  BASE_URL = "https://apptoogoodtogo.com/api/"

  RE_STORE_NAME = "<storeName>(.*?)</storeName>"
  RE_STORE_LOGO_URL = "<logoPicture>.*?<currentUrl>(.*?)</currentUrl>.*?</logoPicture>"
  RE_STORE_ADDRESS = "<addressLine>(.*?)</addressLine>"
  RE_STORE_URL = "<store>.*<website>(.*?)</website>"
  RE_NB_ITEMS = "<itemsAvailable>(.*?)</itemsAvailable>"


  def __init__(self,email,device="IOS"):
    # self.is_logged = False
    # self.notified_items = []
    self.email = email
    self.user_id = ""
    self._polling_id="" #use for authentication with email
    self.access_token = ""
    self.refresh_token = ""
    self.device = device

  # @staticmethod
  # def get_base_header():
  #   return ToGoodApp.BASE_HEADER.copy()

  # @staticmethod
  # def get_default_request():
  #   return ToGoodApp.DEFAULT_ITEMS_REQUEST.copy()

  # def get_auth_header(self):
  #   header = ToGoodApp.get_base_header()
  #   header["Authorization"] = f'Bearer {self.access_token}'
  #   return header

  def _authByEmail(self):
    """Sends request to get email with login code.
    A pollingId is sent back, we use it to set _pollingId attribute
    """

    logging.info("request auth by email ...")
    from settings import DRIVER
    
    url = f"{ToGoodApp.BASE_URL}auth/v3/authByEmail"
    json = {"email":self.email,"device_type":self.device}
    res = DRIVER.request("POST",url,json=json)

    if res.status_code == 200:
      logging.info("success")
      _text = res.text
      match = re.search("<pollingId\>(.*)</pollingId>", _text) # retrieve the pollingId from answer
      if match:
        self._polling_id = match.group(1)
        logging.info("pollingId found")
      else : 
        logging.error(f"no pollingId found in : {_text}")
        raise("No polling id found")
    else: 
      logging.error(f"request to login with email failed\n{res.text}")
      raise("Auth by email failed")

  def _authByRequestPin(self,pin:str):
    """Get refresh and access token.
    If success : set access_token, refresh_token and user_id attributes.
    Otherwise Exception is raised

    Args:
        pin (str): pin that has been sent via email
    """
    logging.info("login with pin ...")
    from settings import DRIVER

    url = f"{ToGoodApp.BASE_URL}auth/v3/authByRequestPin"
    json = {"email":self.email,"device_type":self.device,"request_pin":pin,"request_polling_id":self._polling_id}
    res = DRIVER.request("POST",url,json=json)

    _text = res.text
    if res.status_code == 200:      
      logging.info("success")
      match = re.search("<accessToken>(.*)</accessToken>.*<refreshToken>(.*)</refreshToken>.*<userId><value>(.*)</value></userId>",_text)
      if match:
        self.access_token=match.group(1)
        self.refresh_token=match.group(2)
        self.user_id=match.group(3)
        logging.info("tokens found")
      else : 
        logging.error(f"no tokens found in : {_text}")
        raise("No tokens found")
    else: 
      logging.error(f"request to login with pin failed\n{_text}")
      raise("Authentication failed")


  def fetch_store_id(self,store_id:str,lat:str,lon:str) -> str:
    """Fetch details of a store with its id and geolocation

    Args:
        store_id (str): id of the store to fetch data
        lat (str): latitude of the store
        lon (str): longitude of the store

    Returns:
        str: result string
    """
    from settings import DRIVER
    url = f'{ToGoodApp.BASE_URL}item/v7/{store_id}'
    headers = {"Authorization" : f'Bearer {self.access_token}'}
    json={"user_id":self.user_id,"origin":{"latitude":lat,"longitude":lon}}
    res = DRIVER.request("POST",url,headers=headers,json=json)
    if(res.status_code == 200):
      logging.info(f"successfully fetched store : {store_id}")
      return res.text
    else:
      logging.error(res.text)
      raise(Exception(f"An error occur while fetching store with id : {store_id}"))
  
    



  # def login(self):
  #   if(self.is_logged):
  #     print("You're already logged in ...")
  #     return

  #   url = f'{ToGoodApp.BASE_URL}auth/v2/loginByEmail'
  #   json = {"email" : self.email, "password" : self.password, "device_type" : self.device}
  #   res = requests.post(url, headers=ToGoodApp.get_base_header(), json=json)
  #   if(res.status_code == 200):
  #     res = res.json()
  #     self.access_token = res["access_token"]
  #     self.refresh_token = res["refresh_token"]
  #     self.user_id = res["startup_data"]["user"]["user_id"]
  #     self.is_logged = True
  #     print("Successfully logged in ...")
  #     return
  #   else:
  #     print(f"Login failed\n{res.text}")
  #     return

  # def _refresh_token(self):
  #   url = f'{ToGoodApp.BASE_URL}app/v1/user_settings'
  #   headers = self.get_auth_header()
  #   test_connection = requests.post(url,headers=headers)
  #   if test_connection.status_code == 200:
  #     print("Access token valid")
  #   else:
  #     print("Access token might have expired")
  #     print(test_connection.json())
  #     url = f'{ToGoodApp.BASE_URL}auth/v1/token/refresh'
  #     headers = ToGoodApp.get_base_header()
  #     json = {"refresh_token" : self.refresh_token}
  #     res = requests.post(url,headers=headers,json=json)
  #     if res.status_code == 200 :
  #       print("refreshing token")
  #       self.access_token = res["access_token"]
  #       self.refresh_token = res["refresh_token"]

  # def logout(self):
  #   self._refresh_token()
  #   url = f'{ToGoodApp.BASE_URL}auth/v2/logout'
  #   localtime = time.strftime("%H:%M:%S")
  #   json = {
  #     "localtime" : localtime,
  #     "user_id" : self.user_id
  #   }
  #   headers = self.get_auth_header()
  #   res = requests.post(url, headers=headers, json=json)
  #   if(res.status_code == 200):
  #     print("Successfully logged out ...")
  #     self.is_logged = False
  #   else:
  #     print("An error occured please try again ...")
  #   return

  # def items_area(self,request_data):
  #   self._refresh_token()
  #   url = f'{ToGoodApp.BASE_URL}item/v7/'
  #   headers = self.get_auth_header()
  #   json = request_data
  #   json["user_id"] = self.user_id
  #   res = requests.post(url, headers=headers, json=json)
  #   if(res.status_code == 200):
  #     res = res.json()["items"]
  #     res = list(filter(
  #       lambda item : item["items_available"] > 0,
  #       res
  #     ))
  #     return res
  #   else:
  #     print("An error has occured please try again ...")
  #     return

  

    
  # def add_notified_item(self,id):
  #   self.notified_items.append(id)

  # def get_notified_items(self):
  #   return self.notified_items
