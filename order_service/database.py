"""
Database connection management for Order Service.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings


class Database:
    client: AsyncIOMotorClient = None

    async def connect_db(self):
        """Establish connection to MongoDB"""
        self.client = AsyncIOMotorClient(settings.mongodb_url)

    def close_db(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

    async def get_database(self):
        """Get database instance"""
        return self.client[settings.database_name]


db = Database()
