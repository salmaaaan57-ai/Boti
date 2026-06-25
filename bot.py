import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================================
# ⚙️ الإعدادات الأساسية 
# ==========================================
TOKEN = "8868061017:AAFHWqZAljMOwkFmzPRa5AHk7HwtRxESKwo"
ADMIN_ID = 7556662373             # ضع الآي دي الخاص بك هنا (كرقم بدون علامات تنصيص)
CHANNEL_ID = "-1003869521696"     # ضع آي دي القناة هنا (يجب أن يبدأ بـ -100)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ==========================================
# 📝 حالات الاستمارة (States)
# ==========================================
class Form(StatesGroup):
    agreement = State()
    name = State()
    age = State()
    specs = State()
    contact_info = State()

# ==========================================
# 🚀 البداية وزر التعهد
# ==========================================
@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish() 
    keyboard = InlineKeyboardMarkup()
    agree_btn = InlineKeyboardButton("أتعهد بالجدية وأوافق على الشروط", callback_data="agree")
    keyboard.add(agree_btn)
    
    await message.answer(
        "مرحباً بك في منصة ميثاق للزواج الشرعي.\nالرجاء قراءة الشروط والموافقة عليها:", 
        reply_markup=keyboard
    )
    await Form.agreement.set()

@dp.callback_query_handler(lambda c: c.data == 'agree', state=Form.agreement)
async def process_agreement(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "ما هو اسمك (الاسم الأول أو المستعار)؟")
    await Form.name.set()

# ==========================================
# ✍️ معالجة إدخالات المستخدم
# ==========================================
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer("كم عمرك؟")
    await Form.age.set()

@dp.message_handler(state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
    await message.answer("ما هي المواصفات التي تبحث عنها في شريك حياتك؟")
    await Form.specs.set()

@dp.message_handler(state=Form.specs)
async def process_specs(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['specs'] = message.text
    await message.answer("لضمان الجدية، الرجاء إدخال وسيلة تواصل صحيحة (رقم هاتف، أو معرف تليجرام يبدأ بـ @):")
    await Form.contact_info.set()

# ==========================================
# 📥 استلام البيانات وإرسالها للمدير (مع أزرار التحكم)
# ==========================================
@dp.message_handler(state=Form.contact_info)
async def process_contact(message: types.Message, state: FSMContext):
    user_contact = message.text
    user_id = message.from_user.id
    username = message.from_user.username
    auto_username = f"@{username}" if username else "غير متوفر"

    async with state.proxy() as data:
        # صياغة الاستمارة التي ستُنشر في القناة (بدون بيانات سرية)
        public_text = (
            f"📋 استمارة زواج جديدة\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 الاسم: {data['name']}\n"
            f"🎂 العمر: {data['age']}\n"
            f"📝 المواصفات المطلوبة:\n{data['specs']}\n"
            f"━━━━━━━━━━━━━━\n"
            f" للتواصل مع الحالة، يرجى مراسلة الإدارة."
        )
        
        # صياغة الاستمارة الخاصة بالإدارة (تحتوي على معلومات التواصل)
        admin_text = (
            f"⚠️ استمارة للمراجعة:\n\n"
            f"{public_text}\n\n"
            f"🔒 بيانات التواصل (سرية):\n"
            f"🆔 الآي دي: {user_id}\n"
            f"🔗 المعرف: {auto_username}\n"
            f"📞 وسيلة التواصل المدخلة: {user_contact}"
        )

    # إنشاء أزرار القبول والرفض للمدير
    admin_kb = InlineKeyboardMarkup(row_width=2)
    approve_btn = InlineKeyboardButton("✅ قبول ونشر", callback_data="approve_post")
    reject_btn = InlineKeyboardButton("❌ رفض", callback_data="reject_post")
    admin_kb.add(approve_btn, reject_btn)

    try:
        # إرسال الاستمارة للمدير فقط
        await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_kb)
        await message.answer("✅ تم استلام استمارتك بنجاح. سيتم مراجعتها من قبل الإدارة بسرية تامة.")
    except Exception as e:
        await message.answer("⚠️ حدث خطأ تقني. تأكد من أن المدير قام بتشغيل البوت.")
        logging.error(f"Error sending to admin: {e}")
    
    await state.finish()

# ==========================================
# ⚖️ نظام معالجة قرار الإدارة (القبول أو الرفض)
# ==========================================
@dp.callback_query_handler(lambda c: c.data in ['approve_post', 'reject_post'])
async def admin_decision(callback_query: types.CallbackQuery):
    # التأكد من أن الشخص الذي يضغط الزر هو المدير فعلاً
    if callback_query.from_user.id != ADMIN_ID:
        await bot.answer_callback_query(callback_query.id, "عذراً، هذا الإجراء مخصص للإدارة فقط.", show_alert=True)
        return

    # استخراج النص العام (public_text) من رسالة الإدارة لحذف البيانات السرية قبل النشر
    full_text = callback_query.message.text
    # نقطة القص: نفصل النص عند عبارة "بيانات التواصل (سرية)"
    public_post = full_text.split("🔒 بيانات التواصل (سرية):")[0].replace("⚠️ استمارة للمراجعة:\n\n", "")

    if callback_query.data == 'approve_post':
        try:
            # نشر الجزء العام فقط في القناة
            await bot.send_message(chat_id=CHANNEL_ID, text=public_post)
            # تحديث رسالة المدير لتعكس الحالة
            await callback_query.message.edit_text(f"{full_text}\n\n✅ [تم القبول والنشر في القناة]")
        except Exception as e:
            await callback_query.message.reply(f"⚠️ خطأ في النشر للقناة: تأكد من أن البوت مشرف في القناة.\nالخطأ: {e}")
            
    elif callback_query.data == 'reject_post':
        # تحديث رسالة المدير فقط
        await callback_query.message.edit_text(f"{full_text}\n\n❌ [تم الرفض]")

# ==========================================
# ⚙️ تشغيل البوت
# ==========================================
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
