import random
import time

# ================= OTP STORE =================
OTP_STORE = {}

# OTP expiry (5 minutes)
OTP_EXPIRE = 300

# ================= GENERATE OTP =================
def send_otp(email):
    code = str(random.randint(1000, 9999))

    OTP_STORE[email] = {
        "code": code,
        "time": time.time()
    }

    print(f"[OTP GENERATED] {email} -> {code}")

    # Instead of email, we return code (for debugging OR UI)
    return code

# ================= VERIFY OTP =================
def verify_otp(email, code):
    data = OTP_STORE.get(email)

    if not data:
        return False

    # expiry check
    if time.time() - data["time"] > OTP_EXPIRE:
        del OTP_STORE[email]
        return False

    if data["code"] == code:
        del OTP_STORE[email]
        return True

    return False
