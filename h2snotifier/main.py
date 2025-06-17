import logging
import time
import schedule
import json
import os
from dotenv import dotenv_values

from .db import create_table, sync_houses
from scrape import scrape, house_to_msg
from telegram_chat import TelegramBot

def read_config(config_path=os.path.join(os.path.dirname(__file__), "config.json")):
    with open(config_path) as f:
        return json.load(f)

def scan_and_push(TELEGRAM_API_KEY, DEBUGGING_CHAT_ID):
    print(">>> 正在扫描房源并推送...")
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
                    logging.info(f"✅ Sent to TG: {h['url_key']}")
                    if res is None:
                        debug_telegram.send_simple_msg("⚠️ Telegram 发送失败")
                        debug_telegram.send_simple_msg(msg[:400])
                except Exception as error:
                    debug_telegram.send_simple_msg(f"❌ 推送出错: {str(error)}")
                    debug_telegram.send_simple_msg(f"{h}")

def main():
    env = dotenv_values(os.path.join(os.path.dirname(__file__), ".env"))
    TELEGRAM_API_KEY = env.get("TELEGRAM_API_KEY")
    DEBUGGING_CHAT_ID = env.get("DEBUGGING_CHAT_ID")
    if not TELEGRAM_API_KEY or not DEBUGGING_CHAT_ID:
        raise ValueError("TELEGRAM_API_KEY or DEBUGGING_CHAT_ID not found in .env")
    
    logging.basicConfig(
        filename=os.path.join(os.path.dirname(__file__), "house_sync.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    
    create_table()
    scan_and_push(TELEGRAM_API_KEY, DEBUGGING_CHAT_ID)  # 立即跑一次
    schedule.every(30).seconds.do(lambda: scan_and_push(TELEGRAM_API_KEY, DEBUGGING_CHAT_ID))
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
