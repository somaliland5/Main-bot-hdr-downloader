import threading
import json
import os
from sub_bot import start_sub_bot

# ================= ACTIVE BOTS TRACKER =================
running_bots = {}

# ================= SAFE LOAD DB =================
def load_db():
    default = {
        "bots": [],
        "channels": []
    }

    if not os.path.exists("database.json"):
        return default

    try:
        with open("database.json", "r") as f:
            data = json.load(f)
            return {**default, **data}
    except:
        return default

# ================= START SINGLE BOT =================
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

    running_bots[token] = t
    print(f"[STARTED] Bot {token[:8]}")

# ================= STOP BOT =================
def stop_bot(token):
    if token in running_bots:
        del running_bots[token]
        print(f"[STOPPED] Bot {token[:8]}")

# ================= RUN ALL ACTIVE BOTS =================
def run_all_bots():
    db = load_db()

    bots = db.get("bots", [])

    for bot in bots:
        if bot.get("status") == "active":
            start_bot(bot)

    print("[SYSTEM] All bots started successfully")

# ================= AUTO START =================
run_all_bots()
