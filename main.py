import telebot
import json
import requests
import os
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from runner import run_all_bots, start_bot, stop_bot

# ===== ENV =====
TOKEN = os.getenv("MAIN_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

# ===== DATABASE =====
def load_db():
    if not os.path.exists("database.json"):
        return {"bots": []}
    with open("database.json", "r") as f:
        return json.load(f)

def save_db(data):
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Add Bot", "📦 My Bots")

    if msg.from_user.id == ADMIN_ID:
        kb.add("📢 Broadcast All")

    bot.send_message(
        msg.chat.id,
        "Welcome to Bot Creator\n\nCreate your own TikTok & Instagram Downloader Bot.",
        reply_markup=kb
    )

# ===== ADD BOT =====
@bot.message_handler(func=lambda m: m.text == "➕ Add Bot")
def add_bot(msg):
    bot.send_message(msg.chat.id, "Send your bot token")
    bot.register_next_step_handler(msg, process_token)

def process_token(msg):
    token = msg.text.strip()

    # CHECK TOKEN
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()
        if not r["ok"]:
            bot.send_message(msg.chat.id, "Invalid token ❌")
            return
    except:
        bot.send_message(msg.chat.id, "Error checking token")
        return

    db = load_db()

    # PREVENT DUPLICATE
    for b in db["bots"]:
        if b["token"] == token:
            bot.send_message(msg.chat.id, "Bot already added")
            return

    bot_info = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()["result"]

    db["bots"].append({
        "token": token,
        "owner": msg.from_user.id,
        "username": bot_info.get("username", "unknown"),
        "status": "active"
    })

    save_db(db)

    # START BOT
    start_bot({
        "token": token,
        "owner": msg.from_user.id
    })

    bot.send_message(msg.chat.id, f"Bot @{bot_info.get('username')} added & started ✅")

# ===== MY BOTS =====
@bot.message_handler(func=lambda m: m.text == "📦 My Bots")
def mybots(msg):
    db = load_db()
    found = False

    for b in db["bots"]:
        if b["owner"] == msg.from_user.id:
            found = True

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("🟢 Open", callback_data=f"open|{b['token']}"),
                InlineKeyboardButton("🔴 Stop", callback_data=f"stop|{b['token']}")
            )
            markup.add(
                InlineKeyboardButton("❌ Delete", callback_data=f"del|{b['token']}")
            )

            bot.send_message(
                msg.chat.id,
                f"@{b['username']}\nStatus: {b['status']}",
                reply_markup=markup
            )

    if not found:
        bot.send_message(msg.chat.id, "You have no bots")

# ===== CALLBACKS =====
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    action, token = call.data.split("|")
    db = load_db()

    for b in db["bots"]:
        if b["token"] == token:

            if action == "stop":
                b["status"] = "stopped"
                stop_bot(token)

            elif action == "open":
                b["status"] = "active"
                start_bot(b)

            elif action == "del":
                db["bots"].remove(b)

            save_db(db)
            bot.answer_callback_query(call.id, "Done ✅")
            return

# ===== BROADCAST ALL =====
@bot.message_handler(func=lambda m: m.text == "📢 Broadcast All")
def broadcast_all(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    bot.send_message(msg.chat.id, "Send message / photo / video")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(msg):
    db = load_db()

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Join Channel", url="https://t.me/Create_Our_own_bot")
    )

    for b in db["bots"]:
        try:
            tb = telebot.TeleBot(b["token"])

            if msg.content_type == "text":
                tb.send_message(b["owner"], msg.text, reply_markup=markup)

            elif msg.content_type == "photo":
                tb.send_photo(
                    b["owner"],
                    msg.photo[-1].file_id,
                    caption=msg.caption or "",
                    reply_markup=markup
                )

            elif msg.content_type == "video":
                tb.send_video(
                    b["owner"],
                    msg.video.file_id,
                    caption=msg.caption or "",
                    reply_markup=markup
                )

        except:
            pass

    bot.send_message(msg.chat.id, "Broadcast sent ✅")

# ===== RUN ALL BOTS =====
run_all_bots()

print("Main bot running...")
bot.infinity_polling()
