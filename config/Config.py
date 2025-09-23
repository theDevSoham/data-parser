# config.py
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env into environment

DATABASE_URI = os.getenv("DATABASE_URI", "")