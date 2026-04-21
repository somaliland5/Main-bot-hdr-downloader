import threading
import json
import os
from sub_bot import start_sub_bot
from app import app   # 👈 web dashboard import

running_bots = {}

# ================= LOAD DB =================
def load_db():
    default = {"bots": [], "channels": []}

    if not os.path.exists("database.json"):
        return default

    try:
        with open("database.json", "r") as f:
            data = json.load(f)
            return {**default, **data}
    except:
        return default

# ================= START WEB =================
def run_web():
    print("[WEB STARTING]")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ================= START BOT =================
def start_bot(bot_data):
    token = bot_data.get("token")
    owner = bot_data.get("owner")

    if not token or token in running_bots:
        return

    def run():
        try:
            start_sub_bot(token, owner)
        except Exception as e:
            print(f"[BOT ERROR] {token[:8]} -> {e}")

    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

    running_bots[token] = t
    print(f"[BOT STARTED] {token[:8]}")

# ================= RUN ALL BOTS =================
def run_all_bots():
    db = load_db()

    for bot in db.get("bots", []):
        if bot.get("status") == "active":
            start_bot(bot)

    print("[SYSTEM] ALL BOTS STARTED")

# ================= MAIN START =================
if __name__ == "__main__":

    # 1️⃣ start web in thread
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    # 2️⃣ start bots
    run_all_bots()

    # 3️⃣ keep alive
    web_thread.join()
