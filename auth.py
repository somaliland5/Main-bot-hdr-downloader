import random
import time

# ================= OTP STORE =================
OTP_STORE = {}

OTP_EXPIRE_SECONDS = 300  # 5 minutes

# ================= GENERATE OTP =================
def generate_otp(user_id):
    code = str(random.randint(1000, 9999))

    OTP_STORE[user_id] = {
        "code": code,
        "time": time.time()
    }

    return code

# ================= SEND OTP VIA BOT =================
def send_otp(bot, chat_id, user_id):
    """
    Sends OTP directly to Telegram chat
    """

    code = generate_otp(user_id)

    try:
        bot.send_message(
            chat_id,
            f"🔐 Your verification code is:\n\n<b>{code}</b>\n\n⏳ Valid for 5 minutes",
            parse_mode="HTML"
        )

        print(f"[OTP SENT] user:{user_id} code:{code}")

        return True

    except Exception as e:
        print("[OTP SEND ERROR]", e)
        return False

# ================= VERIFY OTP =================
def verify_otp(user_id, code):
    data = OTP_STORE.get(user_id)

    if not data:
        return False

    # expiry check
    if time.time() - data["time"] > OTP_EXPIRE_SECONDS:
        del OTP_STORE[user_id]
        return False

    # match check
    if data["code"] == code:
        del OTP_STORE[user_id]
        return True

    return False

# ================= CLEANUP =================
def cleanup():
    now = time.time()

    for uid in list(OTP_STORE.keys()):
        if now - OTP_STORE[uid]["time"] > OTP_EXPIRE_SECONDS:
            del OTP_STORE[uid]
