import logging
from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import config
from bot.handlers import user, admin
from bot.database import db
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Bot and Dispatcher
bot = Bot(token=config.BOT_TOKEN)
# NOTE: In serverless, MemoryStorage resets on every function invocation.
# For production serverless, use RedisStorage or PostgreSQLStorage.
dp = Dispatcher(storage=MemoryStorage())

# Register routers
dp.include_router(user.router)
dp.include_router(admin.router)

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    logger.info("Starting up Anilo Uz Bot...")
    try:
        # Check if DB URL is valid and not a placeholder
        if config.DATABASE_URL and "user:password" not in config.DATABASE_URL:
            await db.connect()
            logger.info("Database connected successfully.")
        else:
            logger.warning("DATABASE_URL is not configured properly. DB features disabled.")
    except Exception as e:
        logger.error(f"Database connection error: {e}")
    
    # Set webhook if configuration is complete
    try:
        if config.APP_URL and config.BOT_TOKEN:
            webhook_url = f"{config.APP_URL}/webhook"
            await bot.set_webhook(
                url=webhook_url,
                secret_token=config.WEBHOOK_SECRET,
                drop_pending_updates=True
            )
            logger.info(f"Webhook set successfully to: {webhook_url}")
        else:
            logger.warning("BOT_TOKEN or APP_URL missing. Webhook not set.")
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down...")
    await db.disconnect()
    await bot.session.close()

@app.get("/")
async def index():
    return {"status": "Anilo Uz Bot is running", "admin": config.ADMIN_ID}

@app.post("/webhook")
async def webhook(request: Request):
    # Verify secret token
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != config.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized")

    update = await request.json()
    telegram_update = types.Update(**update)
    
    # Process update
    await dp.feed_update(bot, telegram_update)
    return {"ok": True}

# For local development (uvicorn api.index:app --port 3000)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
