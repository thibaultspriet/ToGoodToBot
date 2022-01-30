import discord
from ToGoodApp import ToGoodApp
import os
from seleniumrequests import Chrome
from selenium.webdriver.chrome.options import Options
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from mail import Reader
import requests



def init():
    ## logging module
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s]:%(levelname)s:from %(pathname)s in %(funcName)s function : %(message)s', datefmt='%d/%m/%Y %H:%M:%S'
    )

    ## GLOBAL VARIABLES
    global DISCORD_CLIENT, TOGOOD_CLIENT, PROD, DRIVER, SCHEDULER, CHANNEL_BOT, MAIL_READER
    PROD = os.getenv("PROD")
    if PROD is None : PROD = False
    else: PROD = (PROD == "True")
    logging.info(f"production state : {PROD}")
    DISCORD_CLIENT = discord.Client()

    if not PROD:
        global DOTENV_FILE
        import dotenv
        logging.info("load dot env")
        DOTENV_FILE = dotenv.find_dotenv()
        dotenv.load_dotenv(DOTENV_FILE)
    else:
        url = "https://api.heroku.com/apps/togood-backend/config-vars"
        data = {"API_CALL_TEST":"True"}
        headers = {"Content-Type": "application/json","Accept": "application/vnd.heroku+json; version=3","Authorization":f"Bearer {os.getenv('HEROKU_API_TOKEN')}"}
        res = requests.patch(url,json=data,headers=headers)
        logging.info(res.status_code)
        logging.info(res.text)

    

    TOGOOD_CLIENT = ToGoodApp(os.getenv("BOT_APP_EMAIL"))

    MAIL_READER = Reader(os.getenv("BOT_APP_EMAIL"),os.getenv("BOT_APP_PASSWORD"))
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    if PROD:
        chrome_options.binary_location = os.getenv("GOOGLE_CHROME_BIN")
        DRIVER = Chrome(executable_path=os.getenv("CHROMEDRIVER_PATH"),options=chrome_options)
    else:
        DRIVER = Chrome(os.getenv("CHROMEDRIVER"),options=chrome_options)
    
    SCHEDULER = AsyncIOScheduler(job_defaults = {"misfire_grace_time":None})

    CHANNEL_BOT = {}
    
