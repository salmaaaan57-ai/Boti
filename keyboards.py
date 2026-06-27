from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_webapp_kb(webapp_url: str):
    # زر رئيسي يفتح صفحة الاستمارة داخل تليجرام
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 تعبئة الاستمارة", web_app=WebAppInfo(url=webapp_url))]
        ],
        resize_keyboard=True
    )

def get_admin_kb(user_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ قبول ونشر", callback_data=f"admin_approve_{user_id}")
    builder.button(text="❌ رفض", callback_data=f"admin_reject_{user_id}")
    builder.adjust(2)
    return builder.as_markup()
