from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_agreement_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="أتعهد بالجدية وأوافق على الشروط", callback_data="agree_terms")
    return kb.as_markup()

def get_gender_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="ذكر 👨", callback_data="gender_male")
    kb.button(text="أنثى 👩", callback_data="gender_female")
    kb.adjust(2)
    return kb.as_markup()

def get_social_status_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    statuses = ["أعزب / بكر", "متزوج (للرجال)", "مطلق / مطلقة", "أرمل / أرملة"]
    for s in statuses:
        kb.button(text=s, callback_data=f"status_{s}")
    kb.adjust(2)
    return kb.as_markup()

def get_kids_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="لا يوجد", callback_data="kids_none")
    kb.button(text="نعم، معي", callback_data="kids_with_me")
    kb.button(text="نعم، مع الطرف الآخر", callback_data="kids_with_other")
    kb.adjust(1)
    return kb.as_markup()

def get_education_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    levels = ["ثانوي فما دون", "دبلوم", "بكالوريوس", "ماجستير / دكتوراه"]
    for lvl in levels:
        kb.button(text=lvl, callback_data=f"edu_{lvl}")
    kb.adjust(2)
    return kb.as_markup()

def get_jobs_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    jobs = ["مجال طبي/صحي", "تعليم/أكاديميا", "هندسة/تقنية", "تجارة/أعمال", "موظف إداري", "لا أعمل", "أخرى"]
    for job in jobs:
        kb.button(text=job, callback_data=f"job_{job}")
    kb.adjust(2)
    return kb.as_markup()

def get_prayer_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="محافظ ولله الحمد", callback_data="pray_good")
    kb.button(text="أغلب الأوقات", callback_data="pray_average")
    kb.button(text="مقصر وأسأل الله الهداية", callback_data="pray_bad")
    kb.adjust(1)
    return kb.as_markup()

def get_smoking_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="نعم", callback_data="smoke_yes")
    kb.button(text="لا", callback_data="smoke_no")
    kb.button(text="أحياناً", callback_data="smoke_sometimes")
    kb.adjust(3)
    return kb.as_markup()

def get_hijab_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    styles = ["منتقبة", "محجبة عباءة", "محجبة عادي", "غير محجبة"]
    for style in styles:
        kb.button(text=style, callback_data=f"hijab_{style}")
    kb.adjust(2)
    return kb.as_markup()

def get_country_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    countries = ["تركيا 🇹🇷", "ألمانيا 🇩🇪", "ألبانيا 🇦🇱", "أخرى"]
    for country in countries:
        kb.button(text=country, callback_data=f"country_{country}")
    kb.adjust(2)
    return kb.as_markup()

def get_states_kb(country: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    states = []
    if "تركيا" in country:
        states = ["إسطنبول", "غازي عنتاب", "أنقرة", "مرسين", "بورصة", "هاتاي", "إزمير"]
    elif "ألمانيا" in country:
        states = ["برلين", "ميونخ", "هامبورغ", "كولونيا", "فرانكفورت", "دوسلدورف", "شتوتغارت"]
    elif "ألبانيا" in country:
        states = ["تيرانا", "دوريس", "فلوره", "شكودر", "كورتشا", "إلباسان", "بيرات"]
    
    for state in states:
        kb.button(text=state, callback_data=f"state_{state}")
    if not states:
        kb.button(text="إدخال يدوي", callback_data="state_manual")
    kb.adjust(2)
    return kb.as_markup()

def get_travel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="نعم، لا أمانع السفر/الانتقال", callback_data="travel_yes")
    kb.button(text="لا أرغب في الانتقال", callback_data="travel_no")
    kb.adjust(1)
    return kb.as_markup()

def get_marriage_types_kb(selected_types: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    types = ["مسيار (معلن أو غير معلن)", "شرعي موثق قانوناً", "شرعي بتوثيق عرفي", "شرعي زيارات"]
    for t in types:
        mark = "✅ " if t in selected_types else ""
        kb.button(text=f"{mark}{t}", callback_data=f"mtype_{t}")
    if selected_types:
        kb.button(text="💾 تأكيد الاختيارات", callback_data="mtype_confirm")
    kb.adjust(1)
    return kb.as_markup()

def get_housing_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="السكن متوفر لدي (للمسيار)", callback_data="house_mine")
    kb.button(text="أشترط توفر السكن لدى الطرف الآخر", callback_data="house_other")
    kb.adjust(1)
    return kb.as_markup()
