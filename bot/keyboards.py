from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="📢 Reklama", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="admin_settings"),
            InlineKeyboardButton(text="🔌 API & Storage", callback_data="admin_storage")
        ],
        [
            InlineKeyboardButton(text="🚫 Bloklash", callback_data="admin_block"),
            InlineKeyboardButton(text="❌ Panelni yopish", callback_data="admin_close")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_button(target="admin_main"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data=target)]
    ])
