import firebase_admin
from firebase_admin import credentials, firestore
from bot.config import config
import logging
import os
import json

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            try:
                self.connect()
            except:
                pass
        return self._db

    def connect(self):
        try:
            if not firebase_admin._apps:
                # Try to load from environment variable (for Vercel)
                sa_info = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
                if sa_info:
                    try:
                        cert_dict = json.loads(sa_info)
                        cred = credentials.Certificate(cert_dict)
                        firebase_admin.initialize_app(cred)
                        logger.info("Firebase initialized using FIREBASE_SERVICE_ACCOUNT.")
                    except Exception as je:
                        logger.error(f"Failed to parse FIREBASE_SERVICE_ACCOUNT JSON: {je}")
                        firebase_admin.initialize_app()
                else:
                    # Fallback to default credentials (for local or GCP)
                    firebase_admin.initialize_app()
                    logger.info("Firebase initialized using Default Credentials.")
            
            # Use custom database ID if provided
            db_id = os.environ.get('FIREBASE_DATABASE_ID')
            if db_id:
                self._db = firestore.client(database=db_id)
                logger.info(f"Firestore client connected to database: {db_id}")
            else:
                self._db = firestore.client()
                logger.info("Firestore client connected to (default) database.")
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            self._db = None

    def disconnect(self):
        pass

    async def add_user(self, user_id: int, username: str, full_name: str):
        if not self.db:
            return
        
        try:
            user_ref = self.db.collection('users').document(str(user_id))
            user_ref.set({
                'telegram_id': user_id,
                'username': username,
                'full_name': full_name,
                'joined_at': firestore.SERVER_TIMESTAMP,
                'is_blocked': False,
                'last_active': firestore.SERVER_TIMESTAMP
            }, merge=True)
        except Exception as e:
            logger.error(f"Firestore error in add_user: {e}")

    async def get_stats(self):
        if not self.db:
            return {"user_count": 0, "error": "DB not connected"}
        
        try:
            docs = self.db.collection('users').stream()
            count = sum(1 for _ in docs)
            return {"user_count": count}
        except Exception as e:
            logger.error(f"Firestore error in get_stats: {e}")
            return {"user_count": 0, "error": str(e)}

    async def add_movie(self, data: dict):
        if not self.db:
            logger.error("Cannot add movie: Firestore not initialized.")
            return False
        
        try:
            # Use title_uz as document ID (slugified or unique string) or auto ID
            # For consistency, let's use auto ID but store the data
            doc_ref = self.db.collection('movies').document()
            data['created_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(data)
            logger.info(f"Movie added to database: {data.get('title_uz')}")
            return True
        except Exception as e:
            logger.error(f"Firestore error in add_movie: {e}")
            return False

    async def get_latest_movies(self, limit: int = 10):
        if not self.db:
            return []
        
        try:
            docs = self.db.collection('movies').order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.error(f"Firestore error in get_latest_movies: {e}")
            return []

    async def get_all_users(self):
        if not self.db:
            return []
        
        try:
            docs = self.db.collection('users').stream()
            return [int(doc.id) for doc in docs]
        except Exception as e:
            logger.error(f"Firestore error in get_all_users: {e}")
            return []

db = Database()
