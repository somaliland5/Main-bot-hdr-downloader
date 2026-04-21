from flask import Flask, render_template, request, redirect, session
import json, os
from auth import send_otp, verify_otp

app = Flask(__name__)
app.secret_key = "super_secret_key"

# ================= DB =================
def load_db():
    if not os.path.exists("database.json"):
        return {"users": [], "bots": []}

    with open("database.json", "r") as f:
        return json.load(f)

def save_db(db):
    with open("database.json", "w") as f:
        json.dump(db, f, indent=4)

# ================= HOME =================
@app.route("/")
def home():
    return redirect("/login")

# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]

        send_otp(email)
        session["email"] = email

        return redirect("/verify")

    return render_template("login.html")

# ================= VERIFY =================
@app.route("/verify", methods=["GET","POST"])
def verify():
    if request.method == "POST":
        code = request.form["code"]
        email = session.get("email")

        if verify_otp(email, code):
            session["user"] = email
            return redirect("/dashboard")

        return "Wrong OTP ❌"

    return render_template("verify.html")

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect("/login")

    db = load_db()

    return render_template("dashboard.html",
        bots=len(db["bots"]),
        users=len(db["users"])
    )

# ================= ADD BOT =================
@app.route("/add_bot", methods=["POST"])
def add_bot():
    if not session.get("user"):
        return redirect("/login")

    token = request.form["token"]

    db = load_db()

    db["bots"].append({
        "token": token,
        "owner": session["user"],
        "status": "active"
    })

    save_db(db)

    return redirect("/dashboard")

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
