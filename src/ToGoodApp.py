import re
import logging
import pytz

class ToGoodApp:

  BASE_URL = "https://apptoogoodtogo.com/api/"

  RE_STORE_NAME = "<storeName>(.*?)</storeName>"
  RE_STORE_LOGO_URL = "<logoPicture>.*?<currentUrl>(.*?)</currentUrl>.*?</logoPicture>"
  RE_STORE_ADDRESS = "<addressLine>(.*?)</addressLine>"
  RE_STORE_URL = "<store>.*<website>(.*?)</website>"
  RE_NB_ITEMS = "<itemsAvailable>(.*?)</itemsAvailable>"


  def __init__(self,email,device="IOS"):
    self.email = email
    self.user_id = ""
    self._polling_id="" #use for authentication with email
    self.access_token = ""
    self.refresh_token = ""
    self.device = device


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

  def get_user(self):
    from settings import DRIVER
    from datetime import datetime
    url = f'{ToGoodApp.BASE_URL}user/v1/'
    headers = {"Authorization" : f'Bearer {self.access_token}'}
    localtime=datetime.now(pytz.timezone("Europe/Paris")).strftime("%H:%M:%S")
    data = {
      "localtime":localtime,
      "user_id":self.user_id
    }
    res = DRIVER.request("POST",url,headers=headers,data=data)
    if(res.status_code == 200):
      return res.text
    else:
      logging.error(res.text)
      raise(Exception(f"Failed to get user"))

