from fastapi import FastAPI
import uvicorn
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes
import asyncio
import logging

app = FastAPI()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7632520774:AAE2eZL8-2U_n2BE0U6ns52O0nwswZyOUyI"

@app.get("/")
async def home():
    return {"status": "Bot is running!"}

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

@app.on_event("startup")
async def startup():
    try:
        app.bot_application = Application.builder().token(BOT_TOKEN).build()
        app.bot_application.add_handler(ChatJoinRequestHandler(handle_join_request))
        logger.info("Bot đã khởi động thành công!")
        asyncio.create_task(app.bot_application.run_polling(allowed_updates=['chat_join_request']))
    except Exception as e:
        logger.error(f"Lỗi khởi động bot: {str(e)}", exc_info=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)