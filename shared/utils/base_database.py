"""
Database connection management for Order Service.
"""
from motor.motor_asyncio import AsyncIOMotorClient


class BaseDatabase:
    def __init__(self, mongodb_url: str, database_name: str):
        self.mongodb_url = mongodb_url
        self.database_name = database_name
        self.client: AsyncIOMotorClient = None

    async def connect_db(self):
        """Establish connection to MongoDB"""
        self.client = AsyncIOMotorClient(self.mongodb_url)

    def close_db(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

    async def get_database(self):
        """Get database instance"""
        return self.client[self.database_name]


db = Database()
