import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep

# Đọc file CSV
input_file = "locations.csv"  # Đường dẫn tới file CSV
output_file = "output_with_coordinates.csv"

# Khởi tạo geolocator từ Nominatim
geolocator = Nominatim(user_agent="geoapiExercises")

# Đọc file CSV chứa danh sách địa điểm
df = pd.read_csv(input_file)

# In tên cột để kiểm tra
print("Tên cột trong file CSV:", df.columns)

# Đảm bảo cột địa điểm tồn tại
if 'Địa điểm' in df.columns:
    location_column = 'Địa điểm'  # Tên cột chính xác
else:
    raise KeyError("Cột chứa địa điểm không tồn tại trong file CSV.")

# Thêm các cột cho tọa độ và tên đường
df['Latitude'] = None
df['Longitude'] = None
df['Formatted Address'] = None

# Hàm tìm tọa độ
def get_location_data(location_name):
    try:
        location = geolocator.geocode(location_name)
        if location:
            return location.latitude, location.longitude, location.address
        else:
            return None, None, None
    except Exception as e:
        print(f"Lỗi: {e}")
        return None, None, None

# Lấy thông tin cho từng địa điểm
for index, row in df.iterrows():
    location_name = row[location_column]  # Lấy tên địa điểm từ cột đúng
    print(f"Đang xử lý: {location_name}")
    lat, lng, address = get_location_data(location_name)
    df.at[index, 'Latitude'] = lat
    df.at[index, 'Longitude'] = lng
    df.at[index, 'Formatted Address'] = address

    # Dừng 1 giây giữa các lần gọi để tránh bị block
    sleep(1)

# Lưu lại kết quả
df.to_csv(output_file, index=False)
print("Hoàn tất! Dữ liệu đã được lưu vào:", output_file)
