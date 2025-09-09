# src/bot/handlers.py
import asyncio
from telethon import events, TelegramClient
import config
# DÒNG SỬA: Chuyển import lên đầu file
from src.utils import message_parser

async def new_forwarding_request_handler(event: events.NewMessage.Event):
    """Handles new messages from the User Client (O) and forwards them."""
    # We only care about replies sent by our designated User Client
    if not event.is_reply or event.sender_id != config.USER_CLIENT_ID:
        return

    print(f"Bot (P): Nhận được yêu cầu điều phối từ Client (O).")

    try:
        # Get the original admin message (H) that the client replied to
        original_message = await event.get_reply_message()
        if not original_message:
            return

        # The new caption is the text of the client's message (Y)
        new_caption = event.text

        # The media is in the original message (H)
        media_file = original_message.media

        if not media_file:
            print("Bot (P): Tin nhắn gốc không chứa media. Bỏ qua.")
            return

        # Get the dispatch key from the original message's caption (H)
        original_caption = original_message.text or original_message.raw_text
        key, _, _ = message_parser.parse_admin_message(original_caption)
        
        if not key:
            print("Bot (P): Không tìm thấy key điều phối trong tin nhắn gốc. Bỏ qua.")
            return

        # Determine target channels
        target_ids = []
        if key == '!':
            # Send to all
            target_ids = list(config.TARGET_ENTITIES.values())
            print(f"Bot (P): Key '!' - Gửi đến tất cả {len(target_ids)} kênh/nhóm.")
        else:
            # Send to specific targets
            target_keys = key.replace('!', '')
            for char_key in target_keys:
                if char_key in config.TARGET_ENTITIES:
                    target_ids.append(config.TARGET_ENTITIES[char_key])
            print(f"Bot (P): Key '{key}' - Gửi đến {len(target_ids)} kênh/nhóm.")

        if not target_ids:
            await event.reply("⚠️ Lỗi: Key điều phối không hợp lệ hoặc không tìm thấy kênh/nhóm tương ứng.")
            return

        # Forward the message
        sent_count = 0
        for target_id in target_ids:
            try:
                await event.client.send_file(
                    entity=target_id,
                    file=media_file,
                    caption=new_caption
                )
                sent_count += 1
                await asyncio.sleep(1) # Small delay to avoid rate limits
            except Exception as e:
                print(f"Bot (P): Lỗi khi gửi đến {target_id}: {e}")

        # Send a confirmation message back to the main channel
        await event.reply(f"✅ Hoàn tất! Đã gửi thành công đến {sent_count}/{len(target_ids)} kênh/nhóm.")

    except Exception as e:
        print(f"Bot (P): Đã xảy ra lỗi nghiêm trọng trong handler: {e}")
        await event.reply(f"❌ Đã có lỗi xảy ra: {e}")


def register_bot_handlers(client: TelegramClient):
    """Registers all event handlers for the bot."""
    # DÒNG SỬA: Xóa các dòng import và globals() không cần thiết ở đây
    client.add_event_handler(
        new_forwarding_request_handler,
        events.NewMessage(chats=config.MAIN_CHANNEL_ID)
    )