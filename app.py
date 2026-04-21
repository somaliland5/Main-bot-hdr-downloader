from flask import Flask, render_template, request, redirect, session, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = "change_this_secret"

ADMIN_PASSWORD = "666661"

# ================= LOAD DB =================
def load_db():
    default = {
        "bots": [],
        "users": [],
        "downloads": {},
        "channels": [],
        "ads": "Your Ad Here"
    }

    if not os.path.exists("database.json"):
        return default

    try:
        with open("database.json", "r") as f:
            data = json.load(f)
            return {**default, **data}
    except:
        return default

def save_db(data):
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
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

    stats = {
        "bots": len(db["bots"]),
        "users": len(db["users"]),
        "downloads": sum(db["downloads"].values()) if db["downloads"] else 0,
        "channels": len(db["channels"])
    }

    top_user = "None"
    if db["downloads"]:
        top_user = max(db["downloads"], key=db["downloads"].get)

    return render_template("dashboard.html", stats=stats, top=top_user, ads=db["ads"])

# ================= API STATS =================
@app.route("/api/stats")
def api_stats():
    db = load_db()
    return jsonify({
        "bots": len(db["bots"]),
        "users": len(db["users"]),
        "downloads": sum(db["downloads"].values()) if db["downloads"] else 0
    })

# ================= BROADCAST (API READY) =================
@app.route("/broadcast", methods=["POST"])
def broadcast():
    if not session.get("admin"):
        return "Unauthorized"

    message = request.form["message"]
    return f"Broadcast sent: {message}"

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
