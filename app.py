from flask import Flask, render_template, request, redirect, session
import json
import os
import traceback

from auth import send_otp, verify_otp

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET_KEY"

# ================= DB =================
def load_db():
    try:
        if not os.path.exists("database.json"):
            return {"users": [], "bots": []}

        with open("database.json", "r") as f:
            return json.load(f)

    except Exception as e:
        print("DB LOAD ERROR:", e)
        return {"users": [], "bots": []}


def save_db(db):
    try:
        with open("database.json", "w") as f:
            json.dump(db, f, indent=4)
    except Exception as e:
        print("DB SAVE ERROR:", e)

# ================= ERROR HANDLER =================
@app.errorhandler(500)
def server_error(e):
    print("🔥 INTERNAL ERROR:")
    print(traceback.format_exc())
    return "Internal Server Error (check logs)", 500

# ================= HOME =================
@app.route("/")
def home():
    return redirect("/login")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            email = request.form.get("email")

            if not email:
                return "Email required"

            # send OTP
            send_otp(app, email, email)  # safe call pattern

            session["email"] = email

            return redirect("/verify")

        return render_template("login.html")

    except Exception as e:
        print("LOGIN ERROR:", e)
        return "Internal Server Error", 500

# ================= VERIFY =================
@app.route("/verify", methods=["GET", "POST"])
def verify():
    try:
        if request.method == "POST":
            code = request.form.get("code")
            email = session.get("email")

            if not email:
                return redirect("/login")

            if verify_otp(email, code):
                session["user"] = email
                return redirect("/dashboard")

            return "Wrong or expired code"

        return render_template("verify.html")

    except Exception as e:
        print("VERIFY ERROR:", e)
        return "Internal Server Error", 500

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    try:
        if not session.get("user"):
            return redirect("/login")

        db = load_db()

        return render_template(
            "dashboard.html",
            users=len(db.get("users", [])),
            bots=len(db.get("bots", []))
        )

    except Exception as e:
        print("DASHBOARD ERROR:", e)
        return "Internal Server Error", 500

# ================= ADD BOT =================
@app.route("/add_bot", methods=["POST"])
def add_bot():
    try:
        if not session.get("user"):
            return redirect("/login")

        token = request.form.get("token")

        if not token:
            return "Token required"

        db = load_db()

        db["bots"].append({
            "token": token,
            "owner": session["user"],
            "status": "active"
        })

        save_db(db)

        return redirect("/dashboard")

    except Exception as e:
        print("ADD BOT ERROR:", e)
        return "Internal Server Error", 500

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= RUN =================
if __name__ == "__main__":
    print("🚀 APP STARTING...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
