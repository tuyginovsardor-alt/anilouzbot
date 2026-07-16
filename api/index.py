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

# Ensure database is connected (lazy connection handled in Database class)
# But we can trigger it here once
try:
    db.connect()
except:
    pass

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    logger.info("Starting up Anilo Uz Bot...")
    try:
        # Initialize Firebase
        db.connect()
    except Exception as e:
        logger.error(f"Firebase initialization error: {e}")
    
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
    webhook_info = await bot.get_webhook_info()
    db_status = "Connected"
    db_details = {}
    try:
        # Check connection and get some info
        if db.db:
            db_details = {
                "project_id": db.db._project,
                "database_id": db.db._database_string.split('/')[-1] if hasattr(db.db, '_database_string') else "(default)"
            }
    except Exception as e:
        db_status = f"Error: {str(e)}"
        
    return {
        "status": "Anilo Uz Bot is running",
        "admin": config.ADMIN_ID,
        "database_status": db_status,
        "database_details": db_details,
        "webhook_set": bool(webhook_info.url),
        "webhook_url": webhook_info.url
    }

@app.get("/setup-webhook")
async def setup_webhook():
    if not config.APP_URL or not config.BOT_TOKEN:
        return {"ok": False, "error": "APP_URL or BOT_TOKEN not set in environment variables"}
    
    webhook_url = f"{config.APP_URL}/webhook"
    await bot.set_webhook(
        url=webhook_url,
        secret_token=config.WEBHOOK_SECRET,
        drop_pending_updates=True
    )
    return {"ok": True, "message": f"Webhook set to {webhook_url}"}

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
