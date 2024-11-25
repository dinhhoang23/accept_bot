import os
import asyncio
import logging
from flask import Flask
import threading
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes

# Khởi tạo Flask app
app = Flask(__name__)

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cấu hình
BOT_TOKEN = "YOUR_BOT_TOKEN"
ALLOWED_CHATS = []  # Danh sách chat_id được phép, để trống để cho phép tất cả

@app.route('/')
def home():
    return "Bot is running!"

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_join_request = update.chat_join_request
    chat_id = chat_join_request.chat.id
    user_id = chat_join_request.from_user.id
    user_name = chat_join_request.from_user.full_name
    
    try:
        # Kiểm tra xem chat có được phép không
        if ALLOWED_CHATS and chat_id not in ALLOWED_CHATS:
            logger.warning(f"Từ chối yêu cầu từ chat không được phép: {chat_id}")
            return

        logger.info(f"Nhận yêu cầu tham gia từ user {user_name} (ID: {user_id}) cho chat {chat_id}")
        
        # Approve yêu cầu tham gia
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        logger.info(f"Đã chấp nhận yêu cầu tham gia từ user {user_name} (ID: {user_id})")
        
    except Exception as e:
        logger.error(f"Lỗi khi xử lý yêu cầu tham gia: {str(e)}", exc_info=True)

def run_bot():
    try:
        logger.info("Đang khởi động bot...")
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(ChatJoinRequestHandler(handle_join_request))
        logger.info("Bot đã khởi động thành công!")
        application.run_polling(allowed_updates=['chat_join_request'])
    except Exception as e:
        logger.error(f"Lỗi khởi động bot: {str(e)}", exc_info=True)

if __name__ == '__main__':
    # Chạy bot trong thread riêng
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Chạy Flask app
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)