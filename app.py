from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DB =================
def load_db():
    if not os.path.exists("database.json"):
        return {"users": [], "bots": []}
    return json.load(open("database.json"))

def save_db(db):
    with open("database.json", "w") as f:
        json.dump(db, f, indent=4)

# ================= HOME =================
@app.route("/")
def home():
    user_id = session.get("user", "Unknown")
    return render_template("index.html", user_id=user_id)

# ================= ADD BOT =================
@app.route("/add_bot", methods=["GET", "POST"])
def add_bot():
    db = load_db()

    if request.method == "POST":
        token = request.form.get("token")

        db["bots"].append({
            "token": token,
            "status": "active"
        })

        save_db(db)
        return redirect("/my_bots")

    return render_template("add_bot.html")

# ================= MY BOTS =================
@app.route("/my_bots")
def my_bots():
    db = load_db()
    return render_template("my_bots.html", bots=db["bots"])

# ================= DELETE BOT =================
@app.route("/delete_bot/<token>")
def delete_bot(token):
    db = load_db()

    db["bots"] = [b for b in db["bots"] if b["token"] != token]

    save_db(db)
    return redirect("/my_bots")

# ================= ADMIN =================
@app.route("/admin")
def admin():
    db = load_db()
    return render_template("admin.html",
        users=len(db["users"]),
        bots=len(db["bots"])
    )

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
