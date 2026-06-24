from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# 1. الميثاق والنية
def get_agreement_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="أتعهد بذلك وأوافق على الشروط", callback_data="agree_terms")
    return kb.as_markup()

# 2. الجنس
def get_gender_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="ذكر 👨", callback_data="gender_male")
    kb.button(text="أنثى 👩", callback_data="gender_female")
    kb.adjust(2)
    return kb.as_markup()

# 3. الحالة الاجتماعية
def get_social_status_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    statuses = ["أعزب / بكر", "متزوج", "مطلق", "أرمل"]
    for s in statuses:
        kb.button(text=s, callback_data=f"status_{s}")
    kb.adjust(2)
    return kb.as_markup()

# 4. الأبناء والحضانة
def get_kids_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="لا يوجد", callback_data="kids_none")
    kb.button(text="نعم، وهم معي", callback_data="kids_with_me")
    kb.button(text="نعم، مع الطرف الآخر", callback_data="kids_with_other")
    kb.adjust(1)
    return kb.as_markup()

# 5. المستوى التعليمي
def get_education_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    levels = ["ثانوي فما دون", "دبلوم", "بكالوريوس", "ماجستير / دكتوراه"]
    for lvl in levels:
        kb.button(text=lvl, callback_data=f"edu_{lvl}")
    kb.adjust(2)
    return kb.as_markup()

# 6. الوظيفة
def get_jobs_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    jobs = [
        "تجارة وأعمال حرة", "هندسة وتقنية معلومات", 
        "قطاع طبي وصحي", "تعليم وأكاديميا", 
        "خدمات لوجستية ونقل", "قطاع فني وحرفي", 
        "موظف إداري / حكومي", "أخرى"
    ]
    for job in jobs:
        kb.button(text=job, callback_data=f"job_{job}")
    kb.adjust(2)
    return kb.as_markup()

# 7. الالتزام بالصلاة
def get_prayer_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="محافظ ولله الحمد", callback_data="pray_good")
    kb.button(text="أغلب الأوقات", callback_data="pray_average")
    kb.button(text="مقصر وأسأل الله الهداية", callback_data="pray_bad")
    kb.adjust(1)
    return kb.as_markup()

# 8. التدخين
def get_smoking_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="نعم", callback_data="smoke_yes")
    kb.button(text="لا", callback_data="smoke_no")
    kb.button(text="أحياناً", callback_data="smoke_sometimes")
    kb.adjust(3)
    return kb.as_markup()

# 9. الحجاب والمظهر (للنساء فقط)
def get_hijab_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    styles = ["منتقبة", "محجبة عباءة", "محجبة عادي", "غير محجبة"]
    for style in styles:
        kb.button(text=style, callback_data=f"hijab_{style}")
    kb.adjust(2)
    return kb.as_markup()

# 10. الإقامة (البلد)
def get_country_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    countries = ["تركيا 🇹🇷", "ألمانيا 🇩🇪", "ألبانيا 🇦🇱", "أخرى"]
    for country in countries:
        kb.button(text=country, callback_data=f"country_{country}")
    kb.adjust(2)
    return kb.as_markup()

# 11. الولايات (ديناميكي بناءً على البلد)
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
    
    if not states: # في حال اختيار "أخرى"
        kb.button(text="إدخال يدوي", callback_data="state_manual")
        
    kb.adjust(2)
    return kb.as_markup()

# 12. قابلية السفر والتنقل
def get_travel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="نعم، لا أمانع السفر/الانتقال", callback_data="travel_yes")
    kb.button(text="لا أرغب في الانتقال", callback_data="travel_no")
    kb.adjust(1)
    return kb.as_markup()

# 13. أنماط الزواج (متعدد الاختيارات برمجياً في bot.py)
def get_marriage_types_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    types = [
        "شرعي موثق قانوناً", 
        "شرعي بتوثيق عرفي", 
        "شرعي زيارات", 
        "مسيار (معلن أو غير معلن)"
    ]
    for t in types:
        kb.button(text=t, callback_data=f"mtype_{t}")
    kb.adjust(1)
    return kb.as_markup()

# 14. السكن (يظهر فقط لمن يختار مسيار أو زيارات)
def get_housing_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="السكن متوفر لدي", callback_data="house_mine")
    kb.button(text="يشترط توفره من الطرف الآخر", callback_data="house_other")
    kb.adjust(1)
    return kb.as_markup()
