import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from states import Registration
import keyboards as kb

logging.basicConfig(level=logging.INFO)

# ===============================================
# ⚙️ الإعدادات الأساسية
# ===============================================
TOKEN = "ضع_توكن_البوت_هنا"
ADMIN_ID = 123456789         # رقمك التعريفي
CHANNEL_ID = "-100123456789" # معرف القناة

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ===============================================
# 🗄️ تهيئة قاعدة البيانات
# ===============================================
async def init_db():
    async with aiosqlite.connect('marriage_db.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, name TEXT, gender TEXT, age TEXT, 
            social_status TEXT, kids TEXT, education TEXT, job TEXT, prayer TEXT, 
            smoking TEXT, hijab TEXT, height TEXT, weight TEXT, skin_color TEXT, 
            health TEXT, country TEXT, state_name TEXT, travel_willingness TEXT, 
            marriage_type TEXT, housing TEXT, partner_specs TEXT, contact_info TEXT, bio TEXT)''')
        await db.commit()

# ===============================================
# 🚀 التسلسل ومسار الاستمارة
# ===============================================
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    welcome_text = "بسم الله الرحمن الرحيم\nأهلاً بك في منصة ميثاق.\nنرجو التعهد بالجدية والمصداقية التامة للبدء."
    await message.answer(welcome_text, reply_markup=kb.get_agreement_kb())
    await state.set_state(Registration.agreement)

@dp.callback_query(Registration.agreement, F.data == "agree_terms")
async def process_agreement(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 **[سؤال 1 من 17]**\nما هو الاسم أو اللقب الذي تفضل استخدامه في بطاقتك؟")
    await state.set_state(Registration.name)

@dp.message(Registration.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📝 **[سؤال 2 من 17]**\nيرجى تحديد الجنس:", reply_markup=kb.get_gender_kb())
    await state.set_state(Registration.gender)

@dp.callback_query(Registration.gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    gender = "ذكر" if callback.data == "gender_male" else "أنثى"
    await state.update_data(gender=gender)
    await callback.message.edit_text("📝 **[سؤال 3 من 17]**\nكم يبلغ العمر؟ (يرجى كتابة أرقام فقط، مثال: 35)")
    await state.set_state(Registration.age)

@dp.message(Registration.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ يرجى إدخال العمر كـ **رقم** فقط:")
        return
    await state.update_data(age=message.text)
    
    data = await state.get_data()
    user_gender = data.get("gender")
    
    await message.answer(
        "📝 **[سؤال 4 من 17]**\nما هي الحالة الاجتماعية؟", 
        reply_markup=kb.get_social_status_kb(user_gender)
    )
    await state.set_state(Registration.social_status)

@dp.callback_query(Registration.social_status, F.data.startswith("status_"))
async def process_status(callback: CallbackQuery, state: FSMContext):
    status = callback.data.replace("status_", "")
    await state.update_data(social_status=status)
    if "بكر" in status or "أعزب" in status:
        await state.update_data(kids="لا يوجد")
        await callback.message.edit_text("📝 **[سؤال 5 من 17]**\nما هو المستوى التعليمي؟", reply_markup=kb.get_education_kb())
        await state.set_state(Registration.education)
    else:
        await callback.message.edit_text("📝 **[سؤال 5 من 17]**\nهل يوجد أبناء؟", reply_markup=kb.get_kids_kb())
        await state.set_state(Registration.kids)

@dp.callback_query(Registration.kids, F.data.startswith("kids_"))
async def process_kids(callback: CallbackQuery, state: FSMContext):
    kids_map = {"kids_none": "لا يوجد", "kids_with_me": "نعم، معي", "kids_with_other": "نعم، مع الطرف الآخر"}
    await state.update_data(kids=kids_map.get(callback.data))
    await callback.message.edit_text("📝 **[سؤال 6 من 17]**\nما هو المستوى التعليمي؟", reply_markup=kb.get_education_kb())
    await state.set_state(Registration.education)

@dp.callback_query(Registration.education, F.data.startswith("edu_"))
async def process_education(callback: CallbackQuery, state: FSMContext):
    await state.update_data(education=callback.data.replace("edu_", ""))
    await callback.message.edit_text("📝 **[سؤال 7 من 17]**\nما هو المجال المهني؟ (اكتب طبيعة العمل باختصار):")
    await state.set_state(Registration.job)

@dp.message(Registration.job)
async def process_job(message: Message, state: FSMContext):
    await state.update_data(job=message.text)
    await message.answer("📝 **[سؤال 8 من 17]**\nكيف تصف التزامك بالصلاة؟", reply_markup=kb.get_prayer_kb())
    await state.set_state(Registration.prayer)

@dp.callback_query(Registration.prayer, F.data.startswith("pray_"))
async def process_prayer(callback: CallbackQuery, state: FSMContext):
    pray_map = {"pray_good": "محافظ", "pray_average": "أغلب الأوقات"}
    await state.update_data(prayer=pray_map.get(callback.data))
    await callback.message.edit_text("📝 **[سؤال 9 من 17]**\nهل تدخن؟", reply_markup=kb.get_smoking_kb())
    await state.set_state(Registration.smoking)

@dp.callback_query(Registration.smoking, F.data.startswith("smoke_"))
async def process_smoking(callback: CallbackQuery, state: FSMContext):
    smoke_map = {"smoke_yes": "نعم", "smoke_no": "لا"}
    await state.update_data(smoking=smoke_map.get(callback.data))
    
    data = await state.get_data()
    if data.get("gender") == "أنثى":
        await callback.message.edit_text("📝 **[سؤال 10 من 17]**\nما هو نمط الحجاب؟", reply_markup=kb.get_hijab_kb())
        await state.set_state(Registration.hijab)
    else:
        await state.update_data(hijab="لا ينطبق (ذكر)")
        await callback.message.edit_text("📝 **[سؤال 10 من 17]**\nكم يبلغ الطول تقريباً؟ (مثال: 175)")
        await state.set_state(Registration.height)

@dp.callback_query(Registration.hijab, F.data.startswith("hijab_"))
async def process_hijab(callback: CallbackQuery, state: FSMContext):
    await state.update_data(hijab=callback.data.replace("hijab_", ""))
    await callback.message.edit_text("📝 **[سؤال 11 من 17]**\nكم يبلغ الطول تقريباً؟ (مثال: 160)")
    await state.set_state(Registration.height)

@dp.message(Registration.height)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.answer("📝 **[سؤال 12 من 17]**\nكم يبلغ الوزن تقريباً؟ (مثال: 70)")
    await state.set_state(Registration.weight)

@dp.message(Registration.weight)
async def process_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.answer("📝 **[سؤال 13 من 17]**\nما هو لون البشرة؟\n(مثال: أبيض، قمحي، أسمر، إلخ...)")
    await state.set_state(Registration.skin_color)

@dp.message(Registration.skin_color)
async def process_skin(message: Message, state: FSMContext):
    await state.update_data(skin_color=message.text)
    await message.answer("📝 **[سؤال 14 من 17]**\nهل تعاني من أي أمراض مزمنة؟\n(سليم ولله الحمد، أو اذكر الحالة)")
    await state.set_state(Registration.health)

@dp.message(Registration.health)
async def process_health(message: Message, state: FSMContext):
    await state.update_data(health=message.text)
    await message.answer("📝 **[سؤال 15 من 17]**\nأين الإقامة الحالية؟", reply_markup=kb.get_country_kb())
    await state.set_state(Registration.country)

@dp.callback_query(Registration.country, F.data.startswith("country_"))
async def process_country(callback: CallbackQuery, state: FSMContext):
    country = callback.data.replace("country_", "")
    await state.update_data(country=country)
    if country == "أخرى":
        await callback.message.edit_text("يرجى كتابة اسم الدولة والمدينة:")
        await state.set_state(Registration.state_name)
    else:
        await callback.message.edit_text(f"اكتب اسم الولاية أو المدينة في {country}:")
        await state.set_state(Registration.state_name)

@dp.message(Registration.state_name)
async def process_state_text(message: Message, state: FSMContext):
    await state.update_data(state_name=message.text)
    await message.answer("هل لديك مرونة في الانتقال أو السفر؟", reply_markup=kb.get_travel_kb())
    await state.set_state(Registration.travel_willingness)

@dp.callback_query(Registration.travel_willingness, F.data.startswith("travel_"))
async def process_travel(callback: CallbackQuery, state: FSMContext):
    travel = "نعم" if "yes" in callback.data else "لا"
    await state.update_data(travel_willingness=travel, selected_mtypes=[])
    await callback.message.edit_text(
        "📝 **[سؤال 16 من 17]**\nما هي أنماط الزواج المقبولة لك؟\n*(يمكنك اختيار أكثر من نمط، ثم اضغط تأكيد)*", 
        reply_markup=kb.get_marriage_types_kb([])
    )
    await state.set_state(Registration.marriage_type)

@dp.callback_query(Registration.marriage_type, F.data.startswith("mtype_"))
async def process_mtype(callback: CallbackQuery, state: FSMContext):
    action = callback.data.replace("mtype_", "")
    data = await state.get_data()
    selected = data.get("selected_mtypes", [])

    if action == "confirm":
        if not selected:
            await callback.answer("⚠️ يرجى اختيار نمط واحد على الأقل!", show_alert=True)
            return
        m_types_dict = {"first": "زواج شرعي (أول)", "poly": "تعدد", "misyar": "مسيار"}
        joined_mtypes = " و ".join([m_types_dict[k] for k in selected])
        await state.update_data(marriage_type=joined_mtypes)
        
        if "misyar" in selected:
            await callback.message.edit_text("بخصوص السكن في زواج المسيار:", reply_markup=kb.get_housing_kb())
            await state.set_state(Registration.housing)
        else:
            await state.update_data(housing="زواج شرعي اعتيادي")
            await ask_partner_specs(callback.message, state)
    else:
        if action in selected:
            selected.remove(action)
        else:
            selected.append(action)
        await state.update_data(selected_mtypes=selected)
        await callback.message.edit_reply_markup(reply_markup=kb.get_marriage_types_kb(selected))

@dp.callback_query(Registration.housing, F.data.startswith("house_"))
async def process_housing(callback: CallbackQuery, state: FSMContext):
    house = "متوفر لدي" if "mine" in callback.data else "أشترط توفره لدى الطرف الآخر"
    await state.update_data(housing=house)
    await ask_partner_specs(callback.message, state)

async def ask_partner_specs(message, state: FSMContext):
    await message.edit_text("📝 **[سؤال 17 من 17]**\nما هي أهم صفتين أو ثلاث لا تتنازل عنها في الشريك؟")
    await state.set_state(Registration.partner_specs)

@dp.message(Registration.partner_specs)
async def process_partner_specs(message: Message, state: FSMContext):
    await state.update_data(partner_specs=message.text)
    await message.answer("📞 كيف يمكن للإدارة التواصل معك عند التطابق؟\n(اكتب رقم هاتف، أو معرف تليجرام، أو إيميل):")
    await state.set_state(Registration.contact_info)

@dp.message(Registration.contact_info)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(contact_info=message.text)
    await message.answer("✍️ أخيراً.. تحدث عن نفسك وطباعك باختصار في سطرين:")
    await state.set_state(Registration.bio)

@dp.message(Registration.bio)
async def process_bio(message: Message, state: FSMContext):
    await state.update_data(bio=message.text)
    data = await state.get_data()
    
    user_id = message.from_user.id
    raw_username = message.from_user.username
    safe_username = f"@{raw_username}" if raw_username else "بدون معرف (مخفي)"

    await message.answer("⚠️ **تنبيه:**\nجاري حفظ الاستمارة، يرجى العلم أن التعديل لا يُتاح إلا لمرة واحدة فقط لضمان الجدية والموثوقية.")

    async with aiosqlite.connect('marriage_db.db') as db:
        await db.execute('''INSERT INTO users 
            (user_id, username, name, gender, age, social_status, kids, education, job, prayer, smoking, 
            hijab, height, weight, skin_color, health, country, state_name, 
            travel_willingness, marriage_type, housing, partner_specs, contact_info, bio)
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
        logging.error(f"Error: {e}")
    await state.clear()

@dp.callback_query(F.data.startswith("admin_approve_"))
async def admin_approve(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[2])
    public_part = callback.message.text.split("➖➖➖➖➖➖➖➖")[0]
    card_text = public_part.replace("📌 **طلب تسجيل جديد للمراجعة**\n", "")
    public_card = f"📢 **استمارة جديدة**\n{card_text}\nللتواصل، يرجى حفظ رقم الاستمارة ومراسلة الإدارة."
    
    try:
        await bot.send_message(CHANNEL_ID, public_card, parse_mode="Markdown")
        await callback.message.edit_text(f"{callback.message.text}\n\n✅ **تم النشر.**")
    except Exception as e:
        await callback.answer("خطأ في النشر.", show_alert=True)

@dp.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject(callback: CallbackQuery):
    await callback.message.edit_text(f"{callback.message.text}\n\n❌ **تم الرفض.**")

async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
