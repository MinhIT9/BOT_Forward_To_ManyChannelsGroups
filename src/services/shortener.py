# src/services/shortener.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from urllib.parse import urlencode
import asyncio
import time

# Import các hàm từ module google_sheets và import config để lấy cờ IS_PROD
from src.services.google_sheets import find_short_link_in_cache, save_short_link_to_cache
import config

# Biến toàn cục để giữ instance của trình duyệt
driver = None

def init_browser():
    """Khởi tạo trình duyệt Chrome với Selenium."""
    global driver
    if driver is None:
        print("Đang khởi tạo trình duyệt Selenium (lần đầu)...")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("Trình duyệt Selenium đã sẵn sàng.")
        except Exception as e:
            print(f"LỖI NGHIÊM TRỌNG: Không thể khởi tạo Chrome. Hãy chắc chắn bạn đã cài đặt Google Chrome.")
            print(f"Chi tiết lỗi: {e}")
            driver = None

def close_browser():
    """Đóng trình duyệt Selenium khi chương trình kết thúc."""
    global driver
    if driver:
        print("Đang đóng trình duyệt Selenium...")
        driver.quit()
        driver = None

async def get_short_link(long_url: str, api_url: str, api_token: str, custom_alias: str = "") -> str | None:
    """
    Hàm chính để lấy link rút gọn.
    Nó sẽ kiểm tra cache trước, nếu không có mới gọi Selenium.
    """
    # --- DÒNG ĐÃ SỬA ---
    # Thêm lại tham số config.IS_PROD bị thiếu khi gọi hàm
    cached_link = find_short_link_in_cache(long_url, config.IS_PROD)
    # -------------------
    
    if cached_link:
        return cached_link

    print("Không có trong cache, bắt đầu quy trình Selenium...")
    new_short_link = await asyncio.to_thread(
        get_short_link_sync, long_url, api_url, api_token, custom_alias
    )

    if new_short_link:
        save_short_link_to_cache(long_url, new_short_link, config.IS_PROD)

    return new_short_link

def get_short_link_sync(long_url: str, api_url: str, api_token: str, custom_alias: str = "") -> str | None:
    """
    Hàm đồng bộ (sync) thực hiện công việc nặng nhọc với Selenium.
    """
    if not driver:
        print("Lỗi: Trình duyệt Selenium chưa được khởi tạo.")
        return None
        
    params = {'api': api_token, 'url': long_url}
    if custom_alias:
        params['alias'] = custom_alias

    initial_url = f"{api_url}?{urlencode(params)}"
    print(f"Đang truy cập URL (với Selenium): {initial_url}")

    try:
        driver.get(initial_url)
        time.sleep(7)
        
        final_url = driver.current_url

        if final_url and final_url != initial_url and "st?" not in final_url:
            print(f"Lấy link rút gọn thành công: {final_url}")
            return final_url
        else:
            print(f"Lỗi API: Trang không chuyển hướng. URL cuối cùng vẫn là: {final_url}")
            try:
                page_content = driver.find_element(By.TAG_NAME, 'body').text
                print(f"Nội dung trang: {page_content[:200]}...")
            except Exception as find_error:
                print(f"Không thể lấy nội dung trang để gỡ lỗi: {find_error}")
            return None
            
    except Exception as e:
        print(f"Lỗi trong quá trình Selenium hoạt động: {e}")
        return None