# app.py
import asyncio
from telethon import TelegramClient
import config
from src.services.shortener import init_browser, close_browser
# Bỏ import sync_ram_cache_to_sheet vì không còn cần thiết
from src.services.google_sheets import cleanup_and_save_cache_to_sheet
from src.bot.handlers import register_bot_handlers
from src.bot.admin_commands import register_admin_commands


# -----------------------------------------------------------------------------
# --- ĐỊNH NGHĨA "CON BOT DỌN DẸP" (CLEANUP WORKER) ---
# -----------------------------------------------------------------------------
async def cleanup_worker():
    """
    Một vòng lặp chạy nền để dọn dẹp cache định kỳ.
    Nó sẽ chạy ngay một lần khi khởi động, sau đó lặp lại.
    """
    print(f"[CLEANUP WORKER] Đã khởi động. Chuẩn bị chạy lần đầu tiên...")
    
    interval_seconds = config.CLEANUP_INTERVAL_HOURS * 3600
    
    while True:
        # Chạy tác vụ dọn dẹp
        await asyncio.to_thread(cleanup_and_save_cache_to_sheet, config.IS_PROD)
        
        # Ngủ trong khoảng thời gian đã định cho đến lần chạy tiếp theo
        print(f"[CLEANUP WORKER] Tác vụ hoàn tất. Sẽ chạy lại sau {config.CLEANUP_INTERVAL_HOURS} giờ.")
        await asyncio.sleep(interval_seconds)
# -----------------------------------------------------------------------------

async def main():
    """Khởi tạo và chạy đồng thời cả bot chính và worker dọn dẹp."""
    init_browser()

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
    register_admin_commands(bot_client) # Đăng ký handler xử lý lệnh admin


    # Khởi chạy Cleanup Worker sau một khoảng trễ nhỏ
    print("Chờ 10 giây trước khi khởi động Worker dọn dẹp...")
    await asyncio.sleep(10)
    cleanup_task = asyncio.create_task(cleanup_worker())

    print("="*20)
    print("HỆ THỐNG ĐÃ SẴN SÀNG! (Bao gồm Bot chính và Worker dọn dẹp)")
    print("="*20)

    # Chạy đồng thời bot và worker dọn dẹp
    await asyncio.gather(
        bot_client.run_until_disconnected(),
        cleanup_task
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nĐã nhận tín hiệu dừng chương trình (Ctrl+C)...")
    finally:
        # Khi tắt, chúng ta không cần chạy sync lần cuối vì các cập nhật
        # đã được ghi bất đồng bộ, và worker dọn dẹp đã chạy định kỳ.
        close_browser()
        print("Đã tắt chương trình thành công.")