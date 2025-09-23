# config.py
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env into environment

DATABASE_URI = os.getenv("DATABASE_URI", "")
VALKEY_HOST = os.getenv("VALKEY_HOST", "localhost")
VALKEY_PORT = os.getenv("VALKEY_PORT", "6379")