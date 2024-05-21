import aiogram
from aiogram import types, Bot, Dispatcher, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import Update
from aiogram.types.chat_member import ChatMemberMember, ChatMemberOwner, ChatMemberAdministrator
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message, ShippingOption, ShippingQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types.message import ContentType
from configuration import BOT_API, PAYMENT_API, EMAIL_NOTIFY, STRUCTURED_MESSAGE, ERRORS, STRUCTURED_MESSAGE_SUPPORT
from keyboard import *
from email_sender import generate_confirmation_code, send_email, payment_announcement
from db import *
from administrator import *
import re
import hashlib
import os
import emoji
import asyncio
# #class CheckSubscriptionUserMiddleware(BaseMiddleware):
# async def on_process_update(self, update: types.Update, data: dict):
#         if "message" in update:
#             this_user = update.message.from_user
#             if update.message.text:
#                 if "start" in update.message.text:
#                     return

#         elif "callback_query" in update:
#             this_user = update.callback_query.from_user

#         else:
#             this_user = None
            
#         if this_user is not None:
#             if not this_user.is_bot:
#                 user_id = this_user.id
#                 is_registered = await check_registration(user_id)
                
#                 if not is_registered:
#                     await bot.send_message(user_id, 
#                                            "<b>😔 Ви не пройшли регістрацію в боті!</b>", 
#                                            parse_mode="HTML")
#                     raise CancelHandler()
#                 else:
#                     pass
                
                
storage = MemoryStorage()
bot = aiogram.Bot(BOT_API)
dp = aiogram.Dispatcher(bot, storage=storage)


post_mapping = {}
credentials_mapping = {}
message_mapping = {}

async def generate_purchase_identifier(user_id, price, num_lessons):
    identifier_string = f"{user_id}{price}{num_lessons}"
    identifier_hash = hashlib.md5(identifier_string.encode()).hexdigest()
    return identifier_hash

async def generate_credentials_indentifier(user_id, first_name, last_name, registration_date, email, lessons_balance):
    identifier_string = f"{user_id}{first_name}{last_name}{registration_date}{email}{lessons_balance}"
    identifier_hash = hashlib.md5(identifier_string.encode()).hexdigest()
    return identifier_hash

async def generate_message_indentifier(user_id, message_text, time, id, status, processed_by_database, processed_by):
    identifier_string = f"{user_id}{message_text}{time}{id}{status}{processed_by_database}{processed_by}"
    identifier_hash = hashlib.md5(identifier_string.encode()).hexdigest()
    return identifier_hash

# class SpecialAccessMiddleware(BaseMiddleware):
#     async def on_pre_process_message(self, message: types.Message, data: dict):
#         user_id = message.from_user.id
#         if user_id == 1013673667:
#             # Add a custom flag to the message data to indicate special access
#             data['special_access'] = True
##############################################################################
##############################################################################
##############################################################################
@dp.callback_query_handler(lambda query: query.data == 'cancel_callback', state = '*')
async def cancel_callback_handler(query: types.CallbackQuery, state: FSMContext):
    # Clear the specific states for the user
    await state.reset_state()  # Pass with_data=False to only clear the state, not the stored data

    # Answer the callback query to remove the "loading" state
    await query.answer()

    # Reply with a cancellation message
    await query.message.edit_text("<b>🚫 Операцію скасовано!</b>", parse_mode="HTML")

@dp.message_handler(text="Функціонал адміністратора 💿")
async def administrator_handler(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text="<b>Функціонал адміністратора 💿</b>",
                           reply_markup=administrator_keyboard_markup(),
                           parse_mode="HTML")

@dp.message_handler(text="Назад 🔙")
async def back_handler(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text="<b>Головне меню 📃</b>",
                           reply_markup=main_reply_keyboard(),
                           parse_mode="HTML")

@dp.message_handler(text="Підтримка 💬")
async def support_handler(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text="<b>💬 FAQ</b>\n\n"
                            "<b>📩 Підтримка:\n</b>"
                            "<b>🌟 Бот запущений: xx.xx.20xx\n</b>"
                            "<b>📺 Офіційний канал:\n</b>",
                           reply_markup = support_button_markup(),
                           parse_mode="HTML")

@dp.message_handler(text="Переглянути учнів 📄")
async def students_check_handler(message: types.Message, state: FSMContext):
    students = await get_all_students()
    keyboard = InlineKeyboardMarkup(row_width=1)

    if students:
        for student in students:
            try:
                user_id = student['user_id']
                first_name = student['first_name']
                last_name = student['last_name']
                registration_date = student['registration_date']
                email = student['email']
                lessons_balance = student['lessons_balance']

                credentials_identifier = await generate_credentials_indentifier(user_id, first_name, last_name, registration_date, email, lessons_balance)
                button_text = f"{first_name} {last_name}"
                
                button_callback_data = f"credentials_{credentials_identifier}"
                
                credentials_mapping[credentials_identifier] = {
                    'user_id' : user_id,
                    'first_name' : first_name,
                    'last_name' : last_name,
                    'registration_date' : registration_date,
                    'email' : email,
                    'lessons_balance' : lessons_balance
                }

                keyboard.add(InlineKeyboardButton(text=button_text, callback_data=button_callback_data))

            except KeyError:
                print(f"Invalid student data: {student}")

        response_message = "<b>Список учнів 📄</b>"
    else:
        response_message = "<b>🙁 Список учнів пустий</b>"

    await bot.send_message(chat_id=message.chat.id, text=response_message, parse_mode="HTML", reply_markup=keyboard)

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('credentials_'))
async def students_manage_handler(callback: types.CallbackQuery, state: FSMContext):
    
    post_identifier = callback.data.split('_')[1]
    post_details = credentials_mapping.get(post_identifier)
    if post_details:
        user_id = post_details['user_id']
        first_name = post_details['first_name']
        last_name = post_details['last_name']
        registration_date = post_details['registration_date']
        email = post_details['email']
        lessons_balance = post_details['lessons_balance']
    
        message_text = STRUCTURED_MESSAGE.format(user_id=user_id, 
                                                 name=first_name + " " + last_name,
                                                 lessons_balance=lessons_balance,
                                                 registration_date=registration_date,
                                                 email=email)
    
        await bot.send_message(chat_id=callback.message.chat.id,
                           text=message_text,
                           reply_markup=administrator_reply_keyboard(user_id),
                           parse_mode="HTML")
    
    else:
        await bot.send_message(chat_id=callback.message.chat.id,
                           text="ERROR!")

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('lessons_'))
async def students_lessons_handler(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split('_')[1]
    user_id = callback.data.split('_')[2]

    teacher_id = callback.from_user.id    
    print(teacher_id)
    action_result = await change_user_lessons(user_id, choice)
    
    # Convert data to lists
    action_result_converted = [action_result.strip()]
    user_id_converted = [str(user_id).strip()]
    teacher_id_converted = [str(teacher_id).strip()]
    
    filename = os.path.join("/Users/zgutadenis/Desktop/My Projects/School_bot", "logs.csv")
    await logs_handler(action_result_converted, user_id_converted, teacher_id_converted, filename)

    # Get the message text based on user_id (assuming you have a function for this)
    message_text = await check_user_credential(user_id)
    
    # Update the message with the new text and reply keyboard
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=message_text,
                                reply_markup=administrator_reply_keyboard(user_id),
                                parse_mode="HTML")


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('student_announcement_'))
async def student_announcement_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.data.split('_')[2]

    await bot.send_message(chat_id=callback.message.chat.id,
                           text="<b>Введіть текст повідомлення:</b>",
                           reply_markup=cancel_reply_keyboard(),
                           parse_mode="HTML")
    
    await state.update_data(user_id=user_id)
    await state.set_state("student_announcement_complete")
    
@dp.message_handler(state='student_announcement_complete')
async def student_announcement_complete(message: types.Message, state: FSMContext):
    text = message.text
    
    async with state.proxy() as data:
        user_id = data.get('user_id')
        
    result = await user_message_send(user_id, text)
    
    if result is True:
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"<b>Повідомлення було доставлено успішно.\nТекст повідомлення: {text}</b>",
                               parse_mode="HTML")
    
    elif result is False:
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"<b>Повідомлення не було доставлено!\n{ERRORS['NO_EMAIL']}</b>",
                               reply_markup=administrator_telegram_message(user_id),
                               parse_mode="HTML")
        
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=ERRORS['NOT_DEFINED'],
                               parse_mode="HTML")
    
    await state.reset_state()
    
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('message_telegram_'))
async def student_announcement_telegram(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.data.split("_")[2]
    
    await bot.send_message(chat_id=callback.message.chat.id,
                           text="<b>Введіть текст повідомлення:</b>",
                           reply_markup=cancel_reply_keyboard(),
                           parse_mode="HTML")
    
    await state.update_data(user_id=user_id)
    await state.set_state("student_telegram_complete")
    
@dp.message_handler(state='student_telegram_complete')
async def student_telegram_complete(message: types.Message, state: FSMContext):
    text = message.text
    
    async with state.proxy() as data:
        user_id = data.get('user_id')
    
    if user_id:   
        await bot.send_message(chat_id=user_id,
                           text=text+"\n\nЗ повагою, English School Wuppertal.",
                           parse_mode="HTML")
        
        await bot.send_message(chat_id=message.from_user.id,
                               text="<b>Повідомлення надіслано!\nТекст: </b>" +text,
                               parse_mode="HTML")
      
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="<b>😔 Помилка! Зверніться до адміністратора бота!</b>",
                               parse_mode="HTML")
        
    await state.reset_state()
    

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message, state: FSMContext) -> None:
    last_name = message.from_user.last_name
    user_id = message.from_user.id
    print(user_id)
    await add_user_to_database(user_id)
    
    if last_name is None:
        await bot.send_message(chat_id=message.from_user.id,
                           text=f"<b>Вітаємо в боті, {message.from_user.first_name}!</b>",
                           parse_mode="HTML",
                           reply_markup=main_reply_keyboard())

    else:
        await bot.send_message(chat_id=message.from_user.id,
                           text=f"<b>Вітаємо в боті, {message.from_user.first_name} {message.from_user.last_name}!</b>",
                           parse_mode="HTML",
                           reply_markup=main_reply_keyboard())
        
    is_registred = await check_registration(user_id)
    if is_registred is None:
        await bot.send_message(chat_id=message.from_user.id,
                                text="<b>❗️ Для завершення регістрації введіть своє ім'я та прізвище!\n\n</b>"
                                    "<b>Приклад: Володимир Зеленський</b>",
                                parse_mode="HTML")
    
        await state.update_data(user_id=user_id)
        await state.set_state('registration_finish')

@dp.message_handler(state='registration_finish')
async def registration_finish(message: types.Message, state: FSMContext) -> None:
    user_name = message.text
    
    if emoji.emoji_count(user_name) > 0:
        await message.answer("❌ <b>Неправильний формат вводу!</b>\n\n"
                            "<b>Будь ласка, використовуйте формат: Ім'я Прізвище</b>",
                            parse_mode=types.ParseMode.HTML)
        await state.set_state('registration_finish')
        return
    
    name_components = user_name.split(' ')
    first_name = name_components[0]
    last_name = name_components[1] if len(name_components) > 1 else None
    #first_name, last_name = user_name.split(' ')
    
    pattern = r"^[а-яА-ЯіІїЇєЄёЁ']+[\s-][а-яА-ЯіІїЇєЄёЁ']+"

    async with state.proxy() as data:
        user_id = data.get('user_id')
    
    if user_name == "Купівля уроків 💸" or user_name == "Підтримка 💬" or user_name == "Функціонал адміністратора 💿":
        await message.answer("❌ <b>Неправильний формат вводу!</b>\n\n"
                            "<b>Будь ласка, використовуйте формат: Ім'я Прізвище</b>",
                            parse_mode=types.ParseMode.HTML)
        await state.set_state('registration_finish')
        
    elif not re.match(pattern, user_name):
        await message.answer("❌ <b>Неправильний формат вводу!</b>\n\n"
                            "<b>Будь ласка, використовуйте формат: Ім'я Прізвище</b>",
                            parse_mode=types.ParseMode.HTML)
        await state.set_state('registration_finish')
        
    else:
        await completed_registration(user_id, first_name, last_name)
        
        await bot.send_message(chat_id=message.from_user.id,
                                    text="<b>☑️ Регістрація успішно завершена!</b>",
                                    parse_mode="HTML")
    
        await state.reset_state()
##############################################################################
##############################################################################
##############################################################################
@dp.message_handler(text='Профіль 👤')
async def check_profile_handler(message: types.Message):
    user_id = message.from_user.id
    message_text = await check_user_credential(user_id)

    await bot.send_message(chat_id=message.from_user.id,
                     text=message_text,
                     reply_markup=credentials_reply_keyboard(user_id),
                     parse_mode="HTML")
    
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('email_approval_'))
async def email_approval(callback: types. CallbackQuery, state: FSMContext):
    user_id = callback.message.chat.id
    check_email = await get_mail(user_id)
    
    if not check_email:
        await bot.send_message(callback.message.chat.id,
                            text='<b>📩 Будь ласка, введіть свою електронну адресу!</b>',
                            parse_mode='HTML')
        await state.set_state('input_email')
    else:
        await bot.send_message(callback.message.chat.id,
                            text='<b>Ваша електронна адреса уже підтверджена, бажаєте змінити?</b>',
                            reply_markup=change_email_keyboard(),
                            parse_mode='HTML')
        
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'change_email')
async def change_email(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.message.chat.id,
                           text='<b>📩 Будь ласка, введіть свою нову електронну адресу!</b>',
                           parse_mode='HTML')
    await state.set_state('input_email')    
    
@dp.message_handler(state="input_email")
async def input_name(message: types.Message, state: FSMContext):
    email = message.text
    user_id = message.from_user.id
    #Just regex in
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(regex, email):
        await bot.send_message(chat_id=message.from_user.id,
                              text="<b>🙁 Вибачте, електронна пошта недійсна!</b>\n\n<b>🔍 Перевірте правильність введення!</b>",
                              parse_mode="HTML")
        await state.reset_state()
        return
    
    await state.update_data(email=email, user_id = user_id)
    
    confirmation_code = await generate_confirmation_code()
    await send_email(email, confirmation_code)
    await state.update_data(confirmation_code=confirmation_code)
    
    await bot.send_message(chat_id=message.from_user.id,                  
                           text=EMAIL_NOTIFY,
                           reply_markup=cancel_reply_keyboard(),
                           parse_mode="HTML")
    
    await state.set_state('confirmation_code_proof')

@dp.message_handler(state="confirmation_code_proof")
async def confirm_code(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        email = data.get('email')
        confirmation_code = data.get('confirmation_code')
        user_id = data.get('user_id')
        
        print(user_id)
        print(confirmation_code)
        
    if message.text != confirmation_code:
        await bot.send_message(chat_id=message.from_user.id,
                               text="<b>🙁 Вибачте, <em>код підтвердження</em> недійсний!</b>\n\n<b>🔍Перевірте правильність введення!</b>",
                               parse_mode="HTML")
        await state.reset_state()
    
    else:
        result = await add_email(user_id, email)
        if isinstance(result, str):
            # If the result is a string, it means there was an error
            await bot.send_message(chat_id=message.from_user.id, text=result, parse_mode="HTML")
        else:
            # Email added successfully
            await bot.send_message(chat_id=message.from_user.id,
                                   text="<b>☑️ Електронну адресу успішно додано!</b>",
                                   parse_mode="HTML")

        await state.reset_state()
        
        
##############################################################################
##############################################################################
##############################################################################
@dp.message_handler(text='Купівля уроків 💸')
async def lesson_purchase_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    is_registered = await check_registration_additional(user_id)
    
    if not is_registered:
        await bot.send_message(chat_id=message.from_user.id,
                                text="<b>😔 Помилка! Зверніться до адміністратора бота!</b>",
                                parse_mode="HTML")

    else:
        courses = await get_course_offers()
        lessons_balance = await check_lessons_balance(user_id)
        
        if lessons_balance > 0:
            await bot.send_message(chat_id=message.from_user.id,
                                text=f"<b>😔 Ви не можете купити курс, оскільки на вашому балансі ще {lessons_balance} уроки(-iв)</b>",
                                parse_mode="HTML")
            return
        
        else:
            if courses is not None:
                for course in courses:
                    price = str(course['price'])
                    description = course['description']
                    num_lessons = course['num_lessons']
                    
                    course_message = f"<b>Course Offer</b>\n\n" \
                        f"<b>Ціна:</b> ${price}\n" \
                        f"<b>Опис:</b> {description}\n" \
                        f"<b>Кількість занять:</b> {num_lessons}\n"

                    post_identifier = await generate_purchase_identifier(user_id, price, num_lessons)

                    post_mapping[post_identifier] = {
                        'user_id' : user_id,
                        'price' : price,
                        'num_lessons' : num_lessons
                    }
                    
                    await bot.send_message(chat_id=message.from_user.id,
                                    text=course_message,
                                    reply_markup = lessons_payment_method(post_identifier),
                                    parse_mode="HTML")
                    
                    await asyncio.sleep(1)
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text="<b>🙁 Доступних курсів не знайдено</b>",
                                    parse_mode="HTML")

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('telegram_payment_'))
async def lessons_purchase_telegram(callback: types.CallbackQuery, state: FSMContext):
    post_identifier = callback.data.split('_')[2]
    
    post_details = post_mapping.get(post_identifier)
    
    if post_details:
        user_id = post_details['user_id']
        price = post_details['price']
        num_lessons = post_details['num_lessons']

        amount = int(float(price) * 100)        
        
        object_price = [LabeledPrice(label='English Course', amount=amount)]

        lessons_balance = await check_lessons_balance(user_id)

        if user_id and price and num_lessons:
            if lessons_balance > 0:
                await bot.send_message(chat_id=callback.message.chat.id,
                               text=f"<b>😔 Ви не можете купити курс, оскільки на вашому балансі ще {lessons_balance} уроки(-iв)</b>",
                               parse_mode="HTML")
                return
    
            else:
                
                await state.update_data(user_id=user_id, price=price, num_lessons=num_lessons)

                await bot.send_invoice(chat_id=callback.message.chat.id,
                                    title="Курс англійської",
                                    description="None",
                                    provider_token=PAYMENT_API,
                                    currency='UAH',
                                    need_email=True,
                                    need_phone_number=True,
                                    is_flexible=False,
                                    prices=object_price,
                                    start_parameter='English',
                                    payload='test_invoice')
        
        
@dp.pre_checkout_query_handler(lambda q: True)
async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, state: FSMContext):
    
    async with state.proxy() as data:
        user_id = data.get('user_id')
        price = data.get('price')
        num_lessons = data.get('num_lessons')
    
    email = await get_mail(user_id)
    await add_lessons(user_id, num_lessons)
    await payment_announcement(price, num_lessons, email)
    
    amount_uah = message.successful_payment.total_amount // 100  # Convert total_amount from kopiykas to hryvnias
    await bot.send_message(chat_id=message.chat.id,
                           text=f"<b>✅ Платіж на суму {amount_uah}UAH успішно здійснено!\n\nПідтвердження оплати відправлено на вашу електронну скриньку</b>",
                           parse_mode="HTML")

##############################################################################
##############################################################################
##############################################################################
@dp.message_handler(text="Повідомити про проблему 📩")
async def support_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    await bot.send_message(chat_id=message.from_user.id,
                           text="<b>Введіть текст проблеми:</b>",
                           parse_mode="HTML",
                           reply_markup=cancel_reply_keyboard())
    
    await state.update_data(user_id=user_id)
    await state.set_state("support_complete_handler")

@dp.message_handler(state="support_complete_handler")
async def support_complete_handler(message: types.Message, state: FSMContext):
    text = message.text
    
    async with state.proxy() as data:
        user_id = data.get('user_id')
        
    result = await support_message_writer(user_id, text)
    
    if result:
        await bot.send_message(chat_id=message.from_user.id,
                               text=result,
                               parse_mode="HTML")
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=result,
                               parse_mode="HTML")
             
    await state.reset_state()

@dp.message_handler(text=["Повідомлення підтримки 📩", "Архів 🗑"])
async def support_check_handler(message: types.Message):
    text_trigger = message.text
    messages_information = await get_all_message_support()
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    if messages_information:
        for message_information in messages_information:
            processed = message_information['processed']
            if (text_trigger == "Повідомлення підтримки 📩" and processed == 0) or (text_trigger == "Архів 🗑" and processed == 1):
                try:
                    user_id = message_information['user_id']
                    message_text = message_information['message']
                    time = message_information['time']
                    id = message_information['id']
                    status = message_information['processed']
                    processed_by_database = message_information['processed_by_id']
                    processed_by = message.from_user.id
                    message_indentifier = await generate_message_indentifier(user_id, message_text, time, id, status, processed_by_database, processed_by)
                    button_text = f"{id}-{time}"
                    
                    button_callback_data = f"support_{message_indentifier}"
                    
                    message_mapping[message_indentifier] = {
                        'user_id' : user_id,
                        'message_text' : message_text,
                        'time' : time,
                        'id' : id,
                        'status' : status,
                        'processed_by' : processed_by,
                        'processed_by_database' : processed_by_database
                    }

                    keyboard.add(InlineKeyboardButton(text=button_text, callback_data=button_callback_data))
        
                except KeyError:
                    print(f"ПОМИЛКА! {ERRORS['NOT_DEFINED']}")
            
            response_message = "<b>Список запитів 📄</b>"
    else:
        response_message = "<b>🙁 Список запитів пустий</b>"

    await bot.send_message(chat_id=message.chat.id, text=response_message, parse_mode="HTML", reply_markup=keyboard)

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('support_'))
async def students_manage_handler(callback: types.CallbackQuery):
    message_indentifier = callback.data.split('_')[1]
    message_details = message_mapping.get(message_indentifier)
    conn = await connect_to_db()
    task_fsm = TaskFSM(conn)
    
    if message_details:
        user_id = message_details['user_id']
        message_text = message_details['message_text']
        time = message_details['time']
        id = message_details['id']
        status = message_details['status']
        processed_by = message_details['processed_by']
        
        check_available = await get_referrers_ids_from_user_id(processed_by)
        print(check_available)
        if len(check_available) > 0:
            await bot.send_message(chat_id=callback.message.chat.id,
                                   text="<b>Ви не завершили попередній емейл!</b>",
                                   parse_mode="HTML")
            return
        
        await add_processedor(id, processed_by)
        updated_data = await check_processedor(id)
     
        if updated_data != callback.from_user.id:
            await bot.send_message(chat_id=callback.message.chat.id,
                                   text="<b>Цей емейл вже обробляється іншим користувачем!</b>",
                                   parse_mode="HTML")
            return
        
        if task_fsm.process_input("start"):
            await task_fsm.update_state_in_db(id)

        
        processed_dict = {'0':'Не опрацьовано ❌', '1':'Опрацьовано ✅'}
        status_converted = processed_dict.get(str(status), '')
        
        await bot.send_message(chat_id=callback.message.chat.id,
                           text=STRUCTURED_MESSAGE_SUPPORT.format(user_id=user_id, id=id, time=time, message_text=message_text, processed=status_converted),
                           reply_markup=support_keyboard_markup(user_id, id),
                           parse_mode="HTML")
        
    else:
        await bot.send_message(chat_id=callback.message.chat.id,
                           text=f"{ERRORS['NOT_DEFINED']}",
                           parse_mode="HTML")
        
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('answer_'))
async def support_process_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.data.split('_')[1]
    message_id = callback.data.split('_')[2]
    
    await bot.send_message(chat_id=callback.message.chat.id,
                     text="<b>Введіть текст відоповіді:</b>",
                     reply_markup=cancel_reply_keyboard(),
                     parse_mode="HTML")
    
    await state.update_data(user_id=user_id, message_id=message_id)
    await state.set_state('support_answear_finish')
    

@dp.message_handler(state="support_answear_finish")
async def support_answear_finish(message: types.Message, state: FSMContext):
    text = message.text
    conn = await connect_to_db()
    task_fsm = TaskFSM(conn)
    
    async with state.proxy() as data:
        user_id = data.get('user_id')
        message_id = data.get('message_id')
        
    await bot.send_message(chat_id=user_id,
                           text=text+"\n\nЗ повагою, English School Wuppertal.",
                           parse_mode="HTML")
    
    result = await processed_message(user_id, message_id)
    
    if result:
        await bot.send_message(chat_id=message.from_user.id,
                               text="<b>✅ Повідомлення опрацьовано!</b>",
                               parse_mode="HTML")
        
        await task_fsm.load_state_from_db(message_id)
        
        if task_fsm.process_input("complete"):
            await task_fsm.update_state_in_db(message_id)
    
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"<b>❌ Помилка! {ERRORS['NOT_DEFINED']}</b>",
                               parse_mode="HTML")
        
        await task_fsm.load_state_from_db(message_id)
        
        if task_fsm.process_input("reject"):
            await task_fsm.update_state_in_db(message_id)
        
    
    await state.reset_state()

if __name__ == '__main__':
    #dp.middleware.setup(CheckSubscriptionUserMiddleware())
    executor.start_polling(dp, 
                           skip_updates=True)    
