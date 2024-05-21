#Configuration file for School-Bot

#Copyright (c) 2023-2024 Morkovka


#BOT_API - Token for your bot, which you can get from @BotFather in Telegram by creating your bot.
#PAYMENT_API - Token, which you can get from your desired payment-system by creating a new project. To connect payment to your bot, you can use @BotFather in Telegram.
#DB_HOST, DB_USER, DB_NAME, DB_PASSWORD - Credentials for your Database, where all the info. is stored.
#SENDER_EMAIL - Your email adress, where SMTP-server is installed for automatical emails sending. Can be made by Gmail
#APP_PASSWORD - passport for your SMTP, when you create a new project with your email.

#6211134929:AAG-ibhGQQadmpRiK4EN9JZJSlVfL1w5FEM
BOT_API = "5774172002:AAGOI-bw9II74cSzCKjK3hSzUdRcVaSuTFE"
PAYMENT_API = "410694247:TEST:462ddd90-a902-4812-872a-6ead8b64b41c"
DB_HOST = "localhost"
DB_USER = "root"
DB_NAME = "telegram_school"
DB_PASSWORD = "root1234"
SENDER_EMAIL = "stonehaven.reset@gmail.com"
APP_PASSWORD = "lfemarbsgejrcfmq"

EMAIL_NOTIFY = """
<b>📩 Будь ласка, перевірте вашу електронну пошту та знайдіть повідомлення від нас. У ньому буде код, який вам потрібно ввести в цьому чаті.\n</b>
<b>⚠️ Зверніть увагу, що повідомлення може потрапити до папки "спам". Будь ласка, перевірте цю папку, якщо ви не можете знайти наш лист в основній папці вхідних повідомлень.</b>
"""

STRUCTURED_MESSAGE = """
    <b>👤 Профіль учня</b>

    <b>🆔 ID: {user_id}</b>
    <b>👀 Ім'я: {name}</b>
    <b>🎒 Баланс уроків: {lessons_balance}</b>
    <b>📆 Дата регістрації: {registration_date}</b>
    <b>📧 Email: {email}</b>
        """

STRUCTURED_MESSAGE_SUPPORT = """
    <b>👤 Повідомлення підтримки</b>
    
    <b>🆔 ID: {user_id}</b>
    <b>👀 ID-проблеми: {id}</b>
    <b>📆 Чаc звернення: {time}</b>
    <b>📧 Проблема: {message_text}</b>
    
    <b>🔗 СТАТУС: {processed}</b>

"""
ERRORS = {
    'NO_EMAIL':'<b>😔 Користувач не додав електронну скриньку!</b>',
    'NOT_DEFINED':'<b>😔 Невідома помилка, зверніться до адміністратора боту!</b>',
    'NOT_REGISTERED':'<b>😔 Помилка (мабудь ви не зареєстровані)! Зверніться до адміністратора бота!</b>'
}
