# config.py
from src.services.google_sheets import connect_to_sheet, load_config_from_sheet, load_cache_from_sheet
import sys

# --- CÁC BIẾN CỐ ĐỊNH ---
# >>> ĐÂY LÀ NÚT ĐIỀU KHIỂN DUY NHẤT CỦA BẠN <<<
IS_PROD = False

API_ID = 21303563
API_HASH = "6ad9d81fb1c8e246de8255d7ecc449f5"
GOOGLE_SHEET_NAME = "BotConfig" # THAY BẰNG TÊN GOOGLE SHEET CỦA BẠN

# --- CẤU HÌNH DÙNG CHUNG CHO CẢ 2 MÔI TRƯỜNG ---
# Thời gian giữa các lần dọn dẹp tự động, tính bằng giờ.
CLEANUP_INTERVAL_HOURS = 48
# --- BIẾN MỚI ---
# Số ngày một link được coi là cũ nếu không được sử dụng.
CACHE_EXPIRATION_DAYS = 30


# --- BIẾN TẠM THỜI ---
USER_CLIENT_ID = None

# --- TẢI CẤU HÌNH VÀ CACHE KHI KHỞI ĐỘNG ---
if not connect_to_sheet(GOOGLE_SHEET_NAME):
    sys.exit("Không thể tiếp tục vì không kết nối được Google Sheet.")

sheet_config = load_config_from_sheet(IS_PROD)
if not sheet_config:
    sys.exit("Không thể tiếp tục vì không tải được cấu hình từ Google Sheet.")

load_cache_from_sheet(IS_PROD)


# --- GÁN CÁC BIẾN CẤU HÌNH ĐỂ CÁC FILE KHÁC SỬ DỤNG ---
MAIN_CHANNEL_ID = int(sheet_config.get("MAIN_CHANNEL_ID"))
BOT_TOKEN = sheet_config.get("BOT_TOKEN")
SHORTENER_API_URL = sheet_config.get("SHORTENER_API_URL")
SHORTENER_API_TOKEN = sheet_config.get("SHORTENER_API_TOKEN")
TARGET_ENTITIES = sheet_config.get("TARGET_ENTITIES", {})

SESSION_NAME_USER = "prod_user" if IS_PROD else "dev_user"
SHORTENER_CUSTOM_ALIAS = "" if IS_PROD else "test"


# --- MẪU TIN NHẮN ---
MESSAGE_TEMPLATE = """{title}

🎯 Vào Xem Clip Ngay:
{short_link}

⚠️ Hướng Dẫn: Xem Tại Đây (https://t.me/CachVaoNhomVN)
✅ Nhóm VIP: Vào Đây Nè (https://t.me/+2EX6KU5deYMxZDQ1) 
💕 Tổng Hợp Link HOT Ko Lỗi (https://t.me/+NYV3Hkwta3kyYmU1)
"""