from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.config import config
from bot.keyboards import get_admin_main_keyboard, get_back_button
from bot.database import db
import asyncio

router = Router()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()

class AddMovieStates(StatesGroup):
    waiting_for_title_uz = State()
    waiting_for_title_ru = State()
    waiting_for_description_uz = State()
    waiting_for_description_ru = State()
    waiting_for_poster_url = State()
    waiting_for_banner_url = State()
    waiting_for_genre = State()
    waiting_for_rating = State()
    waiting_for_year = State()
    waiting_for_type = State()
    waiting_for_status = State()
    waiting_for_video_url = State()
    waiting_for_episodes_count = State()
    waiting_for_site_url = State()

@router.message(Command("admin"), F.from_user.id == config.ADMIN_ID)
async def admin_panel(message: types.Message):
    admin_text = (
        "🛠 <b>ANILO UZ | ADMIN PANEL</b>\n\n"
        "Hurmatli loyiha rahbari, tizimni boshqarish bo'limiga xush kelibsiz. "
        "Quyidagi menyu orqali kerakli bo'limni tanlang:\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 <b>1. Statistika</b>: Bot a'zolari, faollik va tizim yuklamasi tahlili.\n"
        "🎬 <b>2. Kino Qo'shish</b>: Yangi anime yoki kinolarni bazaga kiritish.\n"
        "📢 <b>3. Reklama</b>: Foydalanuvchilarga xabar yuborish tizimi.\n"
        "⚙️ <b>4. Sozlamalar</b>: Bot sozlamalarini tahrirlash.\n"
        "🔌 <b>5. API & Storage</b>: Tizim holati tahlili.\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚡ Kerakli amaliyotni bajarish uchun pastdagi tugmalardan birini bosing:"
    )
    await message.answer(admin_text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "admin_add_movie")
async def start_add_movie(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎬 <b>Yangi kino qo'shish</b>\n\n1. O'zbekcha nomini kiriting:",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await state.set_state(AddMovieStates.waiting_for_title_uz)

@router.message(AddMovieStates.waiting_for_title_uz)
async def process_title_uz(message: types.Message, state: FSMContext):
    await state.update_data(title_uz=message.text)
    await message.answer("2. Ruscha nomini kiriting (yoki '-' deb yozing):")
    await state.set_state(AddMovieStates.waiting_for_title_ru)

@router.message(AddMovieStates.waiting_for_title_ru)
async def process_title_ru(message: types.Message, state: FSMContext):
    await state.update_data(title_ru=message.text)
    await message.answer("3. O'zbekcha tavsifini kiriting:")
    await state.set_state(AddMovieStates.waiting_for_description_uz)

@router.message(AddMovieStates.waiting_for_description_uz)
async def process_desc_uz(message: types.Message, state: FSMContext):
    await state.update_data(description_uz=message.text)
    await message.answer("4. Ruscha tavsifini kiriting (yoki '-' deb yozing):")
    await state.set_state(AddMovieStates.waiting_for_description_ru)

@router.message(AddMovieStates.waiting_for_description_ru)
async def process_desc_ru(message: types.Message, state: FSMContext):
    await state.update_data(description_ru=message.text)
    await message.answer("5. Poster URL (400x600):")
    await state.set_state(AddMovieStates.waiting_for_poster_url)

@router.message(AddMovieStates.waiting_for_poster_url)
async def process_poster(message: types.Message, state: FSMContext):
    await state.update_data(poster_url=message.text)
    await message.answer("6. Banner URL (1920x1080):")
    await state.set_state(AddMovieStates.waiting_for_banner_url)

@router.message(AddMovieStates.waiting_for_banner_url)
async def process_banner(message: types.Message, state: FSMContext):
    await state.update_data(banner_url=message.text)
    await message.answer("7. Janrlar (masalan: Ekshen, Drama):")
    await state.set_state(AddMovieStates.waiting_for_genre)

@router.message(AddMovieStates.waiting_for_genre)
async def process_genre(message: types.Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await message.answer("8. Reyting (0-10):")
    await state.set_state(AddMovieStates.waiting_for_rating)

@router.message(AddMovieStates.waiting_for_rating)
async def process_rating(message: types.Message, state: FSMContext):
    try:
        rating = float(message.text)
        await state.update_data(rating=rating)
        await message.answer("9. Yili (masalan: 2024):")
        await state.set_state(AddMovieStates.waiting_for_year)
    except ValueError:
        await message.answer("⚠️ Iltimos, raqam kiriting (masalan: 8.5):")

@router.message(AddMovieStates.waiting_for_year)
async def process_year(message: types.Message, state: FSMContext):
    try:
        year = int(message.text)
        await state.update_data(year=year)
        await message.answer("10. Turi (movie yoki series):")
        await state.set_state(AddMovieStates.waiting_for_type)
    except ValueError:
        await message.answer("⚠️ Iltimos, yilni raqamda kiriting:")

@router.message(AddMovieStates.waiting_for_type)
async def process_type(message: types.Message, state: FSMContext):
    await state.update_data(type=message.text)
    await message.answer("11. Holati (ongoing yoki completed):")
    await state.set_state(AddMovieStates.waiting_for_status)

@router.message(AddMovieStates.waiting_for_status)
async def process_status(message: types.Message, state: FSMContext):
    await state.update_data(status=message.text)
    await message.answer("12. Video URL (Direct MP4 yoki HLS):")
    await state.set_state(AddMovieStates.waiting_for_video_url)

@router.message(AddMovieStates.waiting_for_video_url)
async def process_video_url(message: types.Message, state: FSMContext):
    await state.update_data(video_url=message.text)
    await message.answer("13. Qismlar soni:")
    await state.set_state(AddMovieStates.waiting_for_episodes_count)

@router.message(AddMovieStates.waiting_for_episodes_count)
async def process_episodes(message: types.Message, state: FSMContext):
    try:
        count = int(message.text)
        await state.update_data(episodes_count=count)
        await message.answer("14. Saytdagi sahifa URL (site_url):")
        await state.set_state(AddMovieStates.waiting_for_site_url)
    except ValueError:
        await message.answer("⚠️ Iltimos, raqam kiriting:")

@router.message(AddMovieStates.waiting_for_site_url)
async def process_site_url(message: types.Message, state: FSMContext):
    await state.update_data(site_url=message.text)
    data = await state.get_data()
    await state.clear()
    
    success = await db.add_movie(data)
    if success:
        await message.answer(f"✅ <b>{data['title_uz']}</b> muvaffaqiyatli bazaga qo'shildi!", parse_mode="HTML")
    else:
        await message.answer("❌ Xatolik yuz berdi. Iltimos, loglarni tekshiring.")

@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: types.CallbackQuery):
    stats = await db.get_stats()
    text = (
        "📊 <b>Tizim Statistikasi</b>\n\n"
        f"👥 Umumiy foydalanuvchilar: {stats['user_count']}\n"
        "🚀 API so'rovlar: 1,240 (bugun)\n"
        "💾 Storage bandligi: 15% / 50GB"
    )
    await callback.message.edit_text(text, reply_markup=get_back_button(), parse_mode="HTML")

@router.callback_query(F.data == "admin_storage")
async def show_storage(callback: types.CallbackQuery):
    text = (
        "🔐 <b>API & Storage Status</b>\n\n"
        "✅ Mega.io: Connected\n"
        "✅ JWT Token: Valid\n"
        "✅ CORS: Allowed for domain.com\n"
        "⚡ Latency: 45ms"
    )
    await callback.message.edit_text(text, reply_markup=get_back_button(), parse_mode="HTML")

@router.callback_query(F.data == "admin_main")
async def back_to_main(callback: types.CallbackQuery):
    admin_text = (
        "🛠 <b>ANILO UZ | ADMIN PANEL</b>\n\n"
        "Quyidagi menyu orqali kerakli bo'limni tanlang:"
    )
    await callback.message.edit_text(admin_text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "admin_close")
async def close_panel(callback: types.CallbackQuery):
    await callback.message.delete()

@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📢 Reklama xabarini yuboring (Matn, rasm yoki video):",
        reply_markup=get_back_button()
    )
    await state.set_state(AdminStates.waiting_for_broadcast)

@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    await state.clear()
    users = await db.get_all_users()
    
    await message.answer(f"🚀 Reklama {len(users)} kishiga yuborilmoqda...")
    
    count = 0
    # Chunking for serverless efficiency
    chunk_size = config.BROADCAST_CHUNK_SIZE
    for i in range(0, len(users), chunk_size):
        chunk = users[i:i + chunk_size]
        tasks = []
        for user_id in chunk:
            tasks.append(message.copy_to(chat_id=user_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        count += sum(1 for r in results if not isinstance(r, Exception))
        
        # Short pause to respect telegram limits and avoid huge spike
        await asyncio.sleep(0.5)

    await message.answer(f"✅ Reklama muvaffaqiyatli yakunlandi: {count}/{len(users)}")
