import asyncio
import logging
import json
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage

import keyboards as kb

logging.basicConfig(level=logging.INFO)

# ===============================================
# ⚙️ الإعدادات الأساسية
# ===============================================
TOKEN = "8787127714:AAEOsu05CBrLstCCs0OQWVMoA3f5TuVQ5CI"
ADMIN_ID = 7556662373
CHANNEL_ID = "-1003869521696"
WEBAPP_URL = "https://salmaaaaan57-ai.github.io/mithaq-form/"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ===============================================
# 🗄️ تهيئة قاعدة البيانات
# ===============================================
async def init_db():
    async with aiosqlite.connect('marriage_db.db') as db:
        # دمج البيانات في عمود JSON مرن لسهولة الاستدعاء
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, data TEXT, status TEXT DEFAULT 'pending'
        )''')
        # جدول الجلسات السرية
        await db.execute('''CREATE TABLE IF NOT EXISTS chat_sessions (
            user1_id INTEGER, user2_id INTEGER, is_active INTEGER DEFAULT 1,
            UNIQUE(user1_id, user2_id)
        )''')
        await db.commit()

# ===============================================
# 🚀 أوامر البداية ومعالجة البيانات
# ===============================================
@dp.message(CommandStart())
async def cmd_start(message: Message):
    # تنظيف أي جلسة سابقة لتجنب التداخل
    async with aiosqlite.connect('marriage_db.db') as db:
        await db.execute("DELETE FROM chat_sessions WHERE user1_id = ? OR user2_id = ?", (message.from_user.id, message.from_user.id))
        await db.commit()
        
    await message.answer(
        "مرحباً بك في منظومة ميثاق.\nاضغط على الزر بالأسفل لتعبئة استمارتك بدقة:",
        reply_markup=kb.get_webapp_kb(WEBAPP_URL)
    )

@dp.message(F.web_app_data)
async def process_webapp_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        user_id = message.from_user.id
        
        async with aiosqlite.connect('marriage_db.db') as db:
            await db.execute("INSERT OR REPLACE INTO users (user_id, data, status) VALUES (?, ?, 'pending')", 
                             (user_id, json.dumps(data, ensure_ascii=False)))
            await db.commit()

        await message.answer("✅ استلمنا استمارتك بنجاح، وهي الآن قيد المراجعة.", reply_markup=kb.get_webapp_kb(WEBAPP_URL))

        # توجيه الاستمارة للآدمن
        admin_text = f"📝 **استمارة جديدة (مراجعة):**\n\n"
        for key, value in data.items():
            admin_text += f"▪️ **{key}:** {value}\n"
            
        await bot.send_message(ADMIN_ID, admin_text, reply_markup=kb.get_admin_kb(user_id))

    except Exception as e:
        logging.error(f"Error processing webapp data: {e}")
        await message.answer("❌ حدث خطأ تقني، نرجو المحاولة لاحقاً.")

# ===============================================
# 👑 لوحة تحكم الإدارة
# ===============================================
@dp.callback_query(F.data.startswith("admin_approve_"))
async def admin_approve(call: CallbackQuery):
    user_id = int(call.data.split("_")[2])
    
    async with aiosqlite.connect('marriage_db.db') as db:
        async with db.execute("SELECT data FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return await call.answer("المستخدم غير مسجل", show_alert=True)
            
            data = json.loads(row[0])
            await db.execute("UPDATE users SET status = 'approved' WHERE user_id = ?", (user_id,))
            await db.commit()

    # صياغة بطاقة العرض للقناة
    public_card = f"📌 **بطاقة رقم: {user_id}**\n\n"
    public_card += f"العمر: {data.get('age')} | الجنس: {data.get('gender')}\n"
    public_card += f"الحالة: {data.get('social_status')} | الإقامة: {data.get('country')}\n"
    public_card += f"المهنة: {data.get('job')} | التعليم: {data.get('education')}\n\n"
    public_card += f"نبذة: {data.get('bio')}\n"

    await bot.send_message(CHANNEL_ID, public_card, reply_markup=kb.get_contact_request_kb(user_id))
    await call.message.edit_text("✅ تم الموافقة وتم النشر في القناة.")
    await bot.send_message(user_id, "🎉 تمت الموافقة على استمارتك ونشر بطاقتك بنجاح.")

@dp.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject(call: CallbackQuery):
    user_id = int(call.data.split("_")[2])
    await bot.send_message(user_id, "❌ نعتذر، تم رفض استمارتك لمخالفتها الشروط.")
    await call.message.edit_text("❌ تم الرفض وإشعار المستخدم.")

# ===============================================
# 💬 منظومة المحادثة المجهولة
# ===============================================
@dp.callback_query(F.data.startswith("req_contact_"))
async def request_contact(call: CallbackQuery):
    target_id = int(call.data.split("_")[2])
    requester_id = call.from_user.id
    
    if target_id == requester_id:
        return await call.answer("لا يمكنك طلب التواصل مع نفسك!", show_alert=True)
        
    await bot.send_message(target_id, f"📩 لديك طلب تواصل جديد من حساب مجهول مهتم ببطاقتك!\nهل توافق على فتح محادثة سرية؟", reply_markup=kb.get_accept_chat_kb(requester_id))
    await call.answer("✅ تم إرسال طلبك. سيتم إشعارك إذا تمت الموافقة.", show_alert=True)

@dp.callback_query(F.data.startswith("accept_chat_"))
async def accept_chat(call: CallbackQuery):
    requester_id = int(call.data.split("_")[2])
    target_id = call.from_user.id

    async with aiosqlite.connect('marriage_db.db') as db:
        await db.execute("DELETE FROM chat_sessions WHERE user1_id IN (?, ?) OR user2_id IN (?, ?)", (requester_id, target_id, requester_id, target_id))
        await db.execute("INSERT INTO chat_sessions (user1_id, user2_id) VALUES (?, ?)", (requester_id, target_id))
        await db.commit()

    await call.message.edit_text("✅ تم قبول المحادثة.")
    
    chat_msg = "🔒 **تم تفعيل المحادثة السرية!**\nالرسائل المرسلة هنا تُنقل للطرف الآخر تلقائياً دون إظهار حسابك. للإنهاء اضغط الزر بالأسفل."
    await bot.send_message(requester_id, chat_msg, reply_markup=kb.get_end_chat_kb())
    await bot.send_message(target_id, chat_msg, reply_markup=kb.get_end_chat_kb())

@dp.callback_query(F.data.startswith("reject_chat_"))
async def reject_chat(call: CallbackQuery):
    requester_id = int(call.data.split("_")[2])
    await call.message.edit_text("تم رفض الطلب.")
    await bot.send_message(requester_id, "❌ اعتذر الطرف الآخر عن قبول المحادثة.")

@dp.message(F.text == "🛑 إنهاء المحادثة السرية")
async def end_chat(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect('marriage_db.db') as db:
        async with db.execute("SELECT user1_id, user2_id FROM chat_sessions WHERE user1_id = ? OR user2_id = ?", (user_id, user_id)) as cursor:
            session = await cursor.fetchone()
            if session:
                other_user = session[1] if session[0] == user_id else session[0]
                await db.execute("DELETE FROM chat_sessions WHERE user1_id = ? OR user2_id = ?", (user_id, user_id))
                await db.commit()
                await bot.send_message(other_user, "🛑 قام الطرف الآخر بإنهاء الجلسة.", reply_markup=kb.get_webapp_kb(WEBAPP_URL))
                await message.answer("✅ تم إنهاء الجلسة من طرفك بنجاح.", reply_markup=kb.get_webapp_kb(WEBAPP_URL))
            else:
                await message.answer("لا توجد محادثة نشطة.", reply_markup=kb.get_webapp_kb(WEBAPP_URL))

# المحرك الناقل للرسائل (لا يلتقط الأوامر أو بيانات الواجهة)
@dp.message(~F.text.in_(["🛑 إنهاء المحادثة السرية", "/start"]) & ~F.web_app_data)
async def chat_relay(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect('marriage_db.db') as db:
        async with db.execute("SELECT user1_id, user2_id FROM chat_sessions WHERE (user1_id = ? OR user2_id = ?) AND is_active = 1", (user_id, user_id)) as cursor:
            session = await cursor.fetchone()
            
            if session:
                target_id = session[1] if session[0] == user_id else session[0]
                try:
                    await message.copy_to(chat_id=target_id)
                except Exception as e:
                    await message.answer("❌ فشل الإرسال، قد يكون الطرف الآخر قام بحظر البوت.")

# ===============================================
# بدء البوت
# ===============================================
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

