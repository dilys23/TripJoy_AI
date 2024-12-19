import requests

def get_lat_lng(address):
    # URL của API và API key của bạn
    api_key = 'loOfwWWk08IKb5q6lbWztwl5mGsBggVYTpAvLVGjDGDr4Axlw0uDFmfVNb7D6Mxa'
    base_url = "https://api.distancematrix.ai/maps/api/geocode/json"
    
    # Xây dựng URL truy vấn với địa chỉ và API key
    url = f"{base_url}?address={address}&key={api_key}"
    
    # Gửi yêu cầu GET tới API
    response = requests.get(url)
    
    # Kiểm tra nếu yêu cầu thành công
    if response.status_code == 200:
        data = response.json()
        
        # Kiểm tra nếu có kết quả
        if data['status'] == 'OK':
            # Trích xuất tọa độ từ dữ liệu trả về
            lat = data["result"][0]["geometry"]["location"]["lat"]
            lng = data["result"][0]["geometry"]["location"]["lng"]
            return lat, lng
        else:
            print("Không tìm thấy kết quả cho địa chỉ.")
            return None, None
    else:
        print(f"Yêu cầu không thành công. Mã lỗi: {response.status_code}")
        return None, None

# Danh sách các địa chỉ
addresses = [
    "21 Hà Văn Trí, Khuê Trung, Cẩm Lệ, Đà Nẵng 550000, Vietnam",
    "Lăng Cô, Phú Lộc, Thua Thien Hue, Vietnam",
    "03 Nguyễn Sinh Sắc, Vỹ Dạ, Huế, Thừa Thiên Huế, Vietnam",
    "Phú Hậu, Huế, Thua Thien Hue, Vietnam",
    "34 Nguyễn Công Trứ, Phú Hội, Huế, Thừa Thiên Huế, Vietnam",
    "15 Lý Thường Kiệt, Phú Nhuận, Huế, Thừa Thiên Huế 530000, Vietnam",
    "Hẻm 10 Bến Nghé, Phú Hội, Huế, Thừa Thiên Huế 52000, Vietnam",
    "Huế, Hương Hòa, Huế, Thừa Thiên Huế 530000, Vietnam",
    "7 kiet 28 Lê Thánh Tôn, Phú Hậu, Huế, Thừa Thiên Huế, Vietnam",
    "Hương Thọ, Hương Trà District, Thua Thien Hue, Vietnam",
    "166 Ni Sư Huỳnh Liên, Phường 10, Tân Bình, Hồ Chí Minh, Vietnam",
    "61 Hùng Vương, Phú Hội, Huế, Thừa Thiên Huế, Vietnam"
]

# Lặp qua danh sách các địa chỉ và lấy tọa độ cho mỗi địa chỉ
for address in addresses:
    lat, lng = get_lat_lng(address)
    if lat is not None and lng is not None:
        print(f"Địa chỉ: {address}\nVĩ độ: {lat}, Kinh độ: {lng}\n")
