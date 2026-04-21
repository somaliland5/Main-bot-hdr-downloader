import telebot
import json
import os
import requests
import threading
from flask import Flask, request, jsonify
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# ================= ENV =================
TOKEN = os.getenv("MAIN_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

# ================= FLASK APP (FOR FORCE JOIN API) =================
app = Flask(__name__)

# ================= DATABASE =================
def load_db():
    if not os.path.exists("database.json"):
        return {
            "bots": [],
            "users": [],
            "downloads": {},
            "channels": []
        }
    with open("database.json", "r") as f:
        return json.load(f)

def save_db(data):
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)

# ================= TRACK USER =================
def track_user(user_id):
    db = load_db()
    if user_id not in db["users"]:
        db["users"].append(user_id)
        save_db(db)

# ================= FORCE JOIN CHECK API =================
@app.route("/check_user", methods=["POST"])
def check_user():
    data = request.json
    user_id = data.get("user_id")

    db = load_db()
    channels = db.get("channels", [])

    missing = []

    for ch in channels:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                missing.append(ch)
        except:
            missing.append(ch)

    if missing:
        return jsonify({
            "ok": False,
            "channels": missing
        })

    return jsonify({"ok": True})

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    track_user(msg.from_user.id)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("➕ Add Bot", "📦 My Bots")

    if msg.from_user.id == ADMIN_ID:
        kb.add("📊 Admin Panel")

    bot.send_message(
        msg.chat.id,
        "🚀 Welcome to Pro Bot System",
        reply_markup=kb
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

    bot.send_message(msg.chat.id, f"🤖 @{info['username']} added successfully")

# ================= MY BOTS =================
@bot.message_handler(func=lambda m: m.text == "📦 My Bots")
def my_bots(msg):
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
                InlineKeyboardButton("❌ Delete Bot", callback_data=f"del|{b['token']}")
            )

            bot.send_message(
                msg.chat.id,
                f"🤖 @{b['username']}\nStatus: {b['status']}",
                reply_markup=markup
            )

    if not found:
        bot.send_message(msg.chat.id, "No bots found")

# ================= ADMIN PANEL =================
@bot.message_handler(func=lambda m: m.text == "📊 Admin Panel")
def admin_panel(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    db = load_db()

    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton("🤖 TOTAL BOTS", callback_data="bots"))
    kb.add(InlineKeyboardButton("👥 TOTAL USERS", callback_data="users"))
    kb.add(InlineKeyboardButton("📥 TOTAL DOWNLOADS", callback_data="downloads"))
    kb.add(InlineKeyboardButton("🏆 TOP USER", callback_data="top"))

    kb.add(InlineKeyboardButton("📢 BROADCAST", callback_data="broadcast"))

    bot.send_message(msg.chat.id, "📊 Admin Panel", reply_markup=kb)

# ================= CALLBACKS =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    db = load_db()
    data = call.data.split("|")
    action = data[0]

    # ===== STATS =====
    if action == "bots":
        bot.send_message(call.message.chat.id, f"🤖 Bots: {len(db['bots'])}")

    elif action == "users":
        bot.send_message(call.message.chat.id, f"👥 Users: {len(db['users'])}")

    elif action == "downloads":
        total = sum(db["downloads"].values())
        bot.send_message(call.message.chat.id, f"📥 Downloads: {total}")

    elif action == "top":
        if not db["downloads"]:
            bot.send_message(call.message.chat.id, "No downloads yet")
            return

        top = max(db["downloads"], key=db["downloads"].get)
        bot.send_message(call.message.chat.id, f"🏆 Top User: {top}")

    # ===== DELETE BOT (FULL REMOVE) =====
    elif action == "del":
        token = data[1]

        db["bots"] = [b for b in db["bots"] if b["token"] != token]
        save_db(db)

        bot.answer_callback_query(call.id, "Bot deleted ❌")
        bot.send_message(call.message.chat.id, "Bot removed completely")

# ================= BROADCAST =================
@bot.message_handler(commands=['broadcast'])
def broadcast(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    bot.send_message(msg.chat.id, "Send message to broadcast")
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(msg):
    db = load_db()

    for u in db["users"]:
        try:
            bot.send_message(u, msg.text)
        except:
            pass

    bot.send_message(msg.chat.id, "Broadcast sent ✅")

# ================= RUN FLASK =================
def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# ================= RUN BOT =================
print("MAIN BOT RUNNING...")
bot.infinity_polling()
