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
TOKEN = "8787127714:AAEOsu05CBrLstCCs0OQWVMoA3f5TuVQ5CI"

# =========== إعدادات الإدارة والقناة ===========
ADMIN_ID = 7556662373  
CHANNEL_ID = -1003869521696 
# ===============================================

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def init_db():
    async with aiosqlite.connect('marriage_db.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, name TEXT, gender TEXT, age TEXT, 
            social_status TEXT, kids TEXT, education TEXT, job TEXT, 
            prayer TEXT, smoking TEXT, hijab TEXT, height TEXT, weight TEXT, 
            skin_color TEXT, health TEXT, country TEXT, state_name TEXT, 
            travel_willingness TEXT, marriage_type TEXT, housing TEXT, 
            partner_specs TEXT, bio TEXT, edit_count INTEGER DEFAULT 0)''')
        
        try:
            await db.execute("ALTER TABLE users ADD COLUMN name TEXT")
            await db.execute("ALTER TABLE users ADD COLUMN edit_count INTEGER DEFAULT 0")
        except:
            pass
        await db.commit()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    async with aiosqlite.connect('marriage_db.db') as db:
        async with db.execute('SELECT edit_count FROM users WHERE user_id = ?', (message.from_user.id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                edit_count = row[0]
                if edit_count >= 1:
                    await message.answer("عذراً، لديك بطاقة مسجلة بالفعل. لقد استنفدت الحد الأقصى المسموح به لتعديل البيانات لضمان المصداقية.")
                else:
                    await message.answer("لديك بطاقة مسجلة مسبقاً. تنبيه: يسمح لك بتعديل بياناتك مرة واحدة فقط.", reply_markup=kb.get_edit_kb())
                return

    welcome_text = "بسم الله الرحمن الرحيم\nأهلاً بك في مسار العفة.\nنرجو التعهد بالجدية والمصداقية التامة للبدء."
    await message.answer(welcome_text, reply_markup=kb.get_agreement_kb())
    await state.set_state(Registration.agreement)

@dp.callback_query(F.data == "edit_profile")
async def process_edit_profile(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("سنبدأ بتحديث بياناتك. يرجى التعهد بالجدية:", reply_markup=kb.get_agreement_kb())
    await state.set_state(Registration.agreement)
    async with aiosqlite.connect('marriage_db.db') as db:
        await db.execute('UPDATE users SET edit_count = 1 WHERE user_id = ?', (callback.from_user.id,))
        await db.commit()

@dp.callback_query(Registration.agreement, F.data == "agree_terms")
async def process_agreement(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✅ جزاك الله خيراً.\n\nما هو الاسم أو اللقب الذي تفضل استخدامه في بطاقتك؟")
    await state.set_state(Registration.name)

@dp.message(Registration.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("يرجى تحديد الجنس:", reply_markup=kb.get_gender_kb())
    await state.set_state(Registration.gender)

@dp.callback_query(Registration.gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    gender = "ذكر" if "male" in callback.data else "أنثى"
    await state.update_data(gender=gender)
    await callback.message.edit_text("كم يبلغ العمر؟ (يرجى كتابة أرقام فقط، مثال: 35)")
    await state.set_state(Registration.age)

@dp.message(Registration.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("يرجى إدخال العمر كـ **رقم** فقط:")
        return
    await state.update_data(age=message.text)
    await message.answer("ما هي الحالة الاجتماعية؟", reply_markup=kb.get_social_status_kb())
    await state.set_state(Registration.social_status)

@dp.callback_query(Registration.social_status, F.data.startswith("status_"))
async def process_status(callback: CallbackQuery, state: FSMContext):
    status = callback.data.replace("status_", "")
    await state.update_data(social_status=status)
    if "بكر" in status or "أعزب" in status:
        await state.update_data(kids="لا يوجد")
        await callback.message.edit_text("ما هو المستوى التعليمي؟", reply_markup=kb.get_education_kb())
        await state.set_state(Registration.education)
    else:
        await callback.message.edit_text("هل يوجد أبناء؟", reply_markup=kb.get_kids_kb())
        await state.set_state(Registration.kids)

@dp.callback_query(Registration.kids, F.data.startswith("kids_"))
async def process_kids(callback: CallbackQuery, state: FSMContext):
    kids_map = {"kids_none": "لا يوجد", "kids_with_me": "نعم، معي", "kids_with_other": "نعم، مع الطرف الآخر"}
    await state.update_data(kids=kids_map.get(callback.data))
    await callback.message.edit_text("ما هو المستوى التعليمي؟", reply_markup=kb.get_education_kb())
    await state.set_state(Registration.education)

@dp.callback_query(Registration.education, F.data.startswith("edu_"))
async def process_education(callback: CallbackQuery, state: FSMContext):
    edu = callback.data.replace("edu_", "")
    await state.update_data(education=edu)
    await callback.message.edit_text("ما هو المجال المهني؟", reply_markup=kb.get_jobs_kb())
    await state.set_state(Registration.job)

@dp.callback_query(Registration.job, F.data.startswith("job_"))
async def process_job(callback: CallbackQuery, state: FSMContext):
    job = callback.data.replace("job_", "")
    await state.update_data(job=job)
    await callback.message.edit_text("كيف تصف التزامك بالصلاة؟", reply_markup=kb.get_prayer_kb())
    await state.set_state(Registration.prayer)

@dp.callback_query(Registration.prayer, F.data.startswith("pray_"))
async def process_prayer(callback: CallbackQuery, state: FSMContext):
    pray_map = {"pray_good": "محافظ", "pray_average": "أغلب الأوقات", "pray_bad": "مقصر"}
    await state.update_data(prayer=pray_map.get(callback.data))
    await callback.message.edit_text("هل تدخن؟", reply_markup=kb.get_smoking_kb())
    await state.set_state(Registration.smoking)

@dp.callback_query(Registration.smoking, F.data.startswith("smoke_"))
async def process_smoking(callback: CallbackQuery, state: FSMContext):
    smoke_map = {"smoke_yes": "نعم", "smoke_no": "لا", "smoke_sometimes": "أحياناً"}
    await state.update_data(smoking=smoke_map.get(callback.data))
    
    data = await state.get_data()
    if data.get("gender") == "أنثى":
        await callback.message.edit_text("ما هو نمط الحجاب؟", reply_markup=kb.get_hijab_kb())
        await state.set_state(Registration.hijab)
    else:
        await state.update_data(hijab="لا ينطبق (ذكر)")
        await callback.message.edit_text("كم يبلغ الطول تقريباً؟ (مثال: 175)")
        await state.set_state(Registration.height)

@dp.callback_query(Registration.hijab, F.data.startswith("hijab_"))
async def process_hijab(callback: CallbackQuery, state: FSMContext):
    hijab = callback.data.replace("hijab_", "")
    await state.update_data(hijab=hijab)
    await callback.message.edit_text("كم يبلغ الطول تقريباً؟ (مثال: 160)")
    await state.set_state(Registration.height)

@dp.message(Registration.height)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.answer("كم يبلغ الوزن تقريباً؟ (مثال: 70)")
    await state.set_state(Registration.weight)

@dp.message(Registration.weight)
async def process_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.answer("ما هو لون البشرة؟ (أبيض، حنطي، أسمر)")
    await state.set_state(Registration.skin_color)

@dp.message(Registration.skin_color)
async def process_skin(message: Message, state: FSMContext):
    await state.update_data(skin_color=message.text)
    await message.answer("هل تعاني من أي أمراض مزمنة؟ (سليم ولله الحمد، أو اذكر الحالة)")
    await state.set_state(Registration.health)

@dp.message(Registration.health)
async def process_health(message: Message, state: FSMContext):
    await state.update_data(health=message.text)
    await message.answer("أين الإقامة الحالية؟", reply_markup=kb.get_country_kb())
    await state.set_state(Registration.country)

@dp.callback_query(Registration.country, F.data.startswith("country_"))
async def process_country(callback: CallbackQuery, state: FSMContext):
    country = callback.data.replace("country_", "")
    await state.update_data(country=country)
    if country == "أخرى":
        await callback.message.edit_text("يرجى كتابة اسم الدولة والمدينة:")
        await state.set_state(Registration.state_name)
    else:
        await callback.message.edit_text(f"اختر الولاية أو المدينة في {country}:", reply_markup=kb.get_states_kb(country))
        await state.set_state(Registration.state_name)

@dp.callback_query(Registration.state_name, F.data.startswith("state_"))
async def process_state_btn(callback: CallbackQuery, state: FSMContext):
    state_name = callback.data.replace("state_", "")
    if state_name == "manual":
        await callback.message.edit_text("يرجى كتابة اسم الولاية أو المدينة:")
        return 
    await state.update_data(state_name=state_name)
    await callback.message.edit_text("هل لديك مرونة في الانتقال أو السفر؟", reply_markup=kb.get_travel_kb())
    await state.set_state(Registration.travel_willingness)

@dp.message(Registration.state_name)
async def process_state_text(message: Message, state: FSMContext):
    await state.update_data(state_name=message.text)
    await message.answer("هل لديك مرونة في الانتقال أو السفر؟", reply_markup=kb.get_travel_kb())
    await state.set_state(Registration.travel_willingness)

@dp.callback_query(Registration.travel_willingness, F.data.startswith("travel_"))
async def process_travel(callback: CallbackQuery, state: FSMContext):
    travel = "نعم" if "yes" in callback.data else "لا"
    await state.update_data(travel_willingness=travel, selected_mtypes=[])
    await callback.message.edit_text("ما هي أنماط الزواج المقبولة؟ (يمكن اختيار أكثر من نمط):", reply_markup=kb.get_marriage_types_kb([]))
    await state.set_state(Registration.marriage_type)

@dp.callback_query(Registration.marriage_type, F.data.startswith("mtype_"))
async def process_mtype(callback: CallbackQuery, state: FSMContext):
    action = callback.data.replace("mtype_", "")
    data = await state.get_data()
    selected_mtypes = data.get("selected_mtypes", [])

    if action == "confirm":
        joined_mtypes = " و ".join(selected_mtypes)
        await state.update_data(marriage_type=joined_mtypes)
        
        if any("مسيار" in t or "زيارات" in t for t in selected_mtypes):
            await callback.message.edit_text("بخصوص السكن في زواج المسيار:", reply_markup=kb.get_housing_kb())
            await state.set_state(Registration.housing)
        else:
            await state.update_data(housing="زواج شرعي اعتيادي")
            await ask_partner_specs(callback.message, state)
    else:
        if action in selected_mtypes:
            selected_mtypes.remove(action)
        else:
            selected_mtypes.append(action)
        await state.update_data(selected_mtypes=selected_mtypes)
        await callback.message.edit_reply_markup(reply_markup=kb.get_marriage_types_kb(selected_mtypes))

@dp.callback_query(Registration.housing, F.data.startswith("house_"))
async def process_housing(callback: CallbackQuery, state: FSMContext):
    house = "متوفر لدي" if "mine" in callback.data else "أشترط توفره لدى الطرف الآخر"
    await state.update_data(housing=house)
    await ask_partner_specs(callback.message, state)

async def ask_partner_specs(message, state: FSMContext):
    await message.edit_text("ما هي أهم صفتين أو ثلاث لا تتنازل عنها في الشريك؟")
    await state.set_state(Registration.partner_specs)

@dp.message(Registration.partner_specs)
async def process_partner_specs(message: Message, state: FSMContext):
    await state.update_data(partner_specs=message.text)
    await message.answer("أخيراً.. تحدث عن نفسك وطباعك باختصار:")
    await state.set_state(Registration.bio)

@dp.message(Registration.bio)
async def process_bio(message: Message, state: FSMContext):
    await state.update_data(bio=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    
    async with aiosqlite.connect('marriage_db.db') as db:
        await db.execute('''INSERT INTO users 
            (user_id, name, gender, age, social_status, kids, education, job, prayer, smoking, 
            hijab, height, weight, skin_color, health, country, state_name, 
            travel_willingness, marriage_type, housing, partner_specs, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            name=excluded.name, gender=excluded.gender, age=excluded.age, social_status=excluded.social_status,
            kids=excluded.kids, education=excluded.education, job=excluded.job, prayer=excluded.prayer,
            smoking=excluded.smoking, hijab=excluded.hijab, height=excluded.height, weight=excluded.weight,
            skin_color=excluded.skin_color, health=excluded.health, country=excluded.country, state_name=excluded.state_name,
            travel_willingness=excluded.travel_willingness, marriage_type=excluded.marriage_type, housing=excluded.housing,
            partner_specs=excluded.partner_specs, bio=excluded.bio
            ''', 
            (user_id, data.get('name'), data.get('gender'), data.get('age'), data.get('social_status'), 
            data.get('kids'), data.get('education'), data.get('job'), data.get('prayer'), 
            data.get('smoking'), data.get('hijab'), data.get('height'), data.get('weight'), 
            data.get('skin_color'), data.get('health'), data.get('country'), data.get('state_name'), 
            data.get('travel_willingness'), data.get('marriage_type'), data.get('housing'), 
            data.get('partner_specs'), data.get('bio')))
        await db.commit()

    profile_summary = (f"✅ **تم حفظ البيانات بنجاح!**\n\n"
                       f"الاسم/اللقب: {data.get('name')}\n"
                       f"النوع: {data.get('gender')} | العمر: {data.get('age')}\n"
                       f"الحالة: {data.get('social_status')}\n"
                       f"أنماط الزواج: {data.get('marriage_type')}\n"
                       f"السكن: {data.get('housing')}\n\n"
                       f"**البحث والربط سيتم تفعيله وإيصال المستخدمين ببعض عند بداية شهر 8.**")
    
    await message.answer(profile_summary, parse_mode="Markdown")
    
    admin_card = (f"📌 **طلب تسجيل جديد للمراجعة**\n"
                  f"الاسم: {data.get('name')} | المعرف: `{user_id}`\n"
                  f"الجنس: {data.get('gender')} | العمر: {data.get('age')}\n"
                  f"الحالة: {data.get('social_status')} | الأبناء: {data.get('kids')}\n"
                  f"الإقامة: {data.get('country')} - {data.get('state_name')}\n"
                  f"الزواج: {data.get('marriage_type')} | السكن: {data.get('housing')}\n"
                  f"الوظيفة: {data.get('job')} | الصلاة: {data.get('prayer')}\n"
                  f"شروط الشريك: {data.get('partner_specs')}\n"
                  f"نبذة: {data.get('bio')}")
    
    try:
        await bot.send_message(ADMIN_ID, admin_card, reply_markup=kb.get_admin_kb(user_id), parse_mode="Markdown")
    except Exception as e:
        print(f"لم يتم إرسال رسالة الإدارة. الخطأ: {e}")

    await state.clear()

@dp.callback_query(F.data.startswith("admin_approve_"))
async def admin_approve(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[2])
    card_text = callback.message.text.replace("📌 **طلب تسجيل جديد للمراجعة**\n", "")
    public_card = f"📢 **استمارة جديدة**\n{card_text}\n\nللتواصل، يرجى حفظ رقم الاستمارة."
    
    try:
        await bot.send_message(CHANNEL_ID, public_card, parse_mode="Markdown")
        await callback.message.edit_text(f"{callback.message.text}\n\n✅ **تم النشر في القناة.**")
    except Exception as e:
        await callback.answer(f"حدث خطأ أثناء النشر: {e}", show_alert=True)

@dp.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject(callback: CallbackQuery):
    await callback.message.edit_text(f"{callback.message.text}\n\n❌ **تم الرفض.**")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
