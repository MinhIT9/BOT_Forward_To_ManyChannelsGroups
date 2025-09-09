# src/client/handlers.py
from telethon import events, TelegramClient
from src.services import shortener
from src.utils import message_parser
import config

async def new_admin_message_handler(event: events.NewMessage.Event):
    """Handles new messages from anyone in the main channel."""
    # DÒNG ĐÃ XÓA: Không còn kiểm tra sender_id nữa
    # if event.sender_id != config.ADMIN_ID:
    #     return

    message_text = event.text or event.raw_text # Use raw_text for captions

    # Parse message to get key, title, and URL
    _, title, long_url = message_parser.parse_admin_message(message_text)

    if not title or not long_url:
        # Không in ra lỗi nữa để tránh spam console, vì tin nhắn thông thường cũng sẽ bị bắt
        return

    print(f"Client (O): Nhận được tin nhắn hợp lệ. Đang xử lý link: {long_url}")

    # Call the shortener service
    short_link = await shortener.get_short_link(
        long_url=long_url,
        api_url=config.SHORTENER_API_URL,
        api_token=config.SHORTENER_API_TOKEN,
        custom_alias=config.SHORTENER_CUSTOM_ALIAS
    )

    if not short_link:
        print(f"Client (O): Không thể tạo link rút gọn. Hủy bỏ tác vụ.")
        await event.reply("⚠️ Lỗi: Không thể tạo link rút gọn. Vui lòng kiểm tra lại API hoặc link gốc.")
        return

    print(f"Client (O): Đã tạo link rút gọn thành công: {short_link}")

    # Format the final message (Y) using the template
    final_message_text = config.MESSAGE_TEMPLATE.format(title=title, short_link=short_link)

    # Send the formatted message as a reply to the original message
    try:
        await event.reply(final_message_text)
        print(f"Client (O): Đã gửi tin nhắn đã định dạng (Y) vào kênh chính.")
    except Exception as e:
        print(f"Client (O): Lỗi khi gửi tin nhắn trả lời: {e}")


def register_client_handlers(client: TelegramClient):
    """Registers all event handlers for the user client."""
    client.add_event_handler(
        new_admin_message_handler,
        events.NewMessage(chats=config.MAIN_CHANNEL_ID)
    )