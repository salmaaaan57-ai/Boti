from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_webapp_kb(webapp_url: str):
    # العودة للزر السفلي لضمان عمل دالة tg.sendData برمجياً
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 تعبئة الاستمارة", web_app=WebAppInfo(url=webapp_url))]
        ],
        resize_keyboard=True
    )

def get_admin_kb(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ قبول ونشر", callback_data=f"admin_approve_{user_id}")
    builder.button(text="❌ رفض", callback_data=f"admin_reject_{user_id}")
    builder.adjust(2)
    return builder.as_markup()

def get_contact_request_kb(target_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✉️ طلب تواصل", callback_data=f"req_contact_{target_id}")
    return builder.as_markup()

def get_accept_chat_kb(requester_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ قبول المحادثة", callback_data=f"accept_chat_{requester_id}")
    builder.button(text="❌ رفض", callback_data=f"reject_chat_{requester_id}")
    builder.adjust(2)
    return builder.as_markup()

def get_end_chat_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🛑 إنهاء المحادثة السرية")]],
        resize_keyboard=True
    )

