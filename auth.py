import random
import smtplib
from email.mime.text import MIMEText

# ================= OTP STORE =================
OTP_STORE = {}

# ================= EMAIL CONFIG =================
EMAIL = "yous01888@gmail.com"

# ⚠️ IMPORTANT:
# Use Gmail App Password (not normal password)
APP_PASSWORD = "mdqd zgwj vskn blii"

# ================= SEND OTP =================
def send_otp(to_email):
    code = str(random.randint(1000, 9999))
    OTP_STORE[to_email] = code

    try:
        msg = MIMEText(f"Your verification code is: {code}")
        msg["Subject"] = "Login Verification Code"
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
    stored = OTP_STORE.get(email)

    if stored and stored == code:
        del OTP_STORE[email]
        return True

    return False
