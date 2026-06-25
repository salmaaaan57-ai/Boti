import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================================
# ⚙️ الإعدادات الأساسية (ضع بياناتك هنا)
# ==========================================
TOKEN = "8787127714:AAEOsu05CBrLstCCs0OQWVMoA3f5TuVQ5CI"
ADMIN_ID = 7556662373             # الآي دي الرقمي الخاص بك
CHANNEL_ID = "-1003869521696"     # آي دي القناة ويجب أن يبدأ بـ -100

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# سجل مؤقت في الذاكرة لتتبع المستخدمين الذين وافقوا على الشروط
USER_STATUS = {}

# ==========================================
# 🚀 أمر البداية وزر التعهد
# ==========================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    USER_STATUS[user_id] = "started"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="أتعهد بالجدية وأوافق على الشروط", callback_data="agree_shroot")]
    ])
    
    await message.answer(
        "مرحباً بك في منصة ميثاق للزواج الشرعي والمسيار.\n\n"
        "الرجاء الضغط على الزر أدناه للموافقة على الشروط والبدء في ملء الاستمارة:", 
        reply_markup=kb
    )

# ==========================================
# 🔄 معالجة الضغط على زر التعهد
# ==========================================
@dp.callback_query(F.data == "agree_shroot")
async def process_agreement(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    USER_STATUS[user_id] = "waiting_form"
    
    await callback_query.answer()
    
    template = (
        "✍️ نظام الاستمارة الموحدة\n\n"
        "قم بنسخ النص التالي، املأ البيانات في رسالة واحدة، ثم أرسلها هنا في المحادثة:\n\n"
        "الاسم أو اللقب:\n"
        "العمر:\n"
        "مكان الإقامة:\n"
        "المواصفات المطلوبة في الطرف الآخر:\n"
        "وسيلة التواصل الشخصية (رقم هاتف أو معرف خاص):"
    )
    await callback_query.message.answer(template)

# ==========================================
# 📥 استلام الاستمارة الموحدة وإرسالها للمدير
# ==========================================
@dp.message(F.text)
async def handle_submission(message: types.Message):
    user_id = message.from_user.id
    
    # التحقق من أن المستخدم ضغط على الزر أولاً وفي حالة انتظار الاستمارة
    if USER_STATUS.get(user_id) == "waiting_form":
        username = message.from_user.username
        auto_username = f"@{username}" if username else "مخفي أو غير محدد"
        
        # صياغة الرسالة التي ستصل للمدير للمراجعة
        admin_text = (
            f"⚠️ استمارة جديدة للمراجعة:\n\n"
            f"{message.text}\n\n"
            f"🔒 بيانات تقنية (سرية للإدارة):\n"
            f"🆔 الآي دي: {user_id}\n"
            f"🔗 المعرف التلقائي: {auto_username}"
        )
        
        # أزرار التحكم الخاصة بالمدير
        admin_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ قبول ونشر", callback_data=f"accept_{user_id}"),
                InlineKeyboardButton(text="❌ رفض", callback_data=f"reject_{user_id}")
            ]
        ])
        
        try:
            await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_kb)
            await message.answer("✅ تم استلام استمارتك بنجاح. سيتم مراجعتها من قبل الإدارة ونشرها بسرية تامة.")
            USER_STATUS[user_id] = "submitted"
        except Exception as e:
            await message.answer("⚠️ حدث خطأ أثناء إرسال استمارتك للإدارة، الرجاء المحاولة لاحقاً.")
            logging.error(f"Failed to send to admin: {e}")

# ==========================================
# ⚖️ لوحة تحكم المدير (القبول والرفض)
# ==========================================
@dp.callback_query(F.data.startswith("accept_") | F.data.startswith("reject_"))
async def admin_decision(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("عذراً، هذا الإجراء مخصص للإدارة فقط.", show_alert=True)
        return

    full_text = callback_query.message.text
    action = callback_query.data.split("_")[0]
    
    # فصل النص العام عن البيانات التقنية السرية قبل النشر في القناة
    public_post = full_text.split("🔒 بيانات تقنية")[0].replace("⚠️ استمارة جديدة للمراجعة:\n\n", "")

    if action == "accept":
        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=public_post)
            await callback_query.message.edit_text(f"{full_text}\n\n✅ [تم القبول والنشر في القناة]")
        except Exception as e:
            await callback_query.message.reply(f"⚠️ خطأ في النشر: تأكد من صلاحيات البوت في القناة.\nالخطأ: {e}")
    
    elif action == "reject":
        await callback_query.message.edit_text(f"{full_text}\n\n❌ [تم رفض هذه الاستمارة]")
    
    await callback_query.answer()

# ==========================================
# ⚙️ تشغيل البوت عبر حلقة asyncio الحديثة
# ==========================================
async def main():
    logging.info("Starting bot...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
