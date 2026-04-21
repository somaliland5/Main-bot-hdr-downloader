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
        return {"bots": [], "channels": []}
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
        kb.add("➕ Add Channel", "📋 Channels")
        kb.add("❌ Delete All Channels")

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

    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()
        if not r["ok"]:
            bot.send_message(msg.chat.id, "Invalid token ❌")
            return
    except:
        bot.send_message(msg.chat.id, "Error checking token")
        return

    db = load_db()

    for b in db["bots"]:
        if b["token"] == token:
            bot.send_message(msg.chat.id, "Bot already added")
            return

    info = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()["result"]

    db["bots"].append({
        "token": token,
        "owner": msg.from_user.id,
        "username": info.get("username", "unknown"),
        "status": "active"
    })

    save_db(db)

    start_bot({
        "token": token,
        "owner": msg.from_user.id
    })

    bot.send_message(msg.chat.id, f"Bot @{info.get('username')} added ✅")

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

# ===== CHANNEL SYSTEM =====
@bot.message_handler(func=lambda m: m.text == "➕ Add Channel")
def add_channel(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    bot.send_message(msg.chat.id, "Send channel username (example: @channel)")
    bot.register_next_step_handler(msg, save_channel)

def save_channel(msg):
    ch = msg.text.strip()

    if not ch.startswith("@"):
        bot.send_message(msg.chat.id, "Invalid format ❌")
        return

    db = load_db()

    if ch in db["channels"]:
        bot.send_message(msg.chat.id, "Already added")
        return

    if len(db["channels"]) >= 5:
        bot.send_message(msg.chat.id, "Max 5 channels allowed")
        return

    db["channels"].append(ch)
    save_db(db)

    bot.send_message(msg.chat.id, f"{ch} added ✅")

@bot.message_handler(func=lambda m: m.text == "📋 Channels")
def list_channels(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    db = load_db()

    if not db["channels"]:
        bot.send_message(msg.chat.id, "No channels added")
        return

    for ch in db["channels"]:
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("❌ Delete", callback_data=f"delch|{ch}")
        )
        bot.send_message(msg.chat.id, ch, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "❌ Delete All Channels")
def delete_all_channels(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    db = load_db()
    db["channels"] = []
    save_db(db)

    bot.send_message(msg.chat.id, "All channels deleted ✅")

# ===== CALLBACKS =====
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    data = call.data.split("|")
    action = data[0]

    db = load_db()

    # BOT CONTROL
    if action in ["open", "stop", "del"]:
        token = data[1]

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

    # CHANNEL DELETE
    elif action == "delch":
        ch = data[1]
        if ch in db["channels"]:
            db["channels"].remove(ch)
            save_db(db)
            bot.answer_callback_query(call.id, "Channel removed ✅")

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
                tb.send_photo(b["owner"], msg.photo[-1].file_id, caption=msg.caption or "", reply_markup=markup)

            elif msg.content_type == "video":
                tb.send_video(b["owner"], msg.video.file_id, caption=msg.caption or "", reply_markup=markup)

        except:
            pass

    bot.send_message(msg.chat.id, "Broadcast sent ✅")

# ===== RUN SYSTEM =====
run_all_bots()

print("MAIN BOT RUNNING...")
bot.infinity_polling()
