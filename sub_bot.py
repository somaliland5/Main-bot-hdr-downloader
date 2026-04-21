import telebot
import os
import json
import requests
import yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= LOAD DB =================
def load_db():
    default = {"channels": []}

    if not os.path.exists("database.json"):
        return default

    try:
        with open("database.json", "r") as f:
            data = json.load(f)
            return {**default, **data}
    except:
        return default

# ================= USERS =================
def load_users(file):
    if not os.path.exists(file):
        return []

    with open(file, "r") as f:
        return json.load(f)

def save_users(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# ================= DOWNLOAD =================
def download_media(url, quality="best"):
    ydl_opts = {
        "outtmpl": "media.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "format": quality
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# ================= BOT CORE =================
def start_sub_bot(TOKEN, OWNER_ID, stop_flag):

    bot = telebot.TeleBot(TOKEN)
    users_file = f"users_{TOKEN[:8]}.json"

    try:
        bot_username = bot.get_me().username
    except:
        return

    quality_map = {}

    # ================= START =================
    @bot.message_handler(commands=['start'])
    def start(msg):

        if not stop_flag["run"]:
            return

        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("⚡ 1080P", callback_data="1080"),
            InlineKeyboardButton("🔥 4K", callback_data="4k")
        )

        bot.send_message(msg.chat.id, "📥 Send link", reply_markup=kb)

    # ================= QUALITY =================
    @bot.callback_query_handler(func=lambda call: call.data in ["1080", "4k"])
    def quality(call):

        if not stop_flag["run"]:
            return

        quality_map[call.from_user.id] = "best" if call.data == "1080" else "bestvideo+bestaudio"
        bot.answer_callback_query(call.id)

    # ================= HANDLE =================
    @bot.message_handler(func=lambda m: True)
    def handle(msg):

        if not stop_flag["run"]:
            return

        url = msg.text.strip()

        loading = bot.send_message(msg.chat.id, "Downloading...")

        try:
            quality = quality_map.get(msg.from_user.id, "best")

            file_path = download_media(url, quality)

            bot.delete_message(msg.chat.id, loading.message_id)

            with open(file_path, "rb") as f:
                bot.send_document(msg.chat.id, f)

            os.remove(file_path)

        except Exception as e:
            print("ERROR:", e)
            bot.send_message(msg.chat.id, "Failed ❌")

    print(f"[BOT RUNNING] {TOKEN[:8]}")

    bot.infinity_polling(skip_pending=True)
