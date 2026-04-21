import threading
import json
import os
from sub_bot import start_sub_bot

# ===== ACTIVE BOT THREADS =====
running_bots = {}

# ===== LOAD DATABASE =====
def load_db():
    if not os.path.exists("database.json"):
        return {"bots": [], "channels": []}
    with open("database.json", "r") as f:
        return json.load(f)

# ===== START SINGLE BOT =====
def start_bot(bot_data):
    token = bot_data["token"]
    owner = bot_data["owner"]

    # prevent duplicate running
    if token in running_bots:
        return

    def run():
        try:
            start_sub_bot(token, owner)
        except Exception as e:
            print(f"[BOT ERROR] {token[:8]} ->", e)

    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

    running_bots[token] = t
    print(f"[STARTED] Bot {token[:8]}")

# ===== STOP BOT =====
def stop_bot(token):
    # Telegram polling cannot be force-killed cleanly
    # so we remove it from active tracking
    if token in running_bots:
        del running_bots[token]
        print(f"[STOPPED] Bot {token[:8]}")

# ===== START ALL ACTIVE BOTS =====
def run_all_bots():
    data = load_db()

    for bot in data["bots"]:
        if bot.get("status") == "active":
            start_bot(bot)

    print("[SYSTEM] All active bots started")
