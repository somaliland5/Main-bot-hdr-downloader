import threading
import json
from sub_bot import start_sub_bot

def load_db():
    with open("database.json", "r") as f:
        return json.load(f)

def run_all_bots():
    data = load_db()

    for bot_data in data["bots"]:
        if bot_data["status"] == "active":
            t = threading.Thread(
                target=start_sub_bot,
                args=(bot_data["token"], bot_data["owner"])
            )
            t.start()
