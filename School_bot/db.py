import aiomysql
import asyncio
from datetime import datetime
from configuration import DB_HOST, DB_USER, DB_NAME, DB_PASSWORD
#import json


async def connect_to_db():
    try:
        conn = await aiomysql.connect(
            host=DB_HOST,
            port=3306,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            cursorclass=aiomysql.DictCursor)
    
        print("Connected successfully...")
        return conn
     
    except Exception as ex:
        print("Connection to DataBase refused...")
        print(ex)

async def check_registration_additional(user_id: int):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        select_query = "SELECT * FROM users WHERE user_id = %s"
        await cursor.execute(select_query, (user_id,))
        result = await cursor.fetchone()
        
        if result is None:
            return False
        else:
            return True

async def add_user_to_database(user_id: int):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        select_query = "SELECT user_id FROM users WHERE user_id = %s"
        await cursor.execute(select_query, (user_id,))
        result = await cursor.fetchone()
        
        if result is None:
            registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            insert_query = "INSERT INTO users (user_id, registration_date) VALUES (%s, %s)"
            await cursor.execute(insert_query, (user_id, registration_date))
            await conn.commit()
        
        else:
            pass
            print("Already in DB")

    conn.close()
    
async def check_registration(user_id):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        select_query = "SELECT first_name, last_name FROM users WHERE user_id = %s"
        await cursor.execute(select_query, (user_id,))
        result = await cursor.fetchone()
        print(result)
        
    if result['first_name'] is None and result['last_name'] is None:
        return None
    else:
        return True

async def completed_registration(user_id, first_name, last_name):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        select_query = "SELECT first_name, last_name FROM users WHERE user_id = %s"
        await cursor.execute(select_query, (user_id,))
        result = await cursor.fetchone()
        
        if result['first_name'] is None and result['last_name'] is None:
            update_query = "UPDATE users SET first_name = %s, last_name = %s WHERE user_id = %s"
            await cursor.execute(update_query, (first_name, last_name, user_id))
            await conn.commit()

        else:
            return None
        
async def check_user_credential(user_id: int):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        select_query = "SELECT * FROM users WHERE user_id = %s"
        await cursor.execute(select_query, (user_id, ))
        result = await cursor.fetchone()

    conn.close()

    STRUCTURED_MESSAGE = """
    <b>👤 Ваш профіль</b>

    <b>🆔 ID: {user_id}</b>
    <b>👀 Ім'я: {name}</b>
    <b>🎒 Баланс уроків: {lessons_balance}</b>
    <b>📆 Дата регістрації: {registration_date}</b>
    <b>📧 Email: {email}</b>
        """

    if result:
        registration_date = result['registration_date'].date()  # Extracting only the date
        email = result['email']
        email_display = email if email else "😔 Не підтверджено"
        first_name = result['first_name'] or ""  
        last_name = result['last_name'] or ""
        lessons_balance = result['lessons_balance']
        name = f"{first_name} {last_name}"

        message_text = STRUCTURED_MESSAGE.format(
            user_id=result['user_id'],
            registration_date=registration_date,
            name=name,
            lessons_balance = lessons_balance,
            email = email_display
        )
        return message_text

    else:
        return '<b>😔 Помилка! Зверніться до адміністратора бота!</b>'

async def get_course_offers():
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        select_query = "SELECT * FROM english_courses"
        await cursor.execute(select_query)
        results = await cursor.fetchall()
        
    conn.close()

    if results:
        return results
    else:
        return None

async def get_mail(user_id):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        select_query = "SELECT email FROM users WHERE user_id = %s"
        await cursor.execute(select_query, (user_id,))
        result = await cursor.fetchone()
        print(result)
    conn.close()

    if result and result['email']:
        return result['email']
    else:
        return None


async def add_email(user_id, email):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        select_query = "SELECT email from users WHERE email = %s"
        await cursor.execute(select_query, (email))
        result = cursor.fetchall()

        if result:
            return "<b>😔 Ця електронна скринька вже виростовується!</b>"
            
        else:
            if user_id and email:
                update_query = "UPDATE users SET email = %s WHERE user_id = %s"
                await cursor.execute(update_query, (email, user_id))
                await conn.commit()
            
    conn.close()
    
async def add_lessons(user_id, num_lessons):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        if user_id and num_lessons:
            update_query = "UPDATE users SET lessons_balance = %s WHERE user_id = %s"
            await cursor.execute(update_query, (num_lessons, user_id))
            await conn.commit()
            
        else:
            return None
        
    conn.close()

async def check_lessons_balance(user_id):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        if user_id:
            select_query = "SELECT lessons_balance FROM users WHERE user_id = %s"
            await cursor.execute(select_query, (user_id,))
            result = await cursor.fetchone()
    conn.close()

    if result is not None and result['lessons_balance']:
        return result['lessons_balance']
    else:
        return 0  # Return 0 or any other default value if the result is None or lessons_balance is not set
