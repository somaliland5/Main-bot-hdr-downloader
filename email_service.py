import smtplib
import random
from email.mime.text import MIMEText

OTP_STORE = {}

EMAIL = "googojoseh1@gmail.com"
APP_PASSWORD = "glkv suhv gfbf fhdm"

def send_code(to_email):
    code = str(random.randint(1000,9999))
    OTP_STORE[to_email] = code

    msg = MIMEText(f"Your login code is: {code}")
    msg["Subject"] = "Login Code"
    msg["From"] = EMAIL
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, APP_PASSWORD)
    server.sendmail(EMAIL, to_email, msg.as_string())
    server.quit()

    return code
