import asyncio
from configuration import SENDER_EMAIL, APP_PASSWORD
from email.message import EmailMessage
from aiosmtplib import SMTP
import string
import random
from datetime import datetime

#async def send_email(email: str):

async def generate_confirmation_code() -> str:
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

async def send_email(email: str, confirmation_code: str):
    html = f'''
        <html>
        <head>
        <style>
            .container {{
            max-width: 500px;
            margin: 0 auto;
            background-color: #f1f1f1;
            border-radius: 10px;
            padding: 20px;
            }}

            .confirmation-code {{
            background-color: #4CAF50;
            color: #ffffff;
            font-weight: bold;
            font-size: 30px;
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            }}

            @media only screen and (max-width: 600px) {{
            .container {{
                max-width: 100%;
            }}
            }}
        </style>
        </head>
        <body>
        <div class="container">
            <div class="confirmation-code">{confirmation_code}</div>
            <p>Ваш код підтвердження</p>
            <p>З повагою, команда English School Wuppertal.</p>
        </div>
        </body>
        </html>
        '''
    msg = EmailMessage()
    msg['Subject'] = 'Enlish School Wuppertal | Підтвердження електронної скриньки'
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg.set_content(html, subtype='html')
    
    async with SMTP(hostname='smtp.gmail.com', port=587, start_tls=True,
                    username=SENDER_EMAIL, password=APP_PASSWORD) as smtp:
        await smtp.send_message(msg)
        
async def payment_announcement(price, num_lessons, email):
    purchase_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html = f'''
    <html>
    <head>
    <style>
        .container {{
        max-width: 500px;
        margin: 0 auto;
        background-color: #f1f1f1;
        border-radius: 10px;
        padding: 20px;
        }}

        .purchase-details {{
        font-size: 16px;
        margin-bottom: 10px;
        color: #000000; /* Black */
        }}

        .confirmation-code {{
        background-color: #4CAF50;
        color: #ffffff;
        font-weight: bold;
        font-size: 30px;
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        }}

        .purchase-message {{
        font-size: 16px;
        margin-top: 20px;
        }}

        .signature {{
        font-size: 14px;
        margin-top: 20px;
        text-align: center;
        }}

        @media only screen and (max-width: 600px) {{
        .container {{
            max-width: 100%;
        }}
        }}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="confirmation-code">Підтвердження покупки</div>
        <p class="purchase-details">Дата покупки: {purchase_time}</p>
        <p class="purchase-details">Кількість уроків: {num_lessons}</p>
        <p class="purchase-details">Ціна: {price}UAH</p>
        <p class="signature">З найкращими побажаннями,<br>English School Wuppertal Team</p>
    </div>
    </body>
    </html>
    '''

    msg = EmailMessage()
    msg['Subject'] = 'English School Wuppertal | Підтвердження покупки'
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg.set_content(html, subtype='html')

    async with SMTP(hostname='smtp.gmail.com', port=587, start_tls=True,
                    username=SENDER_EMAIL, password=APP_PASSWORD) as smtp:
        await smtp.send_message(msg)
        

async def user_announcement(email: str, text: str):
    html = f'''
        <html>
        <head>
        <style>
            .container {{
            max-width: 500px;
            margin: 0 auto;
            background-color: #f1f1f1;
            border-radius: 10px;
            padding: 20px;
            }}

            .confirmation-code {{
            background-color: #4CAF50;
            color: #ffffff;
            font-weight: bold;
            font-size: 30px;
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            }}

            @media only screen and (max-width: 600px) {{
            .container {{
                max-width: 100%;
            }}
            }}
        </style>
        </head>
        <body>
        <div class="container">
            <div class="confirmation-code">{text}</div>
            <p>З повагою, команда English School Wuppertal.</p>
        </div>
        </body>
        </html>
        '''
    msg = EmailMessage()
    msg['Subject'] = 'Enlish School Wuppertal | Оповіщення!'
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg.set_content(html, subtype='html')
    
    async with SMTP(hostname='smtp.gmail.com', port=587, start_tls=True,
                    username=SENDER_EMAIL, password=APP_PASSWORD) as smtp:
        await smtp.send_message(msg)