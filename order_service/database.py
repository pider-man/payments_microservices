from config import settings
from shared.utils.base_database import BaseDatabase


class Database(BaseDatabase):
    def __init__(self):
        super().__init__(settings.mongodb_url, settings.database_name)

db = Database()