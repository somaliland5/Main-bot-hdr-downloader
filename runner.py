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

    if not token:
        return

    if token in running_bots:
        return

    stop_flag = {"run": True}

    def run():
        try:
            start_sub_bot(token, owner, stop_flag)
        except Exception as e:
            print(f"[BOT ERROR] {token[:8]} -> {e}")

    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

    running_bots[token] = {
        "thread": t,
        "stop": stop_flag
    }

    print(f"[STARTED] Bot {token[:8]}")

# ================= STOP BOT =================
def stop_bot(token):
    bot = running_bots.get(token)

    if bot:
        bot["stop"]["run"] = False
        running_bots.pop(token, None)

        print(f"[STOPPED] Bot {token[:8]}")

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

                # start active bots
                if status == "active" and token not in running_bots:
                    start_bot(bot)

                # stop inactive bots
                if status != "active":
                    stop_bot(token)

            # remove deleted bots
            for token in list(running_bots.keys()):
                if token not in db_tokens:
                    stop_bot(token)

        except Exception as e:
            print("WATCH ERROR:", e)

        time.sleep(5)

# ================= WEB =================
def run_web():
    print("[WEB STARTING]")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ================= MAIN =================
if __name__ == "__main__":

    print("[SYSTEM BOOTING]")

    threading.Thread(target=run_web, daemon=True).start()
    threading.Thread(target=watch_bots, daemon=True).start()

    print("[SYSTEM RUNNING]")

    while True:
        time.sleep(60)
