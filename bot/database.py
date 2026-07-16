import firebase_admin
from firebase_admin import credentials, firestore
from bot.config import config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db = None

    def connect(self):
        try:
            # Initialize firebase if not already initialized
            if not firebase_admin._apps:
                # Use default credentials in AI Studio/Vercel
                firebase_admin.initialize_app()
            
            self.db = firestore.client()
            logger.info("Firebase Admin initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")

    def disconnect(self):
        # firebase-admin doesn't strictly need a disconnect call like a pool
        pass

    async def add_user(self, user_id: int, username: str, full_name: str):
        # Firestore is synchronous in firebase-admin (mostly), 
        # but we keep it async for consistency in the bot logic.
        user_ref = self.db.collection('users').document(str(user_id))
        user_ref.set({
            'user_id': user_id,
            'username': username,
            'full_name': full_name,
            'last_active': firestore.SERVER_TIMESTAMP
        }, merge=True)

    async def get_stats(self):
        users_ref = self.db.collection('users')
        # Note: In production with many users, use a counter or aggregation query
        docs = users_ref.stream()
        count = sum(1 for _ in docs)
        return {"user_count": count}

    async def get_all_users(self):
        users_ref = self.db.collection('users')
        docs = users_ref.stream()
        return [int(doc.id) for doc in docs]

db = Database()
