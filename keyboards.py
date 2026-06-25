from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_agreement_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="أتعهد بالجدية وأوافق على الشروط", callback_data="agree_terms")
    return builder.as_markup()

def get_gender_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="ذكر", callback_data="gender_male")
    builder.button(text="أنثى", callback_data="gender_female")
    builder.adjust(2)
    return builder.as_markup()

# لوحة ديناميكية تتغير حسب الجنس
# لوحة ديناميكية تتغير حسب الجنس وتراعي المنطق الشرعي
def get_social_status_kb(gender: str):
    builder = InlineKeyboardBuilder()
    
    if gender == "أنثى":
        # تم حذف "متزوجة" لأنه لا يستقيم منطقياً ولا شرعياً
        statuses = ["بكر", "مطلقة", "أرملة"] 
    else:
        # الرجل يتاح له "متزوج" لغرض التعدد
        statuses = ["أعزب", "متزوج", "مطلق", "أرمل"]
        
    for status in statuses:
        builder.button(text=status, callback_data=f"status_{status}")
        
    builder.adjust(2)
    return builder.as_markup()


def get_kids_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="لا يوجد", callback_data="kids_none")
    builder.button(text="نعم، معي", callback_data="kids_with_me")
    builder.button(text="نعم، مع الطرف الآخر", callback_data="kids_with_other")
    builder.adjust(1)
    return builder.as_markup()

def get_education_kb():
    builder = InlineKeyboardBuilder()
    for edu in ["ثانوي فما دون", "دبلوم", "بكالوريوس", "دراسات عليا"]:
        builder.button(text=edu, callback_data=f"edu_{edu}")
    builder.adjust(2)
    return builder.as_markup()

def get_prayer_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="محافظ على الصلاة", callback_data="pray_good")
    builder.button(text="أغلب الأوقات", callback_data="pray_average")
    builder.adjust(1)
    return builder.as_markup()

def get_smoking_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="نعم", callback_data="smoke_yes")
    builder.button(text="لا", callback_data="smoke_no")
    builder.adjust(2)
    return builder.as_markup()

def get_hijab_kb():
    builder = InlineKeyboardBuilder()
    for h in ["نقاب", "خمار", "حجاب عادي"]:
        builder.button(text=h, callback_data=f"hijab_{h}")
    builder.adjust(3)
    return builder.as_markup()

def get_country_kb():
    builder = InlineKeyboardBuilder()
    countries = ["السعودية", "مصر", "تركيا", "المغرب", "الجزائر", "أخرى"]
    for c in countries:
        builder.button(text=c, callback_data=f"country_{c}")
    builder.adjust(2)
    return builder.as_markup()

def get_travel_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="نعم، مستعد", callback_data="travel_yes")
    builder.button(text="لا، غير مستعد", callback_data="travel_no")
    builder.adjust(2)
    return builder.as_markup()

# الاختيار المتعدد الذكي
def get_marriage_types_kb(selected_keys: list):
    builder = InlineKeyboardBuilder()
    m_types = {
        "first": "زواج شرعي (أول)",
        "poly": "تعدد",
        "misyar": "مسيار"
    }
    for key, val in m_types.items():
        text = f"✅ {val}" if key in selected_keys else val
        builder.button(text=text, callback_data=f"mtype_{key}")
    builder.button(text="✅ تأكيد الاختيارات للانتقال", callback_data="mtype_confirm")
    builder.adjust(1)
    return builder.as_markup()

def get_housing_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="متوفر لدي", callback_data="house_mine")
    builder.button(text="أشترط توفره لدى الطرف الآخر", callback_data="house_other")
    builder.adjust(1)
    return builder.as_markup()

def get_admin_kb(user_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ قبول ونشر", callback_data=f"admin_approve_{user_id}")
    builder.button(text="❌ رفض", callback_data=f"admin_reject_{user_id}")
    builder.adjust(2)
    return builder.as_markup()

