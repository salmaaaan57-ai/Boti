import logging
import aiosqlite
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ضع التوكن هنا مباشرة
TOKEN = "8868061017:AAFHWqZAljMOwkFmzPRa5AHk7HwtRxESKwo"
# ضع معرف قناتك هنا (يجب أن يبدأ بـ -100)
ADMIN_CHANNEL_ID = -1003869521696

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

class Reg(StatesGroup):
    gender = State()
    age = State()
    status = State()
    bio = State()
    photo = State()

def get_kb(options):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=o)] for o in options], resize_keyboard=True)

@router.message(F.text == "/start")
async def cmd_start(msg: Message, state: FSMContext):
    async with aiosqlite.connect("marriage_bot.db") as db:
        async with db.execute("SELECT id FROM users WHERE id = ?", (msg.from_user.id,)) as cursor:
            if await cursor.fetchone():
                return await msg.answer("أنت مسجل بالفعل في النظام.")
    await msg.answer("مرحباً! ما هو جنسك؟", reply_markup=get_kb(["ذكر", "أنثى"]))
    await state.set_state(Reg.gender)

@router.message(Reg.gender)
async def p_gender(msg: Message, state: FSMContext):
    if not msg.text or msg.text not in ["ذكر", "أنثى"]:
        return await msg.answer("يرجى اختيار الجنس من الأزرار.")
    await state.update_data(gender=msg.text)
    await msg.answer("ما هو عمرك؟ (أدخل رقماً بين 18 و 70)")
    await state.set_state(Reg.age)

@router.message(Reg.age)
async def p_age(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit() or not (18 <= int(msg.text) <= 70):
        return await msg.answer("يرجى إدخال رقم صحيح بين 18 و 70.")
    await state.update_data(age=int(msg.text))
    await msg.answer("الحالة الاجتماعية:", reply_markup=get_kb(["أعزب", "متزوج", "مطلق"]))
    await state.set_state(Reg.status)

@router.message(Reg.status)
async def p_status(msg: Message, state: FSMContext):
    if not msg.text or msg.text not in ["أعزب", "متزوج", "مطلق"]:
        return await msg.answer("يرجى اختيار الحالة من الأزرار.")
    await state.update_data(status=msg.text)
    await msg.answer("اكتب نبذة عنك (أقصى 150 حرفاً):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Reg.bio)

@router.message(Reg.bio)
async def p_bio(msg: Message, state: FSMContext):
    if not msg.text or len(msg.text) > 150:
        return await msg.answer("النبذة مطلوبة ولا تتجاوز 150 حرفاً.")
    await state.update_data(bio=msg.text)
    await msg.answer("أرسل صورة سيلفي واضحة للتحقق.")
    await state.set_state(Reg.photo)

@router.message(Reg.photo, F.photo)
async def p_photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    photo_id = msg.photo[-1].file_id
    now = datetime.now().isoformat()
    try:
        async with aiosqlite.connect("marriage_bot.db", timeout=30) as db:
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute('''INSERT INTO users (id, gender, age, status, bio, photo_id, verified, created_at)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                             (msg.from_user.id, data['gender'], data['age'], data['status'], data['bio'], photo_id, 0, now))
            await db.commit()
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="توثيق ✅", callback_data=f"ver_{msg.from_user.id}")],
            [InlineKeyboardButton(text="رفض ❌", callback_data=f"rej_{msg.from_user.id}")]
        ])
        await bot.send_photo(ADMIN_CHANNEL_ID, photo_id,
                             caption=f"طلب جديد:\nID: {msg.from_user.id}\nالجنس: {data['gender']}\nالعمر: {data['age']}\nالحالة: {data['status']}\nالنبذة: {data['bio']}",
                             reply_markup=kb)
        await msg.answer("تم إرسال طلبك للمراجعة.")
    except Exception:
        logger.exception("Database error")
        await msg.answer("حدث خطأ تقني.")
    finally:
        await state.clear()

@router.callback_query(F.data.startswith(("ver_", "rej_")))
async def admin_callback(call: CallbackQuery):
    action, user_id = call.data.split("_")
    status = 1 if action == "ver" else 0
    async with aiosqlite.connect("marriage_db.db", timeout=30) as db: # اسم الملف الصحيح
        await db.execute("UPDATE users SET verified = ? WHERE id = ?", (status, user_id))
        await db.commit()
    await bot.send_message(int(user_id), "تم قبول طلبك!" if status == 1 else "تم رفض طلبك.")
    await call.message.edit_reply_markup(reply_markup=None)

async def main():
    async with aiosqlite.connect("marriage_bot.db") as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, gender TEXT, age INTEGER, status TEXT,
            bio TEXT, photo_id TEXT, verified INTEGER, created_at TIMESTAMP)''')
        await db.commit()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
