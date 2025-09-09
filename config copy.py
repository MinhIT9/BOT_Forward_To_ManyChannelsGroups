# config.py

# --- CÀI ĐẶT MÔI TRƯỜNG ---
# True: Chạy với cấu hình Production (dữ liệu thật).
# False: Chạy với cấu hình Development (dữ liệu test).
IS_PROD = False

# --- CÀI ĐẶT TELETHON CỐ ĐỊNH ---
# Lấy từ https://my.telegram.org
API_ID = 21303563
API_HASH = "6ad9d81fb1c8e246de8255d7ecc449f5"

# --- BIẾN TẠM THỜI ---
# ID của User Client sẽ được tự động điền vào đây khi chương trình khởi chạy.
# Không cần thay đổi giá trị này.
USER_CLIENT_ID = None


# --- CẤU HÌNH THEO TỪNG MÔI TRƯỜNG ---
if IS_PROD:
    # ==================================
    # === CẤU HÌNH PRODUCTION (THẬT) ===
    # ==================================
    print(">>> CHẠY Ở MÔI TRƯỜNG PRODUCTION <<<")
    
    SESSION_NAME_USER = "prod_user"  # Sẽ tạo file prod_user.session
    BOT_TOKEN = 'your_production_bot_token' # THAY BẰNG TOKEN BOT THẬT
    
    MAIN_CHANNEL_ID = -1001234567890 # THAY BẰNG ID CHANNEL CHÍNH (THẬT)
    
    TARGET_ENTITIES = {
        'A': -100111111111,  # ID Channel/Group thật
        'B': -100222222222,
        # ...thêm các kênh/nhóm thật khác ở đây
    }
    
    # Cấu hình API rút gọn link cho Production
    SHORTENER_API_URL = "https://vuotlink.vip/api/api"
    SHORTENER_API_TOKEN = "f6918c1748d0d50744ea2a417d03158370a55222"
    SHORTENER_CUSTOM_ALIAS = ""

else:
    # ====================================
    # === CẤU HÌNH DEVELOPMENT (TEST) ===
    # ====================================
    print(">>> CHẠY Ở MÔI TRƯỜNG DEVELOPMENT <<<")

    SESSION_NAME_USER = "dev_user"  # Sẽ tạo file dev_user.session riêng biệt
    BOT_TOKEN = '7104369638:AAHJzGrYskAC9eEzE7M_ETs0Ga5hwttW--M' # THAY BẰNG TOKEN BOT TEST @BotMonChu TIenNu
    
    MAIN_CHANNEL_ID = -1002049708646 # THAY BẰNG ID CHANNEL TEST CỦA BẠN
    
    TARGET_ENTITIES = {
        'A': -100999999999,  # ID Channel/Group dùng để test
        'B': -100888888888,
        # ...thêm các kênh/nhóm test khác ở đây
    }

    # Cấu hình API rút gọn link cho Development
    SHORTENER_API_URL = "https://vuotlink.vip/st"
    SHORTENER_API_TOKEN = "f6918c1748d0d50744ea2a417d03158370a55222"
    SHORTENER_CUSTOM_ALIAS = "test" # Thêm alias để phân biệt link test

# --- MẪU TIN NHẮN (Dùng chung cho cả hai môi trường) ---
MESSAGE_TEMPLATE = """{title}

🎯 Vào Xem Clip Ngay:
{short_link}

⚠️ Hướng Dẫn: Xem Tại Đây (https://t.me/CachVaoNhomVN)
✅ Nhóm VIP: Vào Đây Nè (https://t.me/+2EX6KU5deYMxZDQ1) 
💕 Tổng Hợp Link HOT Ko Lỗi (https://t.me/+NYV3Hkwta3kyYmU1)
"""