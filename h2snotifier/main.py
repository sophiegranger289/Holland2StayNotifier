import logging
import os
import json
import datetime
import pytz
import gc

from .db import create_table, sync_houses
from .scrape import scrape, house_to_msg
from .telegram_chat import TelegramBot

# Load config and API keys once
CONFIG = None
TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
DEBUGGING_CHAT_ID = os.environ.get("DEBUGGING_CHAT_ID")
DEBUG_TELEGRAM = TelegramBot(apikey=TELEGRAM_API_KEY, chat_id=DEBUGGING_CHAT_ID)

if not TELEGRAM_API_KEY or not DEBUGGING_CHAT_ID:
    raise ValueError("TELEGRAM_API_KEY or DEBUGGING_CHAT_ID not found in environment")

def load_config():
    global CONFIG
    if CONFIG is None:
        with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
            CONFIG = json.load(f)
    return CONFIG

def is_within_run_window():
    tz = pytz.timezone("Europe/Amsterdam")
    now = datetime.datetime.now(tz)
    current_time = now.time()
    weekday = now.weekday()  # Monday is 0
    return weekday < 5 and datetime.time(8, 30) <= current_time <= datetime.time(17, 30)

def scan_and_push():
    if not is_within_run_window():
        print("⏰ 当前不是工作时间（工作日 8:30–17:30），跳过扫描")
        return

    print(">>> 正在扫描房源并推送...")
    config = load_config()
    for gp in config["telegram"]["groups"]:
        cities = gp["cities"]
        chat_id = gp["chat_id"]
        telegram = TelegramBot(apikey=TELEGRAM_API_KEY, chat_id=chat_id)

        houses_in_cities = scrape(cities=cities, apikey=TELEGRAM_API_KEY, debug_chat_id=DEBUGGING_CHAT_ID)
        for city_id, houses in houses_in_cities.items():
            new_houses = sync_houses(city_id=city_id, houses=houses)
            for h in new_houses:
                try:
                    msg = house_to_msg(h)
                    res = telegram.send_simple_msg(msg)
                    logging.info(f"✅ Sent to TG: {h['url_key']}")
                    if res is None:
                        DEBUG_TELEGRAM.send_simple_msg("⚠️ Telegram 发送失败")
                        DEBUG_TELEGRAM.send_simple_msg(msg[:400])
                except Exception as error:
                    DEBUG_TELEGRAM.send_simple_msg(f"❌ 推送出错: {str(error)}")
                    DEBUG_TELEGRAM.send_simple_msg(f"{h}")

    gc.collect()

def main():
    create_table()
    scan_and_push()

if __name__ == "__main__":
    logging.basicConfig(
        filename=os.path.join(os.path.dirname(__file__), "house_sync.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    main()
