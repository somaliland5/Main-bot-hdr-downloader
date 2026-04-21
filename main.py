import telebot
import json
import requests
import os
from telebot.types import ReplyKeyboardMarkup
from runner import run_all_bots

TOKEN = os.getenv("MAIN_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

def load_db():
    with open("database.json", "r") as f:
        return json.load(f)

def save_db(data):
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)

# START
@bot.message_handler(commands=['start'])
def start(msg):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Add Bot", "📦 My Bots")

    if msg.from_user.id == ADMIN_ID:
        kb.add("📢 Broadcast All")

    bot.send_message(msg.chat.id, "Welcome to Bot Creator", reply_markup=kb)

# ADD BOT
@bot.message_handler(func=lambda m: m.text == "➕ Add Bot")
def add_bot(msg):
    bot.send_message(msg.chat.id, "Send your bot token")
    bot.register_next_step_handler(msg, save_token)

def save_token(msg):
    token = msg.text.strip()

    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()
        if not r["ok"]:
            bot.send_message(msg.chat.id, "Invalid token ❌")
            return
    except:
        bot.send_message(msg.chat.id, "Error checking token")
        return

    db = load_db()

    db["bots"].append({
        "token": token,
        "owner": msg.from_user.id,
        "status": "active"
    })

    save_db(db)

    bot.send_message(msg.chat.id, "Bot added and started ✅")

# MY BOTS
@bot.message_handler(func=lambda m: m.text == "📦 My Bots")
def mybots(msg):
    db = load_db()
    text = ""

    for b in db["bots"]:
        if b["owner"] == msg.from_user.id:
            text += f"{b['token'][:10]}... | {b['status']}\n"

    if not text:
        text = "No bots"

    bot.send_message(msg.chat.id, text)

# BROADCAST ALL
@bot.message_handler(func=lambda m: m.text == "📢 Broadcast All")
def bc(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    bot.send_message(msg.chat.id, "Send message")
    bot.register_next_step_handler(msg, send_all)

def send_all(msg):
    db = load_db()

    for b in db["bots"]:
        try:
            tb = telebot.TeleBot(b["token"])
            tb.send_message(b["owner"], msg.text)
        except:
            pass

    bot.send_message(msg.chat.id, "Done ✅")

# RUN ALL SUB BOTS
run_all_bots()

bot.infinity_polling()
