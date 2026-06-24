from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    # 1. الميثاق
    agreement = State()
    
    # 2. البيانات الأساسية
    gender = State()
    age = State()
    social_status = State()
    kids = State()
    
    # 3. التكافؤ العلمي والمهني
    education = State()
    job = State()
    
    # 4. الجانب الديني والمظهري
    prayer = State()
    smoking = State()
    hijab = State()  # يطلب من النساء فقط
    
    # 5. البيانات الجسدية والصحية
    height = State()
    weight = State()
    skin_color = State()
    health = State()
    
    # 6. الإقامة والتنقل
    country = State()
    state_name = State()  # الولاية أو المدينة
    travel_willingness = State()
    
    # 7. أنماط الزواج
    marriage_type = State()
    housing = State()  # يطلب لمن اختار مسيار/زيارات
    
    # 8. المواصفات والنبذة
    partner_specs = State()
    bio = State()
