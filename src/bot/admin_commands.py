# src/bot/admin_commands.py
import asyncio
from telethon import events, TelegramClient
# --- DÒNG IMPORT MỚI ---
# Di chuyển import lên đầu file để tất cả các hàm đều có thể sử dụng
from telethon.tl import functions
from src.services import google_sheets
import config

async def update_targets_command_handler(event: events.NewMessage.Event):
    """
    Xử lý lệnh /updateTargets. Tự động lấy tên và link mời của các
    kênh/nhóm đích rồi cập nhật vào Google Sheet.
    """
    print("[ADMIN COMMAND] Nhận được lệnh /updateTargets.")
    
    try:
        status_message = await event.reply("⏳ Bắt đầu quá trình cập nhật, vui lòng chờ...")
    except Exception as e:
        print(f"[ADMIN COMMAND] Lỗi khi gửi tin nhắn trạng thái: {e}")
        return

    try:
        print("[ADMIN COMMAND] Đang đọc dữ liệu hiện tại từ Google Sheet...")
        all_config_data = google_sheets.get_full_config(config.IS_PROD)
        if not all_config_data:
            await status_message.edit("❌ Lỗi: Không thể đọc dữ liệu cấu hình từ Google Sheet.")
            return
            
        updated_targets = {}
        target_entities = config.TARGET_ENTITIES
        
        print(f"[ADMIN COMMAND] Bắt đầu lấy thông tin cho {len(target_entities)} target...")
        for key, target_id in target_entities.items():
            current_data = all_config_data.get(key, {})
            name = "N/A"
            link = current_data.get("InviteLink", None)

            try:
                entity = await event.client.get_entity(target_id)
                name = entity.title
                
                if not link:
                    print(f"   -> {key}: Chưa có link mời, đang tạo mới...")
                    result = await event.client(
                        functions.messages.ExportChatInviteRequest(peer=entity)
                    )
                    link = result.link
                    print(f"   -> {key}: Đã tạo link mới: {link}")

                updated_targets[key] = {'Name': name, 'InviteLink': link}
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"[ADMIN COMMAND] Lỗi khi xử lý target '{key}' (ID: {target_id}): {e}")
                updated_targets[key] = {'Name': 'Lỗi khi lấy tên', 'InviteLink': 'Lỗi'}

        print("[ADMIN COMMAND] Đang cập nhật dữ liệu hàng loạt lên Google Sheet...")
        success = google_sheets.batch_update_target_info(updated_targets, config.IS_PROD)
        
        if not success:
            await status_message.edit("❌ Lỗi: Không thể cập nhật dữ liệu lên Google Sheet.")
            return

        # --- PHẦN THAY ĐỔI ĐỊNH DẠNG BÁO CÁO ---
        report_lines = ["✅ Cập nhật thông tin kênh/nhóm thành công!\n"]
        for key, data in updated_targets.items():
            # Xây dựng dòng mới với cú pháp hyperlink Markdown
            # [LINK](URL)
            link_markdown = f"[LINK]({data['InviteLink']})"
            report_lines.append(f"{key} - {link_markdown} - {data['Name']}")
        # --------------------------------------------
        
        final_report = "\n".join(report_lines)
        # Giữ nguyên parse_mode='md' để Telegram hiểu được cú pháp hyperlink
        await status_message.edit(final_report, parse_mode='md')
        print("[ADMIN COMMAND] Hoàn tất tác vụ.")

    except Exception as e:
        print(f"[ADMIN COMMAND] Lỗi nghiêm trọng trong quá trình xử lý: {e}")
        await status_message.edit(f"❌ Đã xảy ra lỗi nghiêm trọng: {e}")



def register_admin_commands(client: TelegramClient):
    """Đăng ký các handler cho lệnh quản trị."""
    # --- DÒNG ĐÃ XÓA ---
    # Không cần import ở đây nữa
    
    client.add_event_handler(
        update_targets_command_handler,
        events.NewMessage(pattern='/updateTargets', chats=config.MAIN_CHANNEL_ID)
    )