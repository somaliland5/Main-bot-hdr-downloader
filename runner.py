import threading
import json
import os
from sub_bot import start_sub_bot

# ===== STORE RUNNING BOTS =====
running_bots = {}

# ===== LOAD DATABASE =====
def load_db():
    if not os.path.exists("database.json"):
        return {"bots": []}
    with open("database.json", "r") as f:
        return json.load(f)

# ===== START SINGLE BOT =====
def start_bot(bot_data):
    token = bot_data["token"]
    owner = bot_data["owner"]

    # prevent duplicate run
    if token in running_bots:
        return

    def run():
        try:
            start_sub_bot(token, owner)
        except Exception as e:
            print(f"Bot error ({token[:8]}):", e)

    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

    running_bots[token] = t
    print(f"Started bot: {token[:8]}...")

# ===== STOP BOT =====
def stop_bot(token):
    # Telebot officially ma leh stop → workaround
    if token in running_bots:
        del running_bots[token]
        print(f"Stopped bot: {token[:8]}...")

# ===== RUN ALL BOTS =====
def run_all_bots():
    data = load_db()

    for b in data["bots"]:
        if b.get("status") == "active":
            start_bot(b)
