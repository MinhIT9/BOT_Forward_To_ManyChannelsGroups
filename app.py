# app.py
import asyncio
from telethon import TelegramClient
import config
from src.client.handlers import register_client_handlers
from src.bot.handlers import register_bot_handlers
# Dòng import mới
from src.services.shortener import init_browser, close_browser

async def main():
    """
    Initializes and runs both the user client and the bot client.
    """
    # Khởi tạo trình duyệt Selenium trước khi làm mọi thứ khác
    init_browser()

    # Initialize User Client (O)
    user_client = TelegramClient(
        session=config.SESSION_NAME_USER,
        api_id=config.API_ID,
        api_hash=config.API_HASH
    )

    # Initialize Bot (P)
    bot_client = TelegramClient(
        session='bot_session',
        api_id=config.API_ID,
        api_hash=config.API_HASH
    )

    print("Bắt đầu chạy User Client (O)...")
    await user_client.start()
    print("User Client (O) đã chạy.")
    
    me = await user_client.get_me()
    config.USER_CLIENT_ID = me.id
    print(f"User Client (O) đã đăng nhập với tài khoản ID: {config.USER_CLIENT_ID}")
    
    print("Bắt đầu chạy Bot (P)...")
    await bot_client.start(bot_token=config.BOT_TOKEN)
    print("Bot (P) đã chạy.")
    
    print("Đăng ký các trình xử lý sự kiện (handlers)...")
    register_client_handlers(user_client)
    register_bot_handlers(bot_client)

    print("="*20)
    print("HỆ THỐNG ĐÃ SẴN SÀNG!")
    print("="*20)

    # Chạy đồng thời cả hai client
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Đã dừng chương trình.")
    finally:
        # Dòng mới: Đảm bảo trình duyệt luôn được đóng khi chương trình kết thúc
        close_browser()