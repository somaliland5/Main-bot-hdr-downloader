from flask import Flask, render_template, request, redirect, session, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = "super_secret_key_change_me"

ADMIN_PASSWORD = "12345"

# ================= LOAD DB =================
def load_db():
    default = {
        "bots": [],
        "users": [],
        "downloads": {}
    }

    if not os.path.exists("database.json"):
        return default

    try:
        with open("database.json", "r") as f:
            data = json.load(f)
            return {**default, **data}
    except:
        return default

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form["password"]

        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/")
        return "Wrong password ❌"

    return render_template("login.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= DASHBOARD =================
@app.route("/")
def dashboard():
    if not session.get("admin"):
        return redirect("/login")

    db = load_db()

    total_bots = len(db["bots"])
    total_users = len(db["users"])
    total_downloads = sum(db["downloads"].values()) if db["downloads"] else 0

    top_user = "None"
    if db["downloads"]:
        top_user = max(db["downloads"], key=db["downloads"].get)

    return render_template(
        "dashboard.html",
        bots=total_bots,
        users=total_users,
        downloads=total_downloads,
        top=top_user
    )

# ================= API (LIVE STATS OPTIONAL) =================
@app.route("/api/stats")
def stats():
    db = load_db()

    return jsonify({
        "bots": len(db["bots"]),
        "users": len(db["users"]),
        "downloads": sum(db["downloads"].values()) if db["downloads"] else 0
    })

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
