import asyncio
import logging
import os
from decimal import Decimal
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

load_dotenv(override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "0").split(",") if x.strip()]

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ================== DATABASE ==================
from database import db

# ================== KEYBOARDS ==================
from keyboards.admin_keyboard import get_admin_main_menu

# ================== HELPERS ==================
def format_price(value):
    if isinstance(value, Decimal):
        value = float(value)
    try:
        return f"{value:,.0f} so'm"
    except Exception:
        return str(value)

# ================== HANDLERS ==================
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer(
            "<b>👨‍💼 BIG BURGERS Admin Paneliga Xush Kelibsiz!</b>\n\n"
            "Kerakli bo'limni tanlang:",
            reply_markup=get_admin_main_menu()
        )
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.message(F.text == "📋 Buyurtmalar")
async def cmd_orders(message: Message):
    orders = await db.get_recent_orders(limit=10)
    if not orders:
        await message.answer("📦 Hozircha buyurtma topilmadi.")
        return

    lines = ["<b>📋 So'nggi buyurtmalar:</b>"]
    for order in orders:
        lines.append(
            f"<b>#{order['order_number']}</b> — {order['customer_name']}\n"
            f"Telefon: {order['customer_phone'] or 'N/A'}\n"
            f"Jami: {format_price(order['total_price'])} | Holat: <i>{order['status']}</i>\n"
            f"Sana: {order['created_at']}\n"
        )

    await message.answer("\n\n".join(lines))

@dp.message(F.text == "🍔 Maxsulotlar")
async def cmd_products(message: Message):
    categories = await db.get_categories()
    if not categories:
        await message.answer("🍔 Hozircha aktiv kategoriyalar yo'q.")
        return

    lines = ["<b>🍔 Maxsulotlar bo'limlari:</b>"]
    for category in categories:
        lines.append(f"{category['icon']} {category['name']}")
    lines.append("\nKategoriya nomini kiriting, masalan: Burgerlar")

    await message.answer("\n".join(lines))

@dp.message()
async def cmd_category_products(message: Message):
    category_name = message.text.strip()
    category = await db.get_category_by_name(category_name)
    if not category:
        return

    products = await db.get_products_by_category(category['id'])
    if not products:
        await message.answer(f"{category['name']} bo'yicha maxsulotlar topilmadi.")
        return

    lines = [f"<b>📦 {category['name']} maxsulotlari:</b>"]
    for product in products:
        lines.append(
            f"<b>{product['name']}</b> — {format_price(product['price'])}\n"
            f"{product['badge']} | {product['description'] or 'Tavsif yo‘q.'}\n"
            f"{product['image_url'] or ''}\n"
        )

    await message.answer("\n\n".join(lines))

# ================== RUN BOT ==================
async def main():
    logging.basicConfig(level=logging.INFO)
    
    await db.connect()        # MySQL ga ulanish
    
    print("🚀 BIG BURGERS Admin Bot ishga tushdi!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())