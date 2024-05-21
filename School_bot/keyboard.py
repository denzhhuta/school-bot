from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

def main_reply_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text="Профіль 👤")
    b2 = KeyboardButton(text="Купівля уроків 💸")
    b3 = KeyboardButton(text="Підтримка 💬")
    b4 = KeyboardButton(text="Функціонал адміністратора 💿")
    kb.add(b1).add(b2).insert(b3).add(b4)
    return kb

def administrator_keyboard_markup() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text="Переглянути учнів 📄")
    b2 = KeyboardButton(text="Повідомлення підтримки 📩")
    b3 = KeyboardButton(text="Архів 🗑")
    back_button = KeyboardButton(text="Назад 🔙")
    kb.add(b1).add(b2).add(b3).insert(back_button)
    return kb

def support_button_markup() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text="Повідомити про проблему 📩")
    back_button = KeyboardButton(text="Назад 🔙")
    kb.add(b1).add(back_button)
    return kb
    
def lessons_payment_method(post_identifier) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Оплатити вручну', callback_data=f'manual_payment_{post_identifier}')],
        [InlineKeyboardButton('Оплатити через Телеграм', callback_data=f'telegram_payment_{post_identifier}')]
    ])
    return ikb

def credentials_reply_keyboard(user_id) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('📨 Підтвердити ел.адресу', callback_data=f'email_approval_{user_id}')],
        [InlineKeyboardButton('🎁 Реферальна система', callback_data='referral_system')]
    ])
    return ikb

def cancel_reply_keyboard() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('❌ Скасувати', callback_data='cancel_callback')],
    ])
    return ikb

def change_email_keyboard() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('☑️ Так', callback_data='change_email')],
        [InlineKeyboardButton('❌ Ні', callback_data='cancel_callback')]
    ])
    return ikb

def administrator_reply_keyboard(user_id) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('➖ Відняти урок', callback_data=f'lessons_substract_{user_id}')],
        [InlineKeyboardButton('➕ Додати урок', callback_data=f'lessons_add_{user_id}')],
        [InlineKeyboardButton('📣 Оповістити учня', callback_data=f'student_announcement_{user_id}')]
    ], resize_keyboard=True)
    return ikb

def administrator_telegram_message(user_id) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('❌ Скасувати', callback_data='cancel_callback')],
        [InlineKeyboardButton('📣 Оповіщення в телеграм', callback_data=f'message_telegram_{user_id}')]
    ])
    return ikb

def support_keyboard_markup(user_id, id) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('📤 Відповісти', callback_data=f'answer_{user_id}_{id}')],
        [InlineKeyboardButton('🗄 Видалити(архівувати)', callback_data=f'archive_{id}')]
    ])
    return ikb

