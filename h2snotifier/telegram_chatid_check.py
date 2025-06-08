from telegram import Bot
from telegram.utils.request import Request

BOT_TOKEN = "7962285011:AAE2dMl8JyTRjwC5a0pByadcBbLJb431gyA"  # 👈 在这里粘贴你的真实 Bot Token 字符串

def get_chat_ids():
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
