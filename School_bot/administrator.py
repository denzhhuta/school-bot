import aiomysql
from datetime import datetime
from configuration import DB_HOST, DB_USER, DB_NAME, DB_PASSWORD, ERRORS
from email_sender import user_announcement
import csv 
import os
from datetime import datetime

import aiomysql

class TaskFSM:
    def __init__(self, conn):
        self.state = "To Do"
        self.transitions = {
            "To Do": {"start": "In Progress"},
            "In Progress": {"complete": "Completed", "reject": "To Do"},
            "Completed": {}
        }
        self.conn = conn  # Store the database connection in the class instance

    async def load_state_from_db(self, message_id):
        try:
            async with self.conn.cursor() as cursor:
                # Replace 'states_table' with the actual name of the table where states are stored in the database
                query = f"SELECT states FROM technical_support_messages WHERE id = {message_id}"
                await cursor.execute(query)
                result = await cursor.fetchone()
                if result:
                    self.state = result['states']
                else:
                    print(f"State for message_id {message_id} not found in the database.")
        except Exception as ex:
            print(f"Error loading state for message_id {message_id} from the database.")
            print(ex)

    async def update_state_in_db(self, message_id):
        try:
            async with self.conn.cursor() as cursor:
                # Replace 'states_table' with the actual name of the table where states are stored in the database
                query = f"UPDATE technical_support_messages SET states = '{self.state}' WHERE id = {message_id}"
                await cursor.execute(query)
                await self.conn.commit()
        except Exception as ex:
            print(f"Error updating state for message_id {message_id} in the database.")
            print(ex)

    def process_input(self, action):
        next_state = self.transitions[self.state].get(action)
        if next_state:
            self.state = next_state
            return True
        return False

    def start_task(self):
        return self.process_input("start")

    def complete_task(self):
        return self.process_input("complete")

    def reject_task(self):
        return self.process_input("reject")

        
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
        message_text = "Проблеми з підключенням до бази даних, зверніться до системного адміністратора!"
        return message_text
    
def number_validator(func):
    async def wrapper(*args, **kwargs):
        user_id = args[0]
        choice = args[1]
        
        conn = await connect_to_db()
        async with conn.cursor() as cursor:
            select_query = "SELECT lessons_balance FROM users WHERE user_id = %s"
            await cursor.execute(select_query, (user_id,))
            lessons_balance = await cursor.fetchone()
        
        if choice == "substract" and (lessons_balance is None or lessons_balance[0] <= 0):
            print("Lessons balance is already at the minimum. Cannot subtract.")
            raise Exception("Lessons balance is already at the minimum. Cannot subtract.")
        
        await func(*args, **kwargs)
        conn.close()
    
    return wrapper


async def change_user_lessons(user_id: int, choice):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        if choice == "substract":
            action = "subtracted"
            update_query = "UPDATE users SET lessons_balance = lessons_balance - 1 WHERE user_id = %s"
        elif choice == "add":
            action = "added"
            update_query = "UPDATE users SET lessons_balance = lessons_balance + 1 WHERE user_id = %s"
            
        await cursor.execute(update_query, (user_id,))
        await conn.commit()

    conn.close()
    
    return action
    
async def get_all_students():
    try:
        conn = await connect_to_db()
        async with conn.cursor() as cursor:
            select_query = "SELECT * FROM users"
            await cursor.execute(select_query)
            result = await cursor.fetchall()

        conn.close()
        
        return result 
    
    except Exception as ex:
        print("Error occurred while fetching bookings from the database:")
        print(ex)
        return []
    
async def user_message_send(user_id, text):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        select_query = "SELECT email FROM users WHERE user_id = %s"
        await cursor.execute(select_query, (user_id,))
        result = await cursor.fetchone()
    
    if result['email'] is not None:
        await user_announcement(result['email'], text)
        return True
    else:
        return False
    
async def support_message_writer(user_id, message_text):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        select_query = "SELECT user_id FROM users WHERE user_id = %s"
        await cursor.execute(select_query, (user_id, ))
        result = await cursor.fetchone()
        
        if result:
            insert_query = "INSERT INTO technical_support_messages (user_id, message) VALUES (%s, %s)"
            await cursor.execute(insert_query, (user_id, message_text))
            await conn.commit()
            return "<b>✅ Повідомлення надіслано до підтримки</b>"
    
        else:
            return ERRORS['NOT_REGISTERED']
        
async def get_all_message_support():
    try:
        conn = await connect_to_db()
        async with conn.cursor() as cursor:
            select_query = "SELECT * FROM technical_support_messages"
            await cursor.execute(select_query)
            result = await cursor.fetchall()

        conn.close()
        
        return result 
    
    except Exception as ex:
        print("Error occurred while fetching bookings from the database:")
        print(ex)
        return []       
    
async def processed_message(user_id, message_id):
    try:
        conn = await connect_to_db()
        async with conn.cursor() as cursor:
            insert_query = "UPDATE technical_support_messages SET processed = 1 WHERE id = %s"
            await cursor.execute(insert_query, (message_id,))
            await conn.commit()
        
        return True
            
    except Exception as ex:
        print("Error occurred while fetching bookings from the database:")
        print(ex)
        
        return False

async def add_processedor(id, processed_by):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        if id and processed_by:
            select_query = "SELECT processed_by_id FROM technical_support_messages WHERE id=%s"
            await cursor.execute(select_query, (id,))
            result = await cursor.fetchone()
            
            if result['processed_by_id'] is None:
                insert_query = "UPDATE technical_support_messages SET processed_by_id = %s WHERE id = %s"
                await cursor.execute(insert_query, (processed_by, id))
                await conn.commit()

                # select_query_2 = "SELECT processed_by_id FROM technical_support_messages WHERE id = %s"
                # await cursor.execute(select_query_2, (id, ))
                # updated_data = await cursor.fetchone()
                
                # return updated_data['processed_by_id']
            
        else:
            return None
        
    conn.close() 


async def check_processedor(id):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        if id:
            select_query = "SELECT processed_by_id FROM technical_support_messages WHERE id = %s"
            await cursor.execute(select_query, (id, ))
            updated_data = await cursor.fetchone()
                
            return updated_data['processed_by_id']
            
        else:
            return None
        
    conn.close() 


async def get_referrers_ids_from_user_id(processed_by):
    conn = await connect_to_db()
    async with conn.cursor() as cursor:
        select_query = """
        SELECT id
        FROM technical_support_messages
        WHERE processed_by_id = %s AND states = 'In Progress'
        """
        await cursor.execute(select_query, (processed_by))
        results = await cursor.fetchall()

    conn.close()
    
    referrer_ids = [result['id'] for result in results]
    return referrer_ids


async def logs_handler(action_result_converted, user_id_converted, teacher_id_converted, filename):
    try:
        with open(filename, 'a+', newline='') as file:
            if file.tell() == 0:  # Check if the file is empty
                writer = csv.writer(file)
                writer.writerow(['UserID', 'TeacherID', 'Action', 'Time'])
            file.seek(0, os.SEEK_END)  # Move the file pointer to the end
            writer = csv.writer(file)
            action_time = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            writer.writerows(zip(user_id_converted, teacher_id_converted, action_result_converted, action_time))
        print(f"Successfully appended emails and IBANs to CSV file: {filename}")
    except Exception as e:
        print(f"Error appending emails and IBANs to CSV file: {filename}\n{e}")
    
    