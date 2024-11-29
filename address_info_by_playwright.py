import pandas as pd
from playwright.sync_api import sync_playwright

# Đọc danh sách địa điểm từ file CSV
locations_file = "trip_plans_recommend.csv"
output_file = "output/address_info.csv"  # File lưu riêng thông tin địa chỉ

try:
    df_locations = pd.read_csv(locations_file)
    df_locations["full_location"] = df_locations["Địa điểm"] + ", " + df_locations["Tỉnh thành phố"]
    locations = df_locations["full_location"].dropna().tolist()
except Exception as e:
    print(f"Lỗi khi đọc file CSV: {e}")
    locations = []

if not locations:
    print("Không có địa điểm nào trong file CSV.")
    exit()

def scrape_locations(locations):
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Mở trình duyệt không chế độ headless để theo dõi
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

                # Kiểm tra xem có danh sách địa điểm xuất hiện hay không
                has_location_list = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()

                if has_location_list > 0:
                    print(f"Processing location list for '{location}'")
                    page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')
                    page.click('//a[contains(@href, "https://www.google.com/maps/place")]')
                    page.wait_for_load_state('networkidle', timeout=60000)
                else:
                    print(f"No location list for '{location}', processing single result")

                # Lấy thông tin địa chỉ
                try:
                    address = page.locator('//div[contains(@class, "Io6YTe")]').first.inner_text(timeout=10000)
                except Exception:
                    address = "N/A"

                # Lấy tọa độ từ URL
                try:
                    url = page.url
                    coords = url.split("/@")[1].split(",")[:2]
                    latitude = coords[0].strip()
                    longitude = coords[1].strip()
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

    return data

# Gọi hàm và lưu kết quả
result = scrape_locations(locations)

# Tạo DataFrame từ kết quả
df_result = pd.DataFrame(result)

# Ghi kết quả ra file mới
df_result.to_csv(output_file, index=False, encoding="utf-8")
print(f"Kết quả đã được lưu vào '{output_file}'")

# Cập nhật file gốc với thông tin mới
df_locations["address"] = df_locations["Địa điểm"].map(lambda loc: next((r["address"] for r in result if r["location"] == loc), "N/A"))
df_locations["latitude"] = df_locations["Địa điểm"].map(lambda loc: next((r["latitude"] for r in result if r["location"] == loc), "N/A"))
df_locations["longitude"] = df_locations["Địa điểm"].map(lambda loc: next((r["longitude"] for r in result if r["location"] == loc), "N/A"))

# Ghi đè file gốc
df_locations.to_csv(locations_file, index=False, encoding="utf-8")
print(f"File gốc '{locations_file}' đã được cập nhật.")
