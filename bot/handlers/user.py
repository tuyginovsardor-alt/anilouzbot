from aiogram import Router, types
from aiogram.filters import CommandStart
from bot.database import db

router = Router()

@router.message(CommandStart())
async def start_cmd(message: types.Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.full_name)
    
    welcome_text = (
        f"👋 Salom, <b>{user.full_name}</b>!\n\n"
        "<b>Anilo Uz</b> botiga xush kelibsiz. Bu yerda siz eng sara anime "
        "va kinolarni topishingiz hamda tomosha qilishingiz mumkin.\n\n"
        "⚡ Bot tezkor va xavfsiz ishlaydi."
    )
    await message.answer(welcome_text, parse_mode="HTML")
