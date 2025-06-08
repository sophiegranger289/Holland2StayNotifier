import logging
from telegram import Bot
from telegram.utils.request import Request

class TelegramBot:
    def __init__(self, apikey, chat_id):
        self.chat_id = chat_id
        request = Request(con_pool_size=8)
        self.bot = Bot(token=apikey, request=request)

    def send_simple_msg(self, message):
        try:
            response = self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            return response
        except Exception as e:
            logging.error(f"❌ Telegram 消息发送失败: {e}")
            print(f"❌ Telegram 消息发送失败: {e}")
            return None
