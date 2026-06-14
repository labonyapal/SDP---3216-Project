import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    db_name: str = os.getenv("DATABASE_NAME", "university_db")

db = Database()

def get_db():
    return db.client[db.db_name]