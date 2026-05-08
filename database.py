# database.py
import aiomysql
import logging
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            self.pool = await aiomysql.create_pool(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT", 3306)),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                db=os.getenv("DB_NAME"),
                charset='utf8mb4',
                autocommit=True,
                minsize=5,
                maxsize=20,
            )
            logging.info("✅ MySQL bazasi bilan muvaffaqiyatli ulandi!")
        except Exception as e:
            logging.error(f"❌ Ulanish xatosi: {e}")
            print("\n🔍 Hosting host nomini to'g'ri yozganingizni tekshiring!")
            raise

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def execute(self, query: str, params: tuple = None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())

    async def fetchone(self, query: str, params: tuple = None):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params or ())
                return await cur.fetchone()

    async def fetchall(self, query: str, params: tuple = None):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params or ())
                return await cur.fetchall()

    async def get_categories(self):
        return await self.fetchall(
            "SELECT id, name, icon FROM categories WHERE is_active=1 ORDER BY sort_order"
        )

    async def get_category_by_name(self, name: str):
        return await self.fetchone(
            "SELECT id, name FROM categories WHERE name=%s AND is_active=1",
            (name,)
        )

    async def get_products_by_category(self, category_id: int):
        return await self.fetchall(
            "SELECT id, name, description, price, image_url, badge "
            "FROM products WHERE category_id=%s AND is_active=1 ORDER BY sort_order",
            (category_id,)
        )

    async def get_recent_orders(self, limit: int = 10):
        return await self.fetchall(
            "SELECT order_number, customer_name, customer_phone, total_price, status, created_at "
            "FROM orders ORDER BY created_at DESC LIMIT %s",
            (limit,)
        )


db = Database()