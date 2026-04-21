import telebot
import yt_dlp
import os
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

user_state = {}

# ===== LOAD DB =====
def load_db():
    if not os.path.exists("database.json"):
        return {"channels": []}
    with open("database.json", "r") as f:
        return json.load(f)

# ===== USERS =====
def load_users(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_users(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# ===== DOWNLOAD =====
def download_media(url):
    ydl_opts = {
        "outtmpl": "media.%(ext)s",
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

# ===== FORCE JOIN CHECK =====
def not_joined(bot, user_id):
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

    return missing

# ===== MAIN BOT =====
def start_sub_bot(TOKEN, OWNER_ID):

    bot = telebot.TeleBot(TOKEN)
    users_file = f"users_{TOKEN[:8]}.json"

    bot_username = bot.get_me().username

    # ===== START =====
    @bot.message_handler(commands=['start'])
    def start(msg):

        missing = not_joined(bot, msg.from_user.id)

        if missing:
            markup = InlineKeyboardMarkup()
            for ch in missing:
                markup.add(
                    InlineKeyboardButton(
                        f"Join {ch}",
                        url=f"https://t.me/{ch.replace('@','')}"
                    )
                )
            markup.add(
                InlineKeyboardButton("Check Again", callback_data="check")
            )

            bot.send_message(msg.chat.id, "You must join channels first", reply_markup=markup)
            return

        users = load_users(users_file)
        if msg.chat.id not in users:
            users.append(msg.chat.id)
            save_users(users_file, users)

        bot.send_message(msg.chat.id, "Send TikTok or Instagram link")

    # ===== CHECK JOIN =====
    @bot.callback_query_handler(func=lambda call: call.data == "check")
    def check(call):
        missing = not_joined(bot, call.from_user.id)
        if not missing:
            bot.send_message(call.message.chat.id, "Access granted ✅")
        else:
            bot.answer_callback_query(call.id, "Join required ❌")

    # ===== HANDLE =====
    @bot.message_handler(func=lambda m: True)
    def handle(msg):

        users = load_users(users_file)

        url = msg.text.strip()

        # ===== MESSAGE 1 =====
        loading_msg = bot.send_message(msg.chat.id, "Downloading... ⏳")

        try:
            file_path = download_media(url)

            # DELETE DOWNLOADING MESSAGE
            bot.delete_message(msg.chat.id, loading_msg.message_id)

            # ===== MESSAGE 2 (VIDEO + CAPTION) =====
            caption = f"Via: @{bot_username}"

            with open(file_path, "rb") as f:
                if file_path.endswith((".mp4", ".mov", ".mkv")):
                    bot.send_video(msg.chat.id, f, caption=caption)

                elif file_path.endswith((".jpg", ".png", ".jpeg")):
                    bot.send_photo(msg.chat.id, f, caption=caption)

                else:
                    bot.send_document(msg.chat.id, f, caption=caption)

            # ===== MESSAGE 3 (CREATED SEPARATE) =====
            bot.send_message(msg.chat.id, "Created: @Create_Our_own_bot")

            os.remove(file_path)

        except:
            bot.delete_message(msg.chat.id, loading_msg.message_id)
            bot.send_message(msg.chat.id, "Download failed ❌")

    print(f"Sub bot running: {TOKEN[:8]}")
    bot.infinity_polling()
