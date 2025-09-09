# app.py
import asyncio
from telethon import TelegramClient
import config
from src.services.shortener import init_browser, close_browser
from src.bot.handlers import register_bot_handlers

async def main():
    """
    Khởi tạo và chạy bot xử lý chính.
    """
    init_browser()

    # Khởi tạo Bot (P)
    bot_client = TelegramClient(
        session='bot_session',
        api_id=config.API_ID,
        api_hash=config.API_HASH
    )

    print("Bắt đầu chạy Bot (P)...")
    await bot_client.start(bot_token=config.BOT_TOKEN)
    print("Bot (P) đã chạy.")
    
    bot_me = await bot_client.get_me()
    print(f"Bot (P) đã đăng nhập với tài khoản: @{bot_me.username}")
    
    print("Đăng ký trình xử lý sự kiện (handler)...")
    register_bot_handlers(bot_client)

    print("="*20)
    print("HỆ THỐNG ĐÃ SẴN SÀNG!")
    print("="*20)

    await bot_client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Đã dừng chương trình.")
    finally:
        close_browser()