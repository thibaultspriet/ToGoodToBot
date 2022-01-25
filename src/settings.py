import discord
from ToGoodApp import ToGoodApp
import os
from seleniumrequests import Chrome
from selenium.webdriver.chrome.options import Options
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from mail import Reader




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
        from dotenv import load_dotenv
        logging.info("load dot env")
        load_dotenv()

    

    TOGOOD_CLIENT = ToGoodApp(os.getenv("BOT_APP_EMAIL"))

    MAIL_READER = Reader(os.getenv("BOT_APP_EMAIL"),os.getenv("BOT_APP_PASSWORD"))
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    _chromedriver_path = os.getenv("CHROMEDRIVER") if not PROD else ""
    DRIVER = Chrome(_chromedriver_path,options=chrome_options)
    
    SCHEDULER = AsyncIOScheduler(job_defaults = {"misfire_grace_time":None})

    CHANNEL_BOT = {}
    
