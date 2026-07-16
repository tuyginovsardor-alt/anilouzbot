import firebase_admin
from firebase_admin import credentials, firestore
from bot.config import config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self.connect()
        return self._db

    def connect(self):
        try:
            if not firebase_admin._apps:
                firebase_admin.initialize_app()
            self._db = firestore.client()
            logger.info("Firebase Admin initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            raise e

    def disconnect(self):
        pass

    async def add_user(self, user_id: int, username: str, full_name: str):
        user_ref = self.db.collection('users').document(str(user_id))
        user_ref.set({
            'user_id': user_id,
            'username': username,
            'full_name': full_name,
            'last_active': firestore.SERVER_TIMESTAMP
        }, merge=True)

    async def get_stats(self):
        docs = self.db.collection('users').stream()
        count = sum(1 for _ in docs)
        return {"user_count": count}

    async def get_all_users(self):
        docs = self.db.collection('users').stream()
        return [int(doc.id) for doc in docs]

db = Database()
