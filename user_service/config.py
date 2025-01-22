"""
Configuration management for User Service.
"""
import os


class Settings:
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.database_name = os.getenv("DATABASE_NAME", "user_service_db")
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "sEcReT")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = 30


settings = Settings()
