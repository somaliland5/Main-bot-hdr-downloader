from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, send
from email_service import send_code, OTP_STORE

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# ================= HOME =================
@app.route("/")
def home():
    return redirect("/login")

# ================= LOGIN (EMAIL STEP 1) =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        send_code(email)
        session["email"] = email
        return redirect("/verify")

    return render_template("login.html")

# ================= VERIFY OTP =================
@app.route("/verify", methods=["GET","POST"])
def verify():
    if request.method == "POST":
        code = request.form["code"]
        email = session.get("email")

        if OTP_STORE.get(email) == code:
            session["user"] = email
            return redirect("/chat")

        return "Wrong code ❌"

    return render_template("verify.html")

# ================= CHAT PAGE =================
@app.route("/chat")
def chat():
    if not session.get("user"):
        return redirect("/login")

    return render_template("chat.html", user=session["user"])

# ================= REAL-TIME CHAT =================
@socketio.on("message")
def handle(msg):
    user = session.get("user","User")
    send({"user": user, "msg": msg}, broadcast=True)

# ================= RUN =================
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
