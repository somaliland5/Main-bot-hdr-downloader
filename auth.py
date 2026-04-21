import random
import time

OTP = {}

def send_otp(bot, chat_id, user_id):
    code = str(random.randint(1000, 9999))

    OTP[user_id] = code

    bot.send_message(chat_id, f"🔐 Code: {code}")

def verify_otp(user_id, code):
    return OTP.get(user_id) == code
