from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes
import logging
import asyncio
import aiohttp

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7632520774:AAE2eZL8-2U_n2BE0U6ns52O0nwswZyOUyI"
RENDER_APP_URL = "https://accept-bot.onrender.com"  # Ví dụ: https://your-app.onrender.com
bot_app = None

async def keep_alive():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await session.get(f'{RENDER_APP_URL}/health')
                logger.info("Keep-alive ping successful")
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Keep-alive error: {e}")
                await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Xóa webhook và các updates cũ
        async with aiohttp.ClientSession() as session:
            await session.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook',
                json={'drop_pending_updates': True}
            )
            await asyncio.sleep(1)
        
        global bot_app
        bot_app = Application.builder().token(BOT_TOKEN).build()
        bot_app.add_handler(ChatJoinRequestHandler(handle_join_request))
        
        # Khởi tạo keep-alive task
        asyncio.create_task(keep_alive())
        
        logger.info("Bot đã khởi động thành công!")
        await bot_app.initialize()
        await bot_app.start()
        
        # Đã xóa tham số stop_signals không hợp lệ
        await bot_app.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=['chat_join_request']
        )
        
        yield
        
    except Exception as e:
        logger.error(f"Lỗi khởi động bot: {e}")
        raise
    finally:
        if bot_app:
            await bot_app.stop()
            await bot_app.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def home():
    return {"status": "Bot is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

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