import random
import time
import smtplib
from email.mime.text import MIMEText

OTP_STORE = {}

EMAIL = "googojoseh1@gmail.com"
APP_PASSWORD = "YOUR_APP_PASSWORD_HERE"

# ================= SEND OTP =================
def send_otp(to_email):
    code = str(random.randint(1000, 9999))

    OTP_STORE[to_email] = {
        "code": code,
        "time": time.time()
    }

    try:
        msg = MIMEText(f"Your verification code is: {code}")
        msg["Subject"] = "Your Login OTP Code"
        msg["From"] = EMAIL
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(EMAIL, APP_PASSWORD)
        server.sendmail(EMAIL, to_email, msg.as_string())
        server.quit()

        print(f"[OTP SENT] {to_email} -> {code}")

        return True

    except Exception as e:
        print("[EMAIL ERROR]", e)
        return False

# ================= VERIFY OTP =================
def verify_otp(email, code):
    data = OTP_STORE.get(email)

    if not data:
        return False

    # expire after 5 minutes
    if time.time() - data["time"] > 300:
        del OTP_STORE[email]
        return False

    if data["code"] == code:
        del OTP_STORE[email]
        return True

    return False
