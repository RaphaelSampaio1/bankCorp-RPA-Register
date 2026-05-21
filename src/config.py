import os 
from dotenv import load_dotenv

load_dotenv("data/.env")

class ConfigData:
    SITE_URL = os.getenv("SITE_URL")
    USER = os.getenv("USER")
    PASSWORD = os.getenv("PASSWORD")
