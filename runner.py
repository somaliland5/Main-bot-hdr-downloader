import threading
import json
import os
import time
from sub_bot import start_sub_bot
from app import app

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

# ================= START BOT =================
def start_bot(bot_data):
    token = bot_data.get("token")
    owner = bot_data.get("owner")

    if not token:
        return

    if token in running_bots:
        return

    def run():
        try:
            start_sub_bot(token, owner)
        except Exception as e:
            print(f"[BOT ERROR] {token[:8]} -> {e}")

    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

    running_bots[token] = True
    print(f"[STARTED] Bot {token[:8]}")

# ================= WATCH NEW BOTS =================
def watch_bots():
    old_bots = set()

    while True:
        db = load_db()
        bots = db.get("bots", [])

        for bot in bots:
            token = bot.get("token")

            if token not in old_bots and bot.get("status") == "active":
                start_bot(bot)
                old_bots.add(token)

        time.sleep(5)  # check every 5 seconds

# ================= WEB RUN =================
def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ================= MAIN =================
if __name__ == "__main__":

    # web thread
    threading.Thread(target=run_web, daemon=True).start()

    # bot watcher thread
    threading.Thread(target=watch_bots, daemon=True).start()

    print("[SYSTEM STARTED]")
