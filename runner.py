import threading
import json
import os
import time
from sub_bot import start_sub_bot
from app import app

# ================= RUNNING BOTS =================
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
    except Exception as e:
        print("DB LOAD ERROR:", e)
        return default

# ================= START BOT =================
def start_bot(bot_data):
    token = bot_data.get("token")
    owner = bot_data.get("owner")

    print("TRY START BOT:", token)

    if not token:
        print("NO TOKEN")
        return

    if token in running_bots:
        print("ALREADY RUNNING")
        return

    def run():
        try:
            print("CALLING SUB BOT...")
            start_sub_bot(token, owner)
        except Exception as e:
            print(f"[BOT CRASHED] {e}")

    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

    running_bots[token] = True

# ================= STOP BOT =================
def stop_removed_bots(db_tokens):
    current_tokens = set(running_bots.keys())

    for token in current_tokens:
        if token not in db_tokens:
            print(f"[REMOVED BOT] {token[:8]}")
            running_bots.pop(token, None)

# ================= WATCH SYSTEM =================
def watch_bots():
    print("[WATCHER STARTED]")

    while True:
        try:
            db = load_db()
            bots = db.get("bots", [])

            db_tokens = set()

            for bot in bots:
                token = bot.get("token")
                status = bot.get("status")

                if not token:
                    continue

                db_tokens.add(token)

                # start only active bots
                if status == "active" and token not in running_bots:
                    start_bot(bot)

            # remove deleted bots
            stop_removed_bots(db_tokens)

        except Exception as e:
            print("WATCH ERROR:", e)

        time.sleep(5)  # check every 5 seconds

# ================= WEB =================
def run_web():
    try:
        print("[WEB STARTING]")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    except Exception as e:
        print("WEB ERROR:", e)

# ================= MAIN =================
if __name__ == "__main__":

    print("[SYSTEM BOOTING]")

    # start web
    threading.Thread(target=run_web, daemon=True).start()

    # start watcher
    threading.Thread(target=watch_bots, daemon=True).start()

    print("[SYSTEM RUNNING]")

    # keep alive
    while True:
        time.sleep(60)
