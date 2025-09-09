# config.py

# --- CÀI ĐẶT MÔI TRƯỜNG ---
IS_PROD = False

# --- CÀI ĐẶT TELETHON CỐ ĐỊNH ---
API_ID = 21303563
API_HASH = "6ad9d81fb1c8e246de8255d7ecc449f5"

# --- BIẾN TẠM THỜI ---
USER_CLIENT_ID = None


# --- CẤU HÌNH THEO TỪNG MÔI TRƯỜNG ---
if IS_PROD:
    # ==================================
    # === CẤU HÌNH PRODUCTION (THẬT) ===
    # ==================================
    print(">>> CHẠY Ở MÔI TRƯỜNG PRODUCTION <<<")
    
    SESSION_NAME_USER = "prod_user"
    BOT_TOKEN = 'your_production_bot_token' # THAY BẰNG TOKEN BOT THẬT
    
    MAIN_CHANNEL_ID = -1001234567890 # THAY BẰNG ID CHANNEL CHÍNH (THẬT)
    
    TARGET_ENTITIES = { 'A': -100111111111, 'B': -100222222222 }
    
    # --- THAY ĐỔI MỚI ---
    # Gộp thành 1 link duy nhất, kết thúc bằng &url=
    SHORTENER_QUICK_LINK = "https://vuotlink.vip/st?api=f6918c1748d0d50744ea2a417d03158370a55222&url="
    SHORTENER_CUSTOM_ALIAS = ""

else:
    # ====================================
    # === CẤU HÌNH DEVELOPMENT (TEST) ===
    # ====================================
    print(">>> CHẠY Ở MÔI TRƯỜNG DEVELOPMENT <<<")

    SESSION_NAME_USER = "dev_user"
    BOT_TOKEN = '7104369638:AAHJzGrYskAC9eEzE7M_ETs0Ga5hwttW--M' # THAY BẰNG TOKEN BOT TEST @BotMonChu TIenNu
    
    MAIN_CHANNEL_ID = -1002049708646 # THAY BẰNG ID CHANNEL TEST CỦA BẠN
    
    TARGET_ENTITIES = {
        'A': -1002046713701,  # Channel 1
        'B': -1002043853417,  # Channel 2
        'D': -1002042025957,  # Group 1
        'E': -1002036681213,  # Group 2
        # ...thêm các kênh/nhóm test khác ở đây
    }

    # --- THAY ĐỔI MỚI ---
    # Gộp thành 1 link duy nhất, kết thúc bằng &url=
    SHORTENER_QUICK_LINK = "https://vuotlink.vip/st?api=f6918c1748d0d50744ea2a417d03158370a55222&url="
    SHORTENER_CUSTOM_ALIAS = "test"

# --- MẪU TIN NHẮN ---
MESSAGE_TEMPLATE = """{title}

🎯 Vào Xem Clip Ngay:
{short_link}

⚠️ Hướng Dẫn: Xem Tại Đây (https://t.me/CachVaoNhomVN)
✅ Nhóm VIP: Vào Đây Nè (https://t.me/+2EX6KU5deYMxZDQ1) 
💕 Tổng Hợp Link HOT Ko Lỗi (https://t.me/+NYV3Hkwta3kyYmU1)
"""