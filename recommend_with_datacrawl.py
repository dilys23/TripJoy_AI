import os
import json
import csv
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
import openai
from geopy.distance import geodesic

# Tải biến môi trường từ file .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Dữ liệu đầu vào
input_data = {
    'startLocation': 'Đà Nẵng',
    'destination': 'Huế',
    'days': 3,
    'start_date': '2024-12-02',
    'budget': 3000000,  # 3 triệu VNĐ
    'transport': 'xe máy'
}

# Tính toán ngày kết thúc
start_date = datetime.strptime(input_data['start_date'], '%Y-%m-%d')
end_date = start_date + timedelta(days=input_data['days'] - 1)
input_data['end_date'] = end_date.strftime('%Y-%m-%d')

# Giá trị tối thiểu và tối đa
min_score = 4.3
max_price = input_data['budget'] / (input_data['days'] * 3)

# Đọc dữ liệu từ file CSV
def load_csv(file_path):
    try:
        data = pd.read_csv(file_path)
        return data.to_dict('records')
    except FileNotFoundError:
        print(f"Lỗi: File '{file_path}' không tồn tại.")
        exit()

# Lọc và sắp xếp địa điểm theo khoảng cách
def filter_and_sort_places(places, min_score, max_price, start_location):
    filtered = []
    for place in places:
        try:
            score = float(place['score']) if place['score'] != 'Chưa xét' else 0
            price = int(place['price'])
            if score >= min_score and price <= max_price:
                place['coordinates'] = (
                    float(place['latitude']), float(place['longitude'])
                )  # Thêm tọa độ
                filtered.append(place)
        except (ValueError, KeyError) as e:
            print(f"Lỗi xử lý địa điểm {place.get('name', 'Không xác định')}: {e}")

    # Sắp xếp theo khoảng cách từ vị trí bắt đầu
    start_coords = (16.0544, 108.2022)  # Tọa độ Đà Nẵng
    filtered.sort(
        key=lambda x: geodesic(start_coords, x['coordinates']).km
    )
    # print("filtered: ",filtered)
    return filtered

# Tạo prompt từ danh sách địa điểm
def create_prompt(chunk, input_data):
    places_text = "\n".join([
        f"- {place['name']} tại {place['address']} (Điểm: {place['score']}, Loại: {place['category']}, Giá: {place['price']})"
        for place in chunk
    ])
    return f"""
    Tôi có danh sách các địa điểm sau tại Huế và Đà Nẵng:
    {places_text}

    Bạn là một trợ lý du lịch. Người dùng cung cấp thông tin về chuyến đi, và bạn sẽ gợi ý 3 lịch trình chi tiết theo từng ngày từ danh sách tôi thu thập đó, với các chủ đề sau:
    1. Khám phá thiên nhiên.
    2. Khám phá ẩm thực.
    3. Khám phá văn hóa.

    Thông tin người dùng cung cấp:
    - Điểm khởi hành: {input_data['startLocation']}
    - Điểm đến: {input_data['destination']}
    - Số ngày: {input_data['days']} ngày (từ {input_data['start_date']} đến {input_data['end_date']})
    - Ngân sách: {input_data['budget']} VNĐ
    - Phương tiện: {input_data['transport']}

    Yêu cầu:
1. Lịch trình được chia theo từng ngày, mỗi ngày có các khung giờ từ sáng, trưa, chiều, tối.
2. Đưa ra tên **cụ thể và thực tế** của khách sạn, nhà hàng, quán cà phê và các địa điểm tham quan.
3. **Mỗi khu vực thành phố hoặc điểm đến chỉ gợi ý một khách sạn hoặc homestay cho các ngày bạn ở tại đó**. Nếu bạn lưu trú ở Hội An từ ngày 1 đến ngày 2, bạn chỉ cần 1 khách sạn cho 2 ngày đó, sau đó chuyển sang khách sạn khác khi đến Đà Nẵng.
4. Thêm địa điểm cà phê hoặc nơi uống nước vào mỗi ngày, tránh trùng lặp và phù hợp với lịch trình.
5. Mỗi ngày phải bao gồm các hoạt động: tham quan, ăn uống, nghỉ ngơi, và các địa điểm cà phê hoặc uống nước.
6. Đảm bảo các địa điểm được liệt kê phù hợp với thời gian và ngân sách.
7. Nếu không tìm được địa điểm thực tế, trả về lỗi hoặc từ chối gợi ý.
8. Các địa điểm cần xen kẻ các quán ăn địa phương nổi tiếng hoặc quán coffee nổi tiếng
9. Hãy chỉ rõ địa điểm đó thuộc tỉnh hay thành phố nào.

    Kết quả trả về dưới dạng JSON như ví dụ sau:
    {{
    Lịch trình 1: Khám phá thiên nhiên 
        "trip_plans": [
            {{
                "date": "YYYY-MM-DD",
                "details": [
                    {{
                        "time_range": "Khung giờ", (ví dụ 7h-8h, 9h-10h, v.v)
                        "location": "Tên địa điểm",
                        "address": "Địa chỉ",
                        "province_city": "Tên tỉnh thành phố",
                        "activity": "Hoạt động",
                        "score": "Điểm đánh giá",
                        "cost": "Chi phí"
                    }}
                ]
            }}
        ]
    
    }}
    """

# Gửi yêu cầu OpenAI
def generate_trip_plans(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.7
        )
        return json.loads(response['choices'][0]['message']['content'].strip())
    except Exception as e:
        print(f"Lỗi khi gửi yêu cầu OpenAI: {e}")
        return None

# Ghi kết quả ra file CSV
def save_to_csv_all(trip_plans, file_name="trip_plans_recommend123.csv"):
    with open(file_name, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        for plan in trip_plans["trip_plans"]:
            for detail in plan["details"]:
                writer.writerow([
                    plan["date"],
                    detail["time_range"],
                    detail["location"],
                    detail["address"],
                    detail["province_city"],
                    detail["activity"],
                    detail["cost"]
                ])

# Chương trình chính
if __name__ == "__main__":
    # Xóa file CSV nếu đã tồn tại, để ghi mới từ đầu
    file_name = "trip_plans_recommend123.csv"
    if os.path.exists(file_name):
        os.remove(file_name)

    # Tạo file CSV mới và thêm header
    with open(file_name, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Ngày", "Khung giờ", "Địa điểm", "Địa chỉ", "Tỉnh/Thành phố", "Hoạt động", "Chi phí"])

    # Tiếp tục xử lý các chunk
    places = load_csv('./input/InputData.csv')
    filtered_places = filter_and_sort_places(places, min_score, max_price, input_data['startLocation'])

    if not filtered_places:
        print("Không có địa điểm nào phù hợp với tiêu chí ngân sách và điểm số.")
        exit()

    chunk_size = 100
    chunks = [filtered_places[i:i + chunk_size] for i in range(0, len(filtered_places), chunk_size)]

    for idx, chunk in enumerate(chunks):
        prompt = create_prompt(chunk, input_data)
        trip_plans = generate_trip_plans(prompt)
        if trip_plans:
            save_to_csv_all(trip_plans, file_name)
            print(f"Lịch trình từ chunk {idx + 1} đã được thêm vào file.")
