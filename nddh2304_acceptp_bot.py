import os
import asyncio
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes
from threading import Thread

app = Flask(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7632520774:AAE2eZL8-2U_n2BE0U6ns52O0nwswZyOUyI"

@app.route('/')
def home():
    return "Bot is running!"

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_join_request = update.chat_join_request
    chat_id = chat_join_request.chat.id
    user_id = chat_join_request.from_user.id
    
    try:
        logger.info(f"Nhận yêu cầu tham gia từ user {user_id} cho chat {chat_id}")
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        logger.info(f"Đã chấp nhận yêu cầu tham gia từ user {user_id}")
    except Exception as e:
        logger.error(f"Lỗi khi xử lý yêu cầu tham gia: {e}")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

async def main():
    try:
        logger.info("Đang khởi động bot...")
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(ChatJoinRequestHandler(handle_join_request))
        logger.info("Bot đã khởi động thành công!")
        await application.run_polling(allowed_updates=['chat_join_request'])
    except Exception as e:
        logger.error(f"Lỗi khởi động bot: {str(e)}", exc_info=True)

if __name__ == '__main__':
    # Chạy Flask trong thread riêng
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Chạy bot trong main thread với event loop
    asyncio.run(main())