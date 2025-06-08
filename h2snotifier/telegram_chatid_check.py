import os
from telegram import Bot
from telegram.utils.request import Request
from dotenv import load_dotenv

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # 在运行前请替换为您从 @BotFather 获取的 Token

def get_chat_ids():
    """
    使用说明：
    1. 从 @BotFather 获取您的 Bot Token
    2. 将上面的 YOUR_BOT_TOKEN_HERE 替换为您的 Token
    3. 运行此脚本
    4. 在您想要监控的群组中发送任意消息
    5. 查看输出的 Chat ID，将其添加到 config.json 中
    """
    bot = Bot(token=BOT_TOKEN, request=Request(con_pool_size=8))
    updates = bot.get_updates()

    for update in updates:
        if update.message:
            print("✅ Chat Title:", update.message.chat.title)
            print("🆔 Chat ID:", update.message.chat.id)
            print("👤 Sender:", update.message.from_user.full_name)
            print("💬 Text:", update.message.text)
            print("-" * 40)

if __name__ == "__main__":
    get_chat_ids()
