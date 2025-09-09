# src/bot/handlers.py
import asyncio
from telethon import events, TelegramClient
from src.services import shortener
from src.utils import message_parser
import config

async def new_message_handler(event: events.NewMessage.Event):
    """
    Xử lý tất cả tin nhắn mới trong kênh chính M.
    Bot sẽ rút gọn link, phản hồi lại kênh, sau đó gửi đi.
    """
    # BƯỚC 1: PHÂN TÍCH TIN NHẮN GỐC (H)
    message_H = event.message
    original_caption = message_H.text or message_H.raw_text

    key, title, long_url = message_parser.parse_admin_message(original_caption)
    
    if not key or not title or not long_url:
        return # Bỏ qua tin nhắn thường
        
    media_to_send = message_H.media
    if not media_to_send:
        print("Bot (P): Tin nhắn không có media. Bỏ qua.")
        return

    print(f"Bot (P): Nhận được yêu cầu hợp lệ. Key: '{key}', Link: '{long_url}'")

    # BƯỚC 2: RÚT GỌN LINK
    print(f"Bot (P): Đang gọi Selenium để rút gọn link...")
    short_link = await shortener.get_short_link(
        long_url=long_url,
        api_url=config.SHORTENER_API_URL,
        api_token=config.SHORTENER_API_TOKEN,
        custom_alias=config.SHORTENER_CUSTOM_ALIAS
    )

    if not short_link:
        print(f"Bot (P): Không thể tạo link rút gọn.")
        await message_H.reply("⚠️ Bot (P) lỗi: Không thể tạo link rút gọn.")
        return

    print(f"Bot (P): Đã tạo link rút gọn thành công: {short_link}")

    # BƯỚC 3: TẠO CAPTION MỚI (NỘI DUNG CỦA Y)
    new_caption = config.MESSAGE_TEMPLATE.format(title=title, short_link=short_link)

    # --- BƯỚC MỚI VÀ QUAN TRỌNG: GỬI TIN NHẮN Y VÀO LẠI KÊNH M ---
    try:
        print(f"Bot (P): Đang gửi tin nhắn đã định dạng (Y) vào lại kênh chính...")
        # Gửi tin nhắn Y dưới dạng trả lời cho tin nhắn gốc H
        await message_H.reply(new_caption)
        print(f"Bot (P): Đã gửi tin nhắn Y thành công.")
    except Exception as e:
        print(f"Bot (P): Lỗi khi gửi tin nhắn Y vào kênh chính: {e}")
    # ----------------------------------------------------------------

    # BƯỚC 4: XÁC ĐỊNH CÁC KÊNH/NHÓM ĐÍCH
    target_ids = []
    if key == '!':
        target_ids = list(config.TARGET_ENTITIES.values())
    else:
        target_keys_str = key.replace('!', '')
        for char_key in target_keys_str:
            if char_key in config.TARGET_ENTITIES:
                target_ids.append(config.TARGET_ENTITIES[char_key])

    if not target_ids:
        await message_H.reply(f"⚠️ Bot (P) lỗi: Key '{key}' không hợp lệ.")
        return

    # BƯỚC 5: GỬI SẢN PHẨM CUỐI CÙNG (MEDIA + CAPTION MỚI) ĐẾN CÁC ĐÍCH
    print(f"Bot (P): Bắt đầu gửi đến {len(target_ids)} đích...")
    sent_count = 0
    for target_id in target_ids:
        try:
            await event.client.send_file(
                entity=target_id,
                file=media_to_send,
                caption=new_caption
            )
            sent_count += 1
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Bot (P): Lỗi khi gửi đến {target_id}: {e}")
            
    # BƯỚC 6: GỬI PHẢN HỒI HOÀN TẤT
    await message_H.reply(f"✅ Bot (P) hoàn tất! Đã gửi thành công đến {sent_count}/{len(target_ids)} kênh/nhóm.")
    print(f"Bot (P): Hoàn tất tác vụ.")


def register_bot_handlers(client: TelegramClient):
    """Đăng ký trình xử lý sự kiện cho bot."""
    client.add_event_handler(
        new_message_handler,
        events.NewMessage(chats=config.MAIN_CHANNEL_ID)
    )