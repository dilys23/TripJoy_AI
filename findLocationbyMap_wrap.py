from playwright.sync_api import sync_playwright
import pandas as pd

# Đọc danh sách địa điểm từ file CSV
locations_file = "trip_plans_recommend.csv"
try:
    df_locations = pd.read_csv(locations_file)
    locations = df_locations["Địa điểm"].dropna().tolist()  # Loại bỏ giá trị NaN hoặc trống
except Exception as e:
    print(f"Lỗi khi đọc file CSV: {e}")
    locations = []

# Kiểm tra nếu danh sách địa điểm rỗng
if not locations:
    print("Không có địa điểm nào trong file CSV.")
    exit()

data = []

# Bắt đầu Playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Mở trình duyệt không chế độ headless để theo dõi
    page = browser.new_page()

    for location in locations:
        try:
            # Mở Google Maps
            page.goto("https://maps.google.com", timeout=60000)
            
            # Nhập địa điểm vào ô tìm kiếm
            search_box = page.locator('//input[@id="searchboxinput"]')
            search_box.fill(location)
            page.press('//input[@id="searchboxinput"]', 'Enter')
            
            # Chờ trang tải
            page.wait_for_load_state('networkidle', timeout=60000)
            
            # Lấy thông tin địa chỉ
            try:
                address = page.locator('//div[contains(@class, "Io6YTe")]').first.inner_text(timeout=10000)
            except Exception:
                address = "N/A"
            
            # Lấy tọa độ từ URL
            try:
                url = page.url
                coords = url.split("/@")[1].split(",")[:2]  # Lấy phần latitude và longitude từ URL
                latitude = coords[0]
                longitude = coords[1]
            except Exception:
                latitude = "N/A"
                longitude = "N/A"
            
            # Lưu kết quả
            data.append({
                "location": location,
                "address": address,
                "latitude": latitude,
                "longitude": longitude
            })
            print(f"Processed: {location}")
        
        except Exception as e:
            print(f"Failed to process location '{location}': {e}")
            data.append({
                "location": location,
                "address": "Error",
                "latitude": "Error",
                "longitude": "Error"
            })
    
    browser.close()

# Lưu dữ liệu ra file
output_file = "locations_with_addresses_and_coords.xlsx"
try:
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)
    print(f"Done! Data saved to {output_file}")
except Exception as e:
    print(f"Lỗi khi lưu file: {e}")
