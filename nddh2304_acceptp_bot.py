import asyncio
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes

BOT_TOKEN = "7632520774:AAE2eZL8-2U_n2BE0U6ns52O0nwswZyOUyI"

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_join_request = update.chat_join_request
    chat_id = chat_join_request.chat.id
    user_id = chat_join_request.from_user.id
    
    try:
        # Xử lý yêu cầu mới
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
    except Exception:
        pass

async def approve_pending_requests(bot):
    # Hàm này sẽ chạy khi bot khởi động để xử lý các yêu cầu cũ
    try:
        # Lấy danh sách yêu cầu đang chờ
        pending_requests = await bot.get_chat_join_requests()
        for request in pending_requests:
            await bot.approve_chat_join_request(
                chat_id=request.chat.id,
                user_id=request.from_user.id
            )
    except Exception:
        pass

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Thêm handler cho yêu cầu mới
    application.add_handler(ChatJoinRequestHandler(handle_join_request))
    
    # Chạy hàm xử lý yêu cầu cũ khi khởi động
    asyncio.create_task(approve_pending_requests(application.bot))
    
    application.run_polling(allowed_updates=['chat_join_request'])

if __name__ == '__main__':
    run_bot()
