from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7632520774:AAE2eZL8-2U_n2BE0U6ns52O0nwswZyOUyI"
bot_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động
    global bot_app
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(ChatJoinRequestHandler(handle_join_request))
    logger.info("Bot đã khởi động thành công!")
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling(allowed_updates=['chat_join_request'])
    
    yield
    
    # Cleanup
    await bot_app.stop()
    await bot_app.shutdown()

app = FastAPI(lifespan=lifespan)

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)