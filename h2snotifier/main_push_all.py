import logging
import json
import os
from dotenv import dotenv_values

from scrape import scrape, house_to_msg
from telegram_chat import TelegramBot

# 修改后的路径支持：读取项目根目录下的 .env 文件
env = dotenv_values(os.path.join(os.path.dirname(__file__), "..", ".env"))
TELEGRAM_API_KEY = env.get("TELEGRAM_API_KEY")
DEBUGGING_CHAT_ID = env.get("DEBUGGING_CHAT_ID")

debug_telegram = TelegramBot(apikey=TELEGRAM_API_KEY, chat_id=DEBUGGING_CHAT_ID)

def read_config(config_path="config.json"):
    with open(config_path) as f:
        return json.load(f)

def main():
    config = read_config("config.json")
    for gp in config["telegram"]["groups"]:
        cities = gp["cities"]
        chat_id = gp["chat_id"]
        telegram = TelegramBot(apikey=TELEGRAM_API_KEY, chat_id=chat_id)
        houses_in_cities = scrape(cities=cities)

        for city_id, houses in houses_in_cities.items():
            for h in houses:
                try:
                    msg = house_to_msg(h)
                    res = telegram.send_simple_msg(msg)
                    logging.info(f"Sent telegram Notif for {h['url_key']}")
                    if res is None:
                        debug_telegram.send_simple_msg("⚠️ 发送失败（返回 None）")
                        debug_telegram.send_simple_msg(msg[:400])
                except Exception as error:
                    debug_telegram.send_simple_msg(f"❌ 推送失败: {str(error)}")
                    debug_telegram.send_simple_msg(f"{h}")

if __name__ == "__main__":
    main()
