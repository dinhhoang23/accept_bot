import os
import asyncio
import logging
from flask import Flask
import threading
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes

app = Flask(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "YOUR_BOT_TOKEN"

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

async def run_bot():
    try:
        logger.info("Đang khởi động bot...")
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(ChatJoinRequestHandler(handle_join_request))
        logger.info("Bot đã khởi động thành công!")
        await application.run_polling(allowed_updates=['chat_join_request'])
    except Exception as e:
        logger.error(f"Lỗi khởi động bot: {str(e)}", exc_info=True)

def run_bot_forever():
    asyncio.run(run_bot())

if __name__ == '__main__':
    # Chạy bot trong thread riêng
    bot_thread = threading.Thread(target=run_bot_forever)
    bot_thread.start()
    
    # Chạy Flask app
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)