from aiogram import Router, types, F
from aiogram.filters import CommandStart
from bot.database import db
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

logger = logging.getLogger(__name__)

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
    try:
        await db.add_user(user.id, user.username, user.full_name)
    except Exception as e:
        logger.error(f"Failed to record user in DB: {e}")
    
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

@router.callback_query(F.data == "latest_anime")
async def show_latest(callback: types.CallbackQuery):
    movies = await db.get_latest_movies(5)
    if not movies:
        await callback.answer("Hozircha kinolar mavjud emas.")
        return

    await callback.message.delete()
    
    for movie in movies:
        text = (
            f"🎬 <b>{movie.get('title')}</b>\n"
            f"⭐️ Reyting: {movie.get('rating')}\n"
            f"📅 Yil: {movie.get('year')}\n"
            f"🎭 Janr: {movie.get('genre')}\n\n"
            f"📝 {movie.get('plot', '')[:200]}..."
        )
        
        kb = InlineKeyboardBuilder()
        movie_id = movie.get('id')
        url = f"https://anilo.uz/movie/{movie_id}" if movie_id else "https://anilo.uz"
        kb.row(types.InlineKeyboardButton(text="🌐 Saytda ko'rish", url=url))
        
        if movie.get('poster_url'):
            try:
                await callback.message.answer_photo(
                    photo=movie.get('poster_url'),
                    caption=text,
                    reply_markup=kb.as_markup(),
                    parse_mode="HTML"
                )
            except:
                await callback.message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
        else:
            await callback.message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

    await callback.message.answer("Asosiy menyuga qaytish:", reply_markup=get_user_main_kb())

@router.callback_query(F.data == "about_us")
async def about_us(callback: types.CallbackQuery):
    text = (
        "📖 <b>Anilo Uz haqida</b>\n\n"
        "Biz anime ixlosmandlari uchun sifatli kontent yetkazib beruvchi jamoamiz. "
        "Barcha animelar HD sifatda va o'zbek tilidagi dublyaj yoki subtitrlar bilan taqdim etiladi."
    )
    await callback.message.edit_text(text, reply_markup=get_user_main_kb(), parse_mode="HTML")
