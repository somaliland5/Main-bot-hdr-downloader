from flask import Flask, render_template, request, redirect, session
import json, os

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

ADMIN_PASSWORD = "admin123"
USER_PASSWORD = "user123"

# ================= DB =================
def load_db():
    if not os.path.exists("database.json"):
        return {"messages": []}

    with open("database.json", "r") as f:
        return json.load(f)

def save_db(db):
    with open("database.json", "w") as f:
        json.dump(db, f, indent=4)

# ================= ROOT FIX (IMPORTANT) =================
@app.route("/")
def home():
    return redirect("/login")

# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        password = request.form["password"]
        name = request.form.get("name","User")

        # ADMIN
        if password == ADMIN_PASSWORD:
            session["role"] = "admin"
            return redirect("/admin")

        # USER
        if password == USER_PASSWORD:
            session["role"] = "user"
            session["name"] = name
            return redirect("/user")

        return "Wrong password ❌"

    return render_template("login.html")

# ================= USER PAGE =================
@app.route("/user")
def user():
    if session.get("role") != "user":
        return redirect("/login")

    db = load_db()
    return render_template("user.html", name=session.get("name"), messages=db["messages"])

# ================= ADMIN PAGE =================
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect("/login")

    db = load_db()
    return render_template("admin.html", messages=db["messages"])

# ================= SEND MESSAGE =================
@app.route("/send", methods=["POST"])
def send():
    if not session.get("role"):
        return redirect("/login")

    db = load_db()

    msg = request.form["message"]
    name = session.get("name","User")

    db["messages"].append({
        "name": name,
        "msg": msg
    })

    save_db(db)
    return redirect("/user")

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
