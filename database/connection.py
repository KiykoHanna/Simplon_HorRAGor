# src/database/connection.py

from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

engine = create_engine(DATABASE_URL)

def get_engine():
    return engine