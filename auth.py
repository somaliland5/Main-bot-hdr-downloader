import random
import time

# ================= OTP STORE =================
OTP_STORE = {}

OTP_EXPIRE = 300  # 5 minutes

# ================= GENERATE OTP =================
def generate_otp(user_id):
    code = str(random.randint(1000, 9999))

    OTP_STORE[user_id] = {
        "code": code,
        "time": time.time()
    }

    return code

# ================= SEND OTP =================
def send_otp(bot, chat_id, user_id):
    code = generate_otp(user_id)

    bot.send_message(
        chat_id,
        f"🔐 Your login code is:\n\n<b>{code}</b>\n\n⏳ Expires in 5 minutes",
        parse_mode="HTML"
    )

    print(f"[OTP] sent to {user_id}: {code}")

# ================= VERIFY OTP =================
def verify_otp(user_id, code):
    data = OTP_STORE.get(user_id)

    if not data:
        return False

    # expired
    if time.time() - data["time"] > OTP_EXPIRE:
        del OTP_STORE[user_id]
        return False

    # match
    if data["code"] == code:
        del OTP_STORE[user_id]
        return True

    return False

# ================= CLEANUP =================
def cleanup():
    now = time.time()

    for uid in list(OTP_STORE.keys()):
        if now - OTP_STORE[uid]["time"] > OTP_EXPIRE:
            del OTP_STORE[uid]
