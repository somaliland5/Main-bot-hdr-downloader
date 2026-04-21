import telebot
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from auth import send_otp, verify_otp

TOKEN = "8283644457:AAFnO02xT8KbzqAfLv2MZZLjtT2PqR3KbM8"
bot = telebot.TeleBot(TOKEN)

# ================= USER STATE =================
verified_users = set()
otp_store = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):

    user_id = msg.from_user.id

    # generate OTP
    code = str(random.randint(1000, 9999))
    otp_store[user_id] = code

    # send via auth system (optional use)
    try:
        send_otp(bot, msg.chat.id, user_id)
    except:
        pass

    # buttons
    kb = InlineKeyboardMarkup()

    kb.add(
        InlineKeyboardButton("📋 Copy Code", callback_data=f"copy|{code}")
    )

    kb.add(
        InlineKeyboardButton(
            "🌐 Verify on Web",
            url="https://main-bot-hdr-downloader-production.up.railway.app/verify"
        )
    )

    kb.add(
        InlineKeyboardButton(
            "🤖 Go to Date Bot",
            url="https://t.me/Date_to_daybot"
        )
    )

    bot.send_message(
        msg.chat.id,
        f"🔐 Your Login Code:\n\n`{code}`\n\n👉 Use buttons below",
        parse_mode="Markdown",
        reply_markup=kb
    )

# ================= COPY CODE =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("copy"))
def copy_code(call):

    code = call.data.split("|")[1]

    bot.answer_callback_query(
        call.id,
        f"Code: {code}",
        show_alert=True
    )

# ================= VERIFY MESSAGE =================
@bot.message_handler(func=lambda m: True)
def check_code(msg):

    user_id = msg.from_user.id
    text = msg.text.strip()

    if text.startswith("/"):
        return

    # check OTP
    if otp_store.get(user_id) == text or verify_otp(user_id, text):

        verified_users.add(user_id)

        bot.send_message(
            msg.chat.id,
            "✅ Verified successfully!\nNow you can use the bot 🚀"
        )
    else:
        bot.send_message(
            msg.chat.id,
            "❌ Wrong or expired code.\nPress /start again."
        )

# ================= RUN =================
print("🤖 Bot running...")
bot.infinity_polling(skip_pending=True)
