import telebot
import yt_dlp
import os
import json

user_data = {}

def load_users(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_users(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.mp4',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def start_sub_bot(TOKEN, OWNER_ID):
    bot = telebot.TeleBot(TOKEN)
    users_file = f"users_{TOKEN[:10]}.json"

    # ===== START =====
    @bot.message_handler(commands=['start'])
    def start(msg):
        users = load_users(users_file)
        if msg.chat.id not in users:
            users.append(msg.chat.id)
            save_users(users_file, users)

        bot.send_message(msg.chat.id, "Send TikTok or Instagram link")

    # ===== BROADCAST (ADMIN ONLY) =====
    @bot.message_handler(commands=['broadcast'])
    def broadcast(msg):
        if msg.from_user.id != OWNER_ID:
            return

        bot.send_message(msg.chat.id, "Send message to broadcast")
        user_data[msg.chat.id] = "broadcast"

    @bot.message_handler(func=lambda m: True)
    def handle(msg):
        users = load_users(users_file)

        # BROADCAST MODE
        if user_data.get(msg.chat.id) == "broadcast":
            for u in users:
                try:
                    bot.send_message(u, msg.text)
                except:
                    pass

            bot.send_message(msg.chat.id, "Broadcast sent ✅")
            user_data[msg.chat.id] = None
            return

        # DOWNLOAD
        url = msg.text
        bot.send_message(msg.chat.id, "Downloading...")

        try:
            download_video(url)

            with open("video.mp4", "rb") as f:
                bot.send_video(
                    msg.chat.id,
                    f,
                    caption=f"Via: @{bot.get_me().username}\nCreated: @Create_Our_own_bot"
                )

            os.remove("video.mp4")

        except:
            bot.send_message(msg.chat.id, "Failed to download")

    bot.infinity_polling()
