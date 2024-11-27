from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes
import logging
import asyncio
import aiohttp

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cấu hình bot
BOT_TOKEN = "7632520774:AAE2eZL8-2U_n2BE0U6ns52O0nwswZyOUyI"
RENDER_APP_URL = "https://accept-bot.onrender.com"  # Ví dụ: https://your-app.onrender.com
bot_app = None

# Hàm keep-alive để giữ cho ứng dụng luôn hoạt động
async def keep_alive():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await session.get(f'{RENDER_APP_URL}/health')
                logger.info("Keep-alive ping successful")
                await asyncio.sleep(300)  # Ping mỗi 5 phút
            except Exception as e:
                logger.error(f"Keep-alive error: {e}")
                await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động
    global bot_app
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(ChatJoinRequestHandler(handle_join_request))
    
    # Thêm task keep-alive
    asyncio.create_task(keep_alive())
    
    logger.info("Bot đã khởi động thành công!")
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling(allowed_updates=['chat_join_request'])
    
    yield
    
    # Cleanup
    await bot_app.stop()
    await bot_app.shutdown()

# Khởi tạo FastAPI app
app = FastAPI(lifespan=lifespan)

# Route chính
@app.get("/")
async def home():
    return {"status": "Bot is running!"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

# Xử lý yêu cầu tham gia
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

# Chạy ứng dụng
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)