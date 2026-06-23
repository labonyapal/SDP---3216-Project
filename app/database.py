import os
import threading
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class Database:
    _instance = None
    _lock = threading.Lock()  # Ensures thread safety

    def __new__(cls):
        # Double-checked locking pattern
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Database, cls).__new__(cls)
                    # Initialize instance variables only once
                    cls._instance.client = None
                    cls._instance.db_name = os.getenv("DATABASE_NAME", "university_db")
        return cls._instance

    def connect(self):
        # Initialize the connection only if it hasn't been done yet
        if self.client is None:
            self.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))

    def get_database(self):
        if self.client is None:
            raise Exception("Database not connected. Call connect() first.")
        return self.client[self.db_name]

# Create the singleton instance
db = Database()

# Dependency function for FastAPI
def get_db():
    return db.get_database()