import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from auth import send_otp, verify_otp

TOKEN = "8283644457:AAFnO02xT8KbzqAfLv2MZZLjtT2PqR3KbM8"
bot = telebot.TeleBot(TOKEN)

# ================= USER STATE =================
verified_users = set()

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📩 Send Code", callback_data="send_code")
    )

    bot.send_message(
        msg.chat.id,
        "Welcome 👋\nPlease verify to continue",
        reply_markup=kb
    )

# ================= SEND CODE BUTTON =================
@bot.callback_query_handler(func=lambda call: call.data == "send_code")
def send_code(call):
    send_otp(bot, call.message.chat.id, call.from_user.id)

    bot.send_message(call.message.chat.id, "📨 Code sent to your chat")

# ================= CHECK CODE =================
@bot.message_handler(func=lambda m: True)
def check_code(msg):

    user_id = msg.from_user.id
    code = msg.text.strip()

    if verify_otp(user_id, code):
        verified_users.add(user_id)

        bot.send_message(
            msg.chat.id,
            "✅ Verified successfully!\nNow you can use the bot."
        )
    else:
        bot.send_message(
            msg.chat.id,
            "❌ Wrong or expired code.\nClick /start again."
        )

# ================= RUN BOT =================
print("Bot running...")
bot.infinity_polling(skip_pending=True)
