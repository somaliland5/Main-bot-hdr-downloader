import telebot
import yt_dlp
import os
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===== USER STATE =====
user_state = {}

# ===== USERS FILE =====
def load_users(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_users(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# ===== DOWNLOAD FUNCTION =====
def download_media(url):
    ydl_opts = {
        'outtmpl': 'media.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

# ===== START BOT =====
def start_sub_bot(TOKEN, OWNER_ID):
    bot = telebot.TeleBot(TOKEN)
    users_file = f"users_{TOKEN[:8]}.json"

    # ===== START =====
    @bot.message_handler(commands=['start'])
    def start(msg):
        users = load_users(users_file)

        if msg.chat.id not in users:
            users.append(msg.chat.id)
            save_users(users_file, users)

        bot.send_message(
            msg.chat.id,
            "Send a TikTok or Instagram link to download media."
        )

    # ===== BROADCAST =====
    @bot.message_handler(commands=['broadcast'])
    def broadcast(msg):
        if msg.from_user.id != OWNER_ID:
            return

        bot.send_message(msg.chat.id, "Send message / photo / video to broadcast")
        user_state[msg.chat.id] = "broadcast"

    # ===== HANDLE ALL =====
    @bot.message_handler(func=lambda m: True, content_types=['text','photo','video'])
    def handle(msg):
        users = load_users(users_file)

        # ===== BROADCAST MODE =====
        if user_state.get(msg.chat.id) == "broadcast":

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(
                    "Join Channel",
                    url="https://t.me/Create_Our_own_bot"
                )
            )

            for u in users:
                try:
                    if msg.content_type == "text":
                        bot.send_message(u, msg.text, reply_markup=markup)

                    elif msg.content_type == "photo":
                        bot.send_photo(
                            u,
                            msg.photo[-1].file_id,
                            caption=msg.caption or "",
                            reply_markup=markup
                        )

                    elif msg.content_type == "video":
                        bot.send_video(
                            u,
                            msg.video.file_id,
                            caption=msg.caption or "",
                            reply_markup=markup
                        )

                except:
                    pass

            bot.send_message(msg.chat.id, "Broadcast sent ✅")
            user_state[msg.chat.id] = None
            return

        # ===== DOWNLOAD MODE =====
        if msg.content_type != "text":
            bot.send_message(msg.chat.id, "Please send a valid link.")
            return

        url = msg.text.strip()

        bot.send_message(msg.chat.id, "Downloading...")

        try:
            file_path = download_media(url)

            caption = f"Via: @{bot.get_me().username}\nCreated: @Create_Our_own_bot"

            # send based on type
            if file_path.endswith((".mp4", ".mkv", ".mov")):
                with open(file_path, "rb") as f:
                    bot.send_video(msg.chat.id, f, caption=caption)

            elif file_path.endswith((".jpg", ".png", ".jpeg")):
                with open(file_path, "rb") as f:
                    bot.send_photo(msg.chat.id, f, caption=caption)

            else:
                with open(file_path, "rb") as f:
                    bot.send_document(msg.chat.id, f, caption=caption)

            os.remove(file_path)

        except Exception as e:
            bot.send_message(msg.chat.id, "Failed to download ❌")

    print(f"Sub bot running: {TOKEN[:8]}...")
    bot.infinity_polling()
