from aiogram import Router, types, F
from aiogram.filters import CommandStart
from bot.database import db
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

def get_user_main_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔍 Anime qidirish", callback_data="search_anime"))
    builder.row(types.InlineKeyboardButton(text="🎬 So'nggi yuklanganlar", callback_data="latest_anime"))
    builder.row(
        types.InlineKeyboardButton(text="ℹ️ Biz haqimizda", callback_data="about_us"),
        types.InlineKeyboardButton(text="⭐ Yordam", callback_data="help")
    )
    return builder.as_markup()

@router.message(CommandStart())
async def start_cmd(message: types.Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.full_name)
    
    welcome_text = (
        f"👋 Salom, <b>{user.full_name}</b>!\n\n"
        "✨ <b>Anilo Uz</b> — O'zbekistondagi eng yirik anime portali botiga xush kelibsiz!\n\n"
        "Bu yerda siz:\n"
        "• Eng so'nggi animelarni o'zbek tilida ko'rishingiz\n"
        "• Janrlar bo'yicha qidirishingiz\n"
        "• Sifatli va tezkor yuklab olishingiz mumkin.\n\n"
        "⚡ Kerakli bo'limni tanlang:"
    )
    await message.answer(welcome_text, reply_markup=get_user_main_kb(), parse_mode="HTML")

@router.callback_query(F.data == "about_us")
async def about_us(callback: types.CallbackQuery):
    text = (
        "📖 <b>Anilo Uz haqida</b>\n\n"
        "Biz anime ixlosmandlari uchun sifatli kontent yetkazib beruvchi jamoamiz. "
        "Barcha animelar HD sifatda va o'zbek tilidagi dublyaj yoki subtitrlar bilan taqdim etiladi."
    )
    await callback.message.edit_text(text, reply_markup=get_user_main_kb(), parse_mode="HTML")
