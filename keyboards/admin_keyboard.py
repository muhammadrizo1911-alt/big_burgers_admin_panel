from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_main_menu():
    """Admin uchun asosiy menu"""
    kb = [
        [
            KeyboardButton(text="📋 Buyurtmalar"),
            KeyboardButton(text="🍔 Maxsulotlar")
        ],
        [
            KeyboardButton(text="⚙️ Sozlamalar")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=kb, 
        resize_keyboard=True,
        input_field_placeholder="Bo'limni tanlang..."
    )