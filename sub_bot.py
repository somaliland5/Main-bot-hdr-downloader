import telebot
import os
import json
import requests
import yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= USER STATE =================
user_state = {}

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
        filename = ydl.prepare_filename(info)
        return filename

# ================= FORCE JOIN API =================
def check_access(user_id):
    try:
        r = requests.post(
            "http://localhost:8080/check_user",  # Railway URL replace here
            json={"user_id": user_id},
            timeout=10
        ).json()

        return r.get("ok", False), r.get("channels", [])

    except:
        return True, []

# ================= START BOT =================
def start_sub_bot(TOKEN, OWNER_ID):

    bot = telebot.TeleBot(TOKEN)
    users_file = f"users_{TOKEN[:8]}.json"

    bot_username = bot.get_me().username

    # ================= START =================
    @bot.message_handler(commands=['start'])
    def start(msg):

        ok, missing = check_access(msg.from_user.id)

        if not ok:
            markup = InlineKeyboardMarkup()

            for ch in missing:
                markup.add(
                    InlineKeyboardButton(
                        f"Join {ch}",
                        url=f"https://t.me/{ch.replace('@','')}"
                    )
                )

            markup.add(
                InlineKeyboardButton("✅ Check Again", callback_data="check")
            )

            bot.send_message(
                msg.chat.id,
                "⚠️ Join required channels first",
                reply_markup=markup
            )
            return

        users = load_users(users_file)
        if msg.chat.id not in users:
            users.append(msg.chat.id)
            save_users(users_file, users)

        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("⚡ 1080P DOWNLOAD", callback_data="1080"),
            InlineKeyboardButton("🔥 4K DOWNLOAD", callback_data="4k")
        )

        bot.send_message(
            msg.chat.id,
            "📥 Send TikTok / Instagram link",
            reply_markup=kb
        )

    # ================= CHECK JOIN =================
    @bot.callback_query_handler(func=lambda call: call.data == "check")
    def check(call):
        ok, missing = check_access(call.from_user.id)

        if ok:
            bot.send_message(call.message.chat.id, "Access granted ✅")
        else:
            bot.answer_callback_query(call.id, "Join required ❌")

    # ================= QUALITY SELECT =================
    quality_map = {}

    @bot.callback_query_handler(func=lambda call: call.data in ["1080", "4k"])
    def quality(call):
        quality_map[call.from_user.id] = "best" if call.data == "1080" else "bestvideo+bestaudio"

        bot.answer_callback_query(call.id, f"{call.data.upper()} selected")

    # ================= HANDLE DOWNLOAD =================
    @bot.message_handler(func=lambda m: True, content_types=['text'])
    def handle(msg):

        url = msg.text.strip()

        loading = bot.send_message(msg.chat.id, "Downloading... ⏳")

        try:
            quality = quality_map.get(msg.from_user.id, "best")

            file_path = download_media(url, quality)

            bot.delete_message(msg.chat.id, loading.message_id)

            # MESSAGE 2 (MEDIA)
            caption = f"Via: @{bot_username}"

            with open(file_path, "rb") as f:

                if file_path.endswith((".mp4", ".mov", ".mkv")):
                    bot.send_video(msg.chat.id, f, caption=caption)

                elif file_path.endswith((".jpg", ".png", ".jpeg")):
                    bot.send_photo(msg.chat.id, f, caption=caption)

                else:
                    bot.send_document(msg.chat.id, f, caption=caption)

            # MESSAGE 3 (CREATED)
            bot.send_message(msg.chat.id, "Created: @Create_Our_own_bot")

            os.remove(file_path)

        except:
            bot.delete_message(msg.chat.id, loading.message_id)
            bot.send_message(msg.chat.id, "Download failed ❌")

    print(f"[SUB BOT RUNNING] {TOKEN[:8]}")
    bot.infinity_polling()
