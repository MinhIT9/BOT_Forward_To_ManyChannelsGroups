# src/services/google_sheets.py
import gspread
from datetime import datetime, timedelta
import copy
import asyncio
import config # Import config để sử dụng biến thời gian hết hạn

# Biến toàn cục để giữ kết nối và cache
gc = None
sheet = None
link_cache = {}

# Định dạng ngày tháng nhất quán để đọc/ghi vào Sheet
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_date_flexible(date_str: str) -> datetime:
    """
    Cố gắng phân tích một chuỗi ngày tháng với nhiều định dạng khác nhau.
    Đã được nâng cấp để loại bỏ khoảng trắng thừa.
    """
    if not date_str or not isinstance(date_str, str):
        # Trả về now() nếu chuỗi trống hoặc không phải là chuỗi
        return datetime.now()
        
    # NÂNG CẤP: Loại bỏ các khoảng trắng thừa ở đầu và cuối chuỗi
    date_str = date_str.strip()

    # Danh sách các định dạng ngày tháng cần thử
    formats_to_try = [
        "%Y-%m-%d %H:%M:%S",  # Định dạng chuẩn của chúng ta
        "%d/%m/%Y"           # Định dạng phụ phát hiện từ Sheet
    ]
    
    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    print(f"!!! CẢNH BÁO !!!: Không thể phân tích định dạng ngày tháng '{date_str}'. Sử dụng thời gian hiện tại làm dự phòng.")
    return datetime.now()


def connect_to_sheet(sheet_name: str):
    """Kết nối tới Google Sheet bằng file credentials và mở trang tính."""
    global gc, sheet
    if sheet is None:
        try:
            print("Đang kết nối tới Google Sheets API...")
            gc = gspread.service_account(filename='credentials.json')
            sheet = gc.open(sheet_name)
            print("Kết nối Google Sheets thành công.")
            return True
        except Exception as e:
            print(f"LỖI NGHIÊM TRỌNG: Không thể kết nối tới Google Sheets. {e}")
            return False
    return True


def load_cache_from_sheet(is_prod: bool):
    """
    Tải cache từ Sheet, đã thêm log gỡ lỗi tuyệt đối để xem dữ liệu thô.
    """
    global link_cache
    if not sheet: return

    worksheet_name = "Cache_Prod" if is_prod else "Cache_Dev"
    print(f"Đang tải cache từ trang '{worksheet_name}' vào RAM...")
    try:
        cache_worksheet = sheet.worksheet(worksheet_name)
        all_rows = cache_worksheet.get_all_values()
        
        if not all_rows:
            print("Trang tính cache trống.")
            return
            
        header_raw = all_rows[0]
        header = [h.strip() for h in header_raw]
        records = all_rows[1:]
        
        # --- LOG GỠ LỖI TUYỆT ĐỐI ---
        # In ra tiêu đề sau khi đã được làm sạch để kiểm tra
        print("\n[DEBUG] Tiêu đề đã được làm sạch (header):")
        print(header)
        # ---------------------------

        temp_cache = {}
        print("\n--- BẮT ĐẦU QUÁ TRÌNH PHÂN TÍCH CACHE ---")
        for i, row_list in enumerate(records):
            
            # --- LOG GỠ LỖI TUYỆT ĐỐI ---
            # In ra dữ liệu thô của hàng trước khi làm bất cứ điều gì
            print(f"\n[DEBUG] Dữ liệu thô của Dòng {i+2} (row_list):")
            print(row_list)
            # ---------------------------

            row_list.extend([''] * (len(header) - len(row_list)))
            row_dict = dict(zip(header, row_list))
            
            # --- LOG GỠ LỖI TUYỆT ĐỐI ---
            # In ra dictionary sau khi đã được tạo
            print(f"[DEBUG] Dictionary của Dòng {i+2} (row_dict):")
            print(row_dict)
            # ---------------------------

            long_link = row_dict.get('LongLink')
            if not long_link or not long_link.strip():
                # Bỏ qua các dòng trống, nhưng vẫn in ra để ta biết
                print(f" -> Bỏ qua Dòng {i+2} vì không có LongLink.")
                continue
            
            raw_created_at = row_dict.get('createdAt', '')
            raw_last_used_at = row_dict.get('lastUsedAt', '')

            created_at = parse_date_flexible(raw_created_at)

            last_used_at = None
            if raw_last_used_at and raw_last_used_at.strip():
                last_used_at = parse_date_flexible(raw_last_used_at)
            else:
                last_used_at = created_at
            
            print(f" Dòng {i+2}:")
            print(f"   ├─ Raw CreatedAt: '{raw_created_at}' -> Parsed: {created_at.strftime(DATE_FORMAT)}")
            print(f"   ├─ Raw LastUsedAt: '{raw_last_used_at}'")
            print(f"   └─ Final LastUsedAt: {last_used_at.strftime(DATE_FORMAT)}")
            
            temp_cache[long_link] = {
                'shortLink': row_dict.get('ShortLink'),
                'createdAt': created_at,
                'lastUsedAt': last_used_at
            }
        
        print("--- KẾT THÚC QUÁ TRÌNH PHÂN TÍCH CACHE ---\n")
        link_cache = temp_cache
        print(f"Đã tải thành công {len(link_cache)} mục từ cache vào RAM.")
    except Exception as e:
        print(f"Lỗi khi tải cache từ '{worksheet_name}': {e}")



def load_config_from_sheet(is_prod: bool):
    """Tải cấu hình từ trang tính tương ứng với môi trường."""
    if not sheet: return None
    worksheet_name = "Config_Prod" if is_prod else "Config_Dev"
    print(f"Đang tải cấu hình từ trang '{worksheet_name}'...")
    try:
        config_worksheet = sheet.worksheet(worksheet_name)
        records = config_worksheet.get_all_records()
        app_config = {}
        target_entities = {}
        for row in records:
            key = str(row['Key']).strip()
            value = str(row['Value']).strip()
            if key in ["MAIN_CHANNEL_ID", "BOT_TOKEN", "SHORTENER_API_URL", "SHORTENER_API_TOKEN"]:
                app_config[key] = value
            else:
                target_entities[key] = int(value)
        app_config['TARGET_ENTITIES'] = target_entities
        print(f"Tải cấu hình từ '{worksheet_name}' thành công.")
        return app_config
    except Exception as e:
        print(f"Lỗi khi đọc cấu hình từ trang '{worksheet_name}': {e}")
        return None


async def update_last_used_on_sheet_async(long_url: str, is_prod: bool):
    """Tác vụ chạy nền để cập nhật 'LastUsedAt' trên Google Sheet."""
    if not sheet: return
    worksheet_name = "Cache_Prod" if is_prod else "Cache_Dev"
    try:
        print(f"[ASYNC WRITE] Bắt đầu tác vụ nền cập nhật LastUsedAt cho: {long_url[:50]}...")
        cache_worksheet = sheet.worksheet(worksheet_name)
        cell = cache_worksheet.find(long_url, in_column=1)
        if cell:
            now_str = datetime.now().strftime(DATE_FORMAT)
            cache_worksheet.update_cell(cell.row, 4, now_str)
            print(f"[ASYNC WRITE] Cập nhật LastUsedAt trên Sheet thành công.")
        else:
            print(f"[ASYNC WRITE] Cảnh báo: Không tìm thấy dòng để cập nhật LastUsedAt trên Sheet.")
    except Exception as e:
        print(f"[ASYNC WRITE] Lỗi khi cập nhật LastUsedAt trên Sheet: {e}")


def find_short_link_in_cache(long_url: str, is_prod: bool) -> str | None:
    """Tìm link trong cache RAM và kích hoạt tác vụ ghi bất đồng bộ."""
    if long_url in link_cache:
        link_cache[long_url]['lastUsedAt'] = datetime.now()
        short_link = link_cache[long_url]['shortLink']
        print(f"CACHE HIT (from RAM): Tìm thấy link: {short_link}. Đã cập nhật LastUsedAt trong RAM.")
        asyncio.create_task(update_last_used_on_sheet_async(long_url, is_prod))
        return short_link
    else:
        print(f"CACHE MISS (in RAM): Không tìm thấy link.")
        return None


def save_short_link_to_cache(long_url: str, short_link: str, is_prod: bool):
    """Lưu link mới vào RAM và ghi một dòng mới vào Google Sheet."""
    global link_cache
    if not sheet: return
    now = datetime.now()
    link_cache[long_url] = {'shortLink': short_link, 'createdAt': now, 'lastUsedAt': now}
    worksheet_name = "Cache_Prod" if is_prod else "Cache_Dev"
    try:
        cache_worksheet = sheet.worksheet(worksheet_name)
        created_at_str = now.strftime(DATE_FORMAT)
        last_used_at_str = now.strftime(DATE_FORMAT)
        cache_worksheet.append_row([long_url, short_link, created_at_str, last_used_at_str])
        print(f"CACHE WRITE: Đã lưu link mới vào RAM và Google Sheet '{worksheet_name}'.")
    except Exception as e:
        print(f"Lỗi khi lưu vào cache '{worksheet_name}': {e}")


def cleanup_and_save_cache_to_sheet(is_prod: bool):
    """Dọn dẹp cache cũ và ghi toàn bộ cache 'sạch' từ RAM lên Google Sheet."""
    if not sheet: return
    worksheet_name = "Cache_Prod" if is_prod else "Cache_Dev"
    print(f"--- [CLEANUP WORKER] Bắt đầu tác vụ dọn dẹp và lưu cache vào '{worksheet_name}' ---")
    
    cache_snapshot = copy.deepcopy(link_cache)

    expiration_days_ago = datetime.now() - timedelta(days=config.CACHE_EXPIRATION_DAYS)

    fresh_links = {}
    for long, data in cache_snapshot.items():
        if data['lastUsedAt'] > expiration_days_ago:
            fresh_links[long] = data
    
    deleted_count = len(cache_snapshot) - len(fresh_links)
    if deleted_count == 0:
        print(f"[CLEANUP WORKER] Không có link cũ nào cần xóa. Tác vụ hoàn tất.")
        return

    print(f"[CLEANUP WORKER] Dọn dẹp: Sẽ giữ lại {len(fresh_links)} link, xóa {deleted_count} link cũ.")

    # --- SỬA LỖI Ở ĐÂY: DÙNG KEY VIẾT THƯỜNG CHO TIÊU ĐỀ ---
    rows_to_write = [["LongLink", "ShortLink", "createdAt", "lastUsedAt"]]
    # ----------------------------------------------------
    sorted_links = sorted(fresh_links.items(), key=lambda item: item[1]['lastUsedAt'], reverse=True)
    
    for long, data in sorted_links:
        rows_to_write.append([
            long,
            data['shortLink'],
            data['createdAt'].strftime(DATE_FORMAT),
            data['lastUsedAt'].strftime(DATE_FORMAT)
        ])

    try:
        cache_worksheet = sheet.worksheet(worksheet_name)
        cache_worksheet.clear()
        cache_worksheet.update('A1', rows_to_write)
        print(f"[CLEANUP WORKER] Đã lưu thành công {len(rows_to_write) - 1} link vào Google Sheet.")
    except Exception as e:
        print(f"[CLEANUP WORKER] Lỗi nghiêm trọng khi ghi lại cache vào Sheet: {e}")
    
    print(f"--- [CLEANUP WORKER] Hoàn tất tác vụ dọn dẹp ---")