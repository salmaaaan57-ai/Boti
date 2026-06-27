import asyncio
import logging
import json
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage

import keyboards as kb

logging.basicConfig(level=logging.INFO)

# ===============================================
# ⚙️ الإعدادات الأساسية
# ===============================================
TOKEN = "8787127714:AAEOsu05CBrLstCCs0OQWVMoA3f5TuVQ5CI" # توكن البوت
ADMIN_ID = 7556662373         # رقمك التعريفي
CHANNEL_ID = "-1003869521696" # معرف القناة
WEBAPP_URL = "ضع_رابط_موقعك_هنا" # سنضع هنا رابط Github Pages لاحقاً

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ===============================================
# 🗄️ تهيئة قاعدة البيانات (مع الأعمدة الجديدة)
# ===============================================
async def init_db():
    async with aiosqlite.connect('marriage_db.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, name TEXT, gender TEXT, age TEXT, 
            social_status TEXT, kids TEXT, education TEXT, job TEXT, prayer TEXT, 
            smoking TEXT, hijab TEXT, height TEXT, weight TEXT, skin_color TEXT, 
            health TEXT, country TEXT, state_name TEXT, travel_willingness TEXT, 
            marriage_type TEXT, housing TEXT, partner_specs TEXT, contact_info TEXT, bio TEXT,
            requests_count INTEGER DEFAULT 0, is_premium INTEGER DEFAULT 0)''')
        
        # حماية البيانات القديمة وإضافة أعمدة الرصيد إن لم تكن موجودة
        try: await db.execute('ALTER TABLE users ADD COLUMN requests_count INTEGER DEFAULT 0')
        except: pass
        try: await db.execute('ALTER TABLE users ADD COLUMN is_premium INTEGER DEFAULT 0')
        except: pass
        
        await db.commit()

# ===============================================
# 🚀 البداية وفتح الاستمارة (Web App)
# ===============================================
@dp.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "بسم الله الرحمن الرحيم\n"
        "أهلاً بك في منصة ميثاق للزواج الشرعي.\n\n"
        "👇 **اضغط على الزر بالأسفل لتعبئة استمارتك بسرعة وسرية تامة.**"
    )
    # إرسال زر الويب
    await message.answer(welcome_text, reply_markup=kb.get_webapp_kb(WEBAPP_URL))

# ===============================================
# 📥 استقبال البيانات من صفحة الويب وحفظها
# ===============================================
@dp.message(F.web_app_data)
async def process_webapp_data(message: Message):
    # تفكيك البيانات القادمة من الـ HTML
    data = json.loads(message.web_app_data.data)
    
    user_id = message.from_user.id
    raw_username = message.from_user.username
    safe_username = f"@{raw_username}" if raw_username else "بدون معرف (مخفي)"

    await message.answer("🔄 **جاري مراجعة وحفظ الاستمارة...**")

    # الحفظ في قاعدة البيانات
    async with aiosqlite.connect('marriage_db.db') as db:
        await db.execute('''INSERT INTO users 
            (user_id, username, name, gender, age, social_status, kids, education, job, prayer, smoking, 
            hijab, height, weight, skin_color, health, country, state_name, travel_willingness, 
            marriage_type, housing, partner_specs, contact_info, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            username=excluded.username, name=excluded.name, gender=excluded.gender, age=excluded.age, 
            social_status=excluded.social_status, kids=excluded.kids, education=excluded.education, 
            job=excluded.job, prayer=excluded.prayer, smoking=excluded.smoking, hijab=excluded.hijab, 
            height=excluded.height, weight=excluded.weight, skin_color=excluded.skin_color, health=excluded.health, 
            country=excluded.country, state_name=excluded.state_name, travel_willingness=excluded.travel_willingness, 
            marriage_type=excluded.marriage_type, housing=excluded.housing, partner_specs=excluded.partner_specs, 
            contact_info=excluded.contact_info, bio=excluded.bio
            ''', 
            (user_id, safe_username, data.get('name'), data.get('gender'), data.get('age'), data.get('social_status'), 
            data.get('kids'), data.get('education'), data.get('job'), data.get('prayer'), data.get('smoking'), 
            data.get('hijab'), data.get('height'), data.get('weight'), data.get('skin_color'), data.get('health'), 
            data.get('country'), data.get('state_name'), data.get('travel_willingness'), data.get('marriage_type'), 
            data.get('housing'), data.get('partner_specs'), data.get('contact_info'), data.get('bio')))
        await db.commit()

    await message.answer("✅ **تم رفع بطاقتك بنجاح للإدارة للمراجعة.**")
    
    # إرسال البطاقة للإدارة
    admin_card = (f"📌 **طلب تسجيل جديد للمراجعة**\n"
                  f"الاسم: {data.get('name')} | الجنس: {data.get('gender')}\n"
                  f"العمر: {data.get('age')} | الحالة: {data.get('social_status')}\n"
                  f"الإقامة: {data.get('country')} - {data.get('state_name')}\n"
                  f"الزواج: {data.get('marriage_type')}\n"
                  f"الشروط: {data.get('partner_specs')}\n"
                  f"النبذة: {data.get('bio')}\n"
                  f"➖➖➖➖➖➖➖➖\n"
                  f"🔒 **بيانات الإدارة:**\n"
                  f"الآي دي: `{user_id}`\n"
                  f"المعرف: {safe_username}\n"
                  f"التواصل: {data.get('contact_info')}")
    try:
        await bot.send_message(ADMIN_ID, admin_card, reply_markup=kb.get_admin_kb(user_id), parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error sending admin card: {e}")

# ===============================================
# ⚖️ قرارات الإدارة (نشر/رفض)
# ===============================================
@dp.callback_query(F.data.startswith("admin_approve_"))
async def admin_approve(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[2])
    public_part = callback.message.text.split("➖➖➖➖➖➖➖➖")[0]
    card_text = public_part.replace("📌 **طلب تسجيل جديد للمراجعة**\n", "")
    public_card = f"📢 **استمارة جديدة (رقم: {user_id})**\n{card_text}\n\n📩 للتواصل مع هذه الاستمارة أرسل الأمر:\n`/connect {user_id}`"
    
    try:
        await bot.send_message(CHANNEL_ID, public_card, parse_mode="Markdown")
        await callback.message.edit_text(f"{callback.message.text}\n\n✅ **تم النشر.**")
    except Exception:
        await callback.answer("خطأ في النشر.", show_alert=True)

@dp.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject(callback: CallbackQuery):
    await callback.message.edit_text(f"{callback.message.text}\n\n❌ **تم الرفض.**")

# ===============================================
# 👑 أوامر الإدارة (منح الصلاحيات يدوياً) /grant
# ===============================================
@dp.message(Command("grant"))
async def grant_premium(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        target_id = int(message.text.split()[1])
    except:
        await message.answer("⚠️ الاستخدام الصحيح: `/grant [ID]`", parse_mode="Markdown")
        return
        
    async with aiosqlite.connect('marriage_db.db') as db:
        await db.execute("UPDATE users SET is_premium = 1 WHERE user_id = ?", (target_id,))
        await db.commit()
    
    await message.answer(f"✅ تم تفعيل الصلاحية اللامحدودة (Premium) للمستخدم: `{target_id}` بنجاح.", parse_mode="Markdown")
    try:
        await bot.send_message(target_id, "🎁 **مبارك!**\nقامت الإدارة بمنحك عضوية مميزة (Premium) استثنائية.\nيمكنك الآن إرسال طلبات تواصل غير محدودة.")
    except: pass

# ===============================================
# 💸 نظام الدفع (نجوم تليجرام) و العداد
# ===============================================
@dp.message(Command("connect"))
async def request_connection(message: Message):
    user_id = message.from_user.id
    try:
        target_id = int(message.text.split()[1])
    except:
        await message.answer("⚠️ للاستخدام اكتب: `/connect [رقم الاستمارة]`\nمثال: `/connect 123456789`", parse_mode="Markdown")
        return
        
    async with aiosqlite.connect('marriage_db.db') as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT requests_count, is_premium FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
        if not user_data:
            await message.answer("⚠️ يجب عليك تعبئة استمارتك أولاً عبر زر البداية.")
            return
            
        is_premium = user_data['is_premium']
        requests_count = user_data['requests_count']
        
        if is_premium == 1:
            await send_contact_notification(user_id, target_id)
            await message.answer(f"✅ تم إرسال طلب التواصل. *(باقة Premium)*", parse_mode="Markdown")
        else:
            if requests_count < 3:
                await db.execute("UPDATE users SET requests_count = requests_count + 1 WHERE user_id = ?", (user_id,))
                await db.commit()
                await send_contact_notification(user_id, target_id)
                await message.answer(f"✅ تم إرسال طلب التواصل.\n*(استهلكت {requests_count + 1} من أصل 3 طلبات مجانية)*", parse_mode="Markdown")
            else:
                await send_premium_invoice(message.chat.id)

async def send_contact_notification(sender_id, target_id):
    try:
        await bot.send_message(
            target_id, 
            f"📩 **إشعار تواصل!**\nهناك مستخدم مهتم بالتواصل معك.\nرقم بطاقته: `{sender_id}`\n\nلرؤية بطاقته والتواصل معه، تواصل مع الإدارة.",
            parse_mode="Markdown"
        )
    except: pass

async def send_premium_invoice(chat_id):
    prices = [LabeledPrice(label="باقة التواصل اللامحدود", amount=50)]
    await bot.send_invoice(
        chat_id=chat_id, title="تفعيل الباقة المفتوحة ⭐️",
        description="استنفدت طلباتك المجانية (3 طلبات).\nلتفعيل الباقة اللامحدودة، ادفع 50 نجمة.",
        payload="buy_premium", provider_token="", currency="XTR", prices=prices
    )

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    if message.successful_payment.invoice_payload == "buy_premium":
        async with aiosqlite.connect('marriage_db.db') as db:
            await db.execute("UPDATE users SET is_premium = 1 WHERE user_id = ?", (message.from_user.id,))
            await db.commit()
        await message.answer("✅ **تم الدفع بنجاح! حسابك الآن Premium.**")

# ===============================================
# ⚙️ الإقلاع
# ===============================================
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
