"""
Configuration management for Order Service.
"""
import os


class Settings:
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.database_name = os.getenv("DATABASE_NAME", "order_service_db")
        self.user_service_url = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
        self.service_port = 8001


settings = Settings()
