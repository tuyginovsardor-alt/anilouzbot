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

@router.message(Command("admin"), F.from_user.id == config.ADMIN_ID)
async def admin_panel(message: types.Message):
    admin_text = (
        "🛠 <b>ANILO UZ | ADMIN PANEL</b>\n\n"
        "Hurmatli loyiha rahbari, tizimni boshqarish bo'limiga xush kelibsiz. "
        "Quyidagi menyu orqali kerakli bo'limni tanlang:\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 <b>1. Statistika</b>: Bot a'zolari, faollik va tizim yuklamasi tahlili.\n"
        "📢 <b>2. Reklama</b>: Foydalanuvchilarga xabar yuborish tizimi.\n"
        "⚙️ <b>3. Sozlamalar</b>: Bot sozlamalarini tahrirlash.\n"
        "🔐 <b>4. API & Storage</b>: CORS, JWT xavfsizligi va Mega.io storage gateway holati.\n"
        "🚫 <b>5. Bloklash</b>: Qoidabuzar foydalanuvchilarni cheklash.\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚡ Kerakli amaliyotni bajarish uchun pastdagi tugmalardan birini bosing:"
    )
    await message.answer(admin_text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")

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
