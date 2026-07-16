import asyncpg
from bot.config import config

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(config.DATABASE_URL)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def add_user(self, user_id: int, username: str, full_name: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (user_id, username, full_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE 
                SET username = $2, full_name = $3
                """,
                user_id, username, full_name
            )

    async def get_stats(self):
        async with self.pool.acquire() as conn:
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            return {"user_count": user_count}

    async def get_all_users(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id FROM users")
            return [row['user_id'] for row in rows]

db = Database()
