"""
Configuration module — loads environment variables from data/.env.

Uses python-dotenv to read credentials and the site URL so sensitive
values stay out of the source code.
"""

import os
from dotenv import load_dotenv

load_dotenv("data/.env")


class ConfigData:
    """
    Holds configuration constants loaded from environment variables.

    Attributes:
        SITE_URL (str): Banking portal URL.
        USER (str): Login username.
        PASSWORD (str): Login password.
    """
    SITE_URL = os.getenv("SITE_URL")
    USER = os.getenv("USER")
    PASSWORD = os.getenv("PASSWORD")
