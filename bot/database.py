from supabase import create_client, Client
from bot.config import config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self._client: Client = None

    @property
    def client(self) -> Client:
        if self._client is None:
            self.connect()
        return self._client

    def connect(self):
        try:
            if config.SUPABASE_URL and config.SUPABASE_KEY:
                self._client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
                logger.info("Supabase client initialized successfully.")
            else:
                logger.warning("Supabase credentials missing in config.")
        except Exception as e:
            logger.error(f"Error initializing Supabase: {e}")
            self._client = None

    def disconnect(self):
        pass

    async def add_user(self, user_id: int, username: str, full_name: str):
        if not self.client:
            return
        
        try:
            # Check if user exists to avoid overwriting joined_at if we were to send it
            # But upsert with on_conflict is cleaner. 
            # We only send fields that should be updated or set on first time.
            data = {
                'telegram_id': user_id,
                'username': username,
                'full_name': full_name,
                'is_blocked': False
            }
            # Supabase upsert will handle the rest. 
            # If 'joined_at' has a default in DB, it will be set on insert.
            self.client.table('users').upsert(data, on_conflict='telegram_id').execute()
        except Exception as e:
            logger.error(f"Supabase error in add_user: {e}")

    async def get_stats(self):
        if not self.client:
            return {"user_count": 0, "error": "DB not connected"}
        
        try:
            # count() in supabase-py returns a response object
            response = self.client.table('users').select("telegram_id", count="exact").execute()
            count = len(response.data) if response.data else 0
            # If we want exact count from header: response.count
            return {"user_count": response.count if hasattr(response, 'count') else count}
        except Exception as e:
            logger.error(f"Supabase error in get_stats: {e}")
            return {"user_count": 0, "error": str(e)}

    async def add_movie(self, data: dict):
        if not self.client:
            logger.error("Cannot add movie: Supabase not initialized.")
            return False
        
        try:
            self.client.table('movies').insert(data).execute()
            logger.info(f"Movie added to Supabase: {data.get('title_uz')}")
            return True
        except Exception as e:
            logger.error(f"Supabase error in add_movie: {e}")
            return False

    async def get_latest_movies(self, limit: int = 10):
        if not self.client:
            return []
        
        try:
            response = self.client.table('movies')\
                .select("*")\
                .order('id', desc=True)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Supabase error in get_latest_movies: {e}")
            return []

    async def get_all_users(self):
        if not self.client:
            return []
        
        try:
            response = self.client.table('users').select("telegram_id").execute()
            return [int(row['telegram_id']) for row in response.data] if response.data else []
        except Exception as e:
            logger.error(f"Supabase error in get_all_users: {e}")
            return []

db = Database()
