import telebot
import json
import os
import requests
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("MAIN_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

# ================= SAFE DB =================
def load_db():
    default = {
        "bots": [],
        "users": [],
        "downloads": {},
        "channels": []
    }

    if not os.path.exists("database.json"):
        return default

    try:
        with open("database.json", "r") as f:
            data = json.load(f)
            return {**default, **data}
    except:
        return default

def save_db(data):
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)

# ================= TRACK USERS =================
def track_user(user_id):
    db = load_db()
    if user_id not in db["users"]:
        db["users"].append(user_id)
        save_db(db)

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    track_user(msg.from_user.id)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("➕ Add Bot", "📦 My Bots")

    if msg.from_user.id == ADMIN_ID:
        kb.add("📊 Admin Panel", "📢 Broadcast")

    bot.send_message(
        msg.chat.id,
        "🚀 Welcome to Pro Bot System",
        reply_markup=kb
    )

    # ===== 4K UNLOCK UI (ADMIN VIEW USERS) =====
    if msg.from_user.id == ADMIN_ID:
        inline = InlineKeyboardMarkup()
        inline.add(
            InlineKeyboardButton("🔓 UNLOCK 4K QUALITY", callback_data="unlock4k")
        )

        bot.send_message(
            msg.chat.id,
            "Premium Control Panel",
            reply_markup=inline
        )

# ================= ADD BOT =================
@bot.message_handler(func=lambda m: m.text == "➕ Add Bot")
def add_bot(msg):
    bot.send_message(msg.chat.id, "Send bot token")
    bot.register_next_step_handler(msg, save_bot)

def save_bot(msg):
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
            bot.send_message(msg.chat.id, "Bot already exists")
            return

    info = r["result"]

    db["bots"].append({
        "token": token,
        "owner": msg.from_user.id,
        "username": info["username"],
        "status": "active"
    })

    save_db(db)

    bot.send_message(msg.chat.id, f"🤖 @{info['username']} added")

# ================= MY BOTS =================
@bot.message_handler(func=lambda m: m.text == "📦 My Bots")
def my_bots(msg):
    db = load_db()

    for b in db["bots"]:
        if b["owner"] == msg.from_user.id:

            markup = InlineKeyboardMarkup()

            markup.add(
                InlineKeyboardButton("🟢 Open", callback_data=f"open|{b['token']}"),
                InlineKeyboardButton("🔴 Stop", callback_data=f"stop|{b['token']}")
            )

            markup.add(
                InlineKeyboardButton("❌ Delete Bot", callback_data=f"del|{b['token']}")
            )

            bot.send_message(
                msg.chat.id,
                f"🤖 @{b['username']}\nStatus: {b['status']}",
                reply_markup=markup
            )

# ================= ADMIN PANEL =================
@bot.message_handler(func=lambda m: m.text == "📊 Admin Panel")
def admin_panel(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    db = load_db()

    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton("🤖 TOTAL BOTS", callback_data="bots"))
    kb.add(InlineKeyboardButton("👥 USERS", callback_data="users"))
    kb.add(InlineKeyboardButton("📥 DOWNLOADS", callback_data="downloads"))
    kb.add(InlineKeyboardButton("🏆 TOP USER", callback_data="top"))
    kb.add(InlineKeyboardButton("📢 BROADCAST ALL", callback_data="bcall"))

    bot.send_message(msg.chat.id, "📊 Admin Panel", reply_markup=kb)

# ================= BROADCAST SYSTEM =================
@bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
def broadcast(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    bot.send_message(msg.chat.id, "Send message / photo / video / button")
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(msg):
    db = load_db()

    for u in db["users"]:
        try:
            if msg.content_type == "text":
                bot.send_message(u, msg.text)

            elif msg.content_type == "photo":
                bot.send_photo(u, msg.photo[-1].file_id, caption=msg.caption or "")

            elif msg.content_type == "video":
                bot.send_video(u, msg.video.file_id, caption=msg.caption or "")

        except:
            pass

    bot.send_message(msg.chat.id, "Broadcast sent ✅")

# ================= CALLBACKS =================
@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    db = load_db()
    data = call.data.split("|")
    action = data[0]

    if action == "bots":
        bot.send_message(call.message.chat.id, f"Bots: {len(db['bots'])}")

    elif action == "users":
        bot.send_message(call.message.chat.id, f"Users: {len(db['users'])}")

    elif action == "downloads":
        total = sum(db["downloads"].values())
        bot.send_message(call.message.chat.id, f"Downloads: {total}")

    elif action == "top":
        if db["downloads"]:
            top = max(db["downloads"], key=db["downloads"].get)
            bot.send_message(call.message.chat.id, f"Top User: {top}")

    elif action == "unlock4k":
        bot.send_message(
            call.message.chat.id,
            "🔓 4K UNLOCKED SYSTEM\nContact: @scholes1"
        )

    elif action == "bcall":
        bot.send_message(call.message.chat.id, "Send broadcast message")
        bot.register_next_step_handler(call.message, do_broadcast)

    elif action == "del":
        token = data[1]
        db["bots"] = [b for b in db["bots"] if b["token"] != token]
        save_db(db)
        bot.send_message(call.message.chat.id, "Bot deleted ❌")

# ================= RUN =================
print("MAIN BOT RUNNING...")
bot.infinity_polling()
