import logging
import time
import schedule
import json
import os
import gc
import datetime
import pytz

from .db import create_table, sync_houses, mark_as_pushed
from .scrape import scrape, house_to_msg
from .telegram_chat import TelegramBot

# 新增：用于计数
scan_counter = 0
SCAN_LIMIT = 350  # 每300次重启一次

def read_config(config_path=os.path.join(os.path.dirname(__file__), "config.json")):
    with open(config_path) as f:
        return json.load(f)

def is_within_run_window():
    tz = pytz.timezone("Europe/Amsterdam")  # 欧洲中部时间
    now = datetime.datetime.now(tz)
    current_time = now.time()
    weekday = now.weekday()  # Monday is 0, Sunday is 6
    return weekday < 5 and datetime.time(8, 30) <= current_time <= datetime.time(17, 30)

def scan_and_push(TELEGRAM_API_KEY, DEBUGGING_CHAT_ID):
    global scan_counter
    if not is_within_run_window():
        print("⏰ 当前不是工作时间（工作日 8:30–17:30），跳过扫描")
        return

    print(f">>> 第 {scan_counter+1} 次扫描房源并推送...")
    debug_telegram = TelegramBot(apikey=TELEGRAM_API_KEY, chat_id=DEBUGGING_CHAT_ID)
    config = read_config()

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
                    if res is not None:
                        mark_as_pushed(h["url_key"])  # ✅ 标记已推送
                        logging.info(f"✅ Sent to TG: {h['url_key']}")
                    else:
                        debug_telegram.send_simple_msg("⚠️ Telegram 发送失败")
                        debug_telegram.send_simple_msg(msg[:400])
                except Exception as error:
                    logging.error(f"❌ 推送出错: {str(error)}")
                    debug_telegram.send_simple_msg(f"❌ 推送出错: {str(error)}")
                    debug_telegram.send_simple_msg(f"{h}")

        del houses_in_cities
        gc.collect()

    scan_counter += 1
    if scan_counter >= SCAN_LIMIT:
        print("🔁 已达到扫描次数上限，准备重启程序...")
        os._exit(0)

def main():
    TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
    DEBUGGING_CHAT_ID = os.environ.get("DEBUGGING_CHAT_ID")
    if not TELEGRAM_API_KEY or not DEBUGGING_CHAT_ID:
        raise ValueError("TELEGRAM_API_KEY or DEBUGGING_CHAT_ID not found in .env")

    logging.basicConfig(
        filename=os.path.join(os.path.dirname(__file__), "house_sync.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    create_table()
    scan_and_push(TELEGRAM_API_KEY, DEBUGGING_CHAT_ID)  # 立即跑一次
    schedule.every(3).seconds.do(lambda: scan_and_push(TELEGRAM_API_KEY, DEBUGGING_CHAT_ID))
    while True:
        schedule.run_pending()
        time.sleep(1)
