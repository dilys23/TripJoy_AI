import csv
import json
import openai
from datetime import datetime, timedelta

# Đảm bảo bạn thay đổi API Key
openai.api_key = ""

def generate_dates(start_date, days):
    """Tạo danh sách ngày từ ngày bắt đầu và trả về ngày kết thúc."""
    start = datetime.strptime(start_date, "%d/%m/%Y")
    dates = [(start + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(days)]
    end_date = (start + timedelta(days=days - 1)).strftime("%d/%m/%Y")
    return dates, end_date

def suggest_trip_plan(input):
    dates, end_date = generate_dates(input['start_date'], input['days'])
    prompt = f"""
   Bạn là một trợ lý du lịch. Người dùng cung cấp thông tin về chuyến đi, và bạn sẽ gợi ý lịch trình chi tiết theo từng ngày.

Thông tin người dùng cung cấp:
- Điểm khởi hành: {input['startLocation']}
- Điểm đến: {input['destination']}
- Số ngày: {input['days']} ngày (từ {input['start_date']} đến {end_date})
- Ngân sách: {input['budget']} VNĐ
- Phương tiện: {input['transport']}

Yêu cầu:
1. Lịch trình được chia theo từng ngày, mỗi ngày có các khung giờ từ sáng, trưa, chiều, tối.
2. Đưa ra tên **cụ thể và thực tế** của khách sạn, nhà hàng, quán cà phê và các địa điểm tham quan.
3. **Mỗi khu vực thành phố hoặc điểm đến (ví dụ: Hội An, Đà Nẵng) chỉ gợi ý một khách sạn hoặc homestay cho các ngày bạn ở tại đó**. Nếu bạn lưu trú ở Hội An từ ngày 1 đến ngày 2, bạn chỉ cần 1 khách sạn cho 2 ngày đó, sau đó chuyển sang khách sạn khác khi đến Đà Nẵng.
4. Thêm địa điểm cà phê hoặc nơi uống nước vào mỗi ngày, tránh trùng lặp và phù hợp với lịch trình.
5. Mỗi ngày phải bao gồm các hoạt động: tham quan, ăn uống, nghỉ ngơi, và các địa điểm cà phê hoặc uống nước.
6. Đảm bảo các địa điểm được liệt kê phù hợp với thời gian và ngân sách.
7. Nếu không tìm được địa điểm thực tế, trả về lỗi hoặc từ chối gợi ý.
8. Các địa điểm cần xen kẻ các quán ăn địa phương nổi tiếng hoặc quán coffee nổi tiếng

Đầu ra mong muốn:
1. Trả kết quả dưới dạng JSON với định dạng:
{{
    "trip_plans": [
        {{
            "date": "Ngày tháng",
            "details": [
                {{"time_range": "Khung giờ", "location": "Tên địa điểm cụ thể", "activity": "Hoạt động", "cost": Chi phí}}
            ]
        }}
    ]
}}
2. Ví dụ:
{{
    "trip_plans": [
        {{
            "date": "05/12/2024",
            "details": [
                {{"time_range": "7h-8h", "location": "Khách sạn Anantara Hội An", "activity": "Ăn sáng", "cost": 200000}},
                {{"time_range": "9h-11h", "location": "Bãi biển Mỹ Khê", "activity": "Tham quan", "cost": 0}},
                {{"time_range": "12h-13h", "location": "Nhà hàng Bé Mặn", "activity": "Ăn trưa", "cost": 300000}},
                {{"time_range": "14h-16h", "location": "Hội An Impression Theme Park", "activity": "Tham quan", "cost": 100000}},
                {{"time_range": "16h-17h", "location": "Quán Cà Phê The Espresso Station", "activity": "Uống cà phê", "cost": 50000}},
                {{"time_range": "18h-20h", "location": "Nhà hàng đặc sản Mì Quảng Bà Hường", "activity": "Ăn tối", "cost": 150000}},
                {{"time_range": "20h+", "location": "Khách sạn Anantara Hội An", "activity": "Nghỉ ngơi", "cost": 0}}
            ]
        }},
        {{
            "date": "06/12/2024",
            "details": [
                {{"time_range": "7h-8h", "location": "Khách sạn Anantara Hội An", "activity": "Ăn sáng", "cost": 200000}},
                {{"time_range": "9h-11h", "location": "Chùa Cầu", "activity": "Tham quan", "cost": 0}},
                {{"time_range": "12h-13h", "location": "Nhà hàng Quán Cơm", "activity": "Ăn trưa", "cost": 150000}},
                {{"time_range": "14h-16h", "location": "Hội An Impression Theme Park", "activity": "Tham quan", "cost": 100000}},
                {{"time_range": "16h-17h", "location": "Quán Cà Phê Faifo", "activity": "Uống cà phê", "cost": 50000}},
                {{"time_range": "18h-20h", "location": "Nhà hàng Hải Sản Sông Hàn", "activity": "Ăn tối", "cost": 200000}},
                {{"time_range": "20h+", "location": "Khách sạn Anantara Hội An", "activity": "Nghỉ ngơi", "cost": 0}}
            ]
        }},
        {{
            "date": "07/12/2024",
            "details": [
                {{"time_range": "7h-8h", "location": "Khách sạn Novotel Đà Nẵng", "activity": "Ăn sáng", "cost": 200000}},
                {{"time_range": "9h-11h", "location": "Bà Nà Hills", "activity": "Tham quan", "cost": 500000}},
                {{"time_range": "12h-13h", "location": "Nhà hàng Phở Quảng", "activity": "Ăn trưa", "cost": 100000}},
                {{"time_range": "14h-16h", "location": "Bảo tàng Đà Nẵng", "activity": "Tham quan", "cost": 100000}},
                {{"time_range": "16h-17h", "location": "Quán Cà Phê 43", "activity": "Uống cà phê", "cost": 50000}},
                {{"time_range": "18h-20h", "location": "Nhà hàng Làng Nướng", "activity": "Ăn tối", "cost": 200000}},
                {{"time_range": "20h+", "location": "Khách sạn Novotel Đà Nẵng", "activity": "Nghỉ ngơi", "cost": 0}}
            ]
        }}
    ]
}}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Hoặc "gpt-4"
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.7
        )

        # Parse JSON từ phản hồi của API
        trip_plans_json = response['choices'][0]['message']['content'].strip()
        trip_plans = json.loads(trip_plans_json)

        # Ghi kết quả ra file CSV
        with open("trip_plans_recommend.csv", mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Ngày", "Khung giờ", "Địa điểm", "Hoạt động", "Chi phí"])

            for plan in trip_plans["trip_plans"]:
                date = plan["date"]
                for detail in plan["details"]:
                    writer.writerow([
                        date,
                        detail["time_range"],
                        detail["location"],
                        detail["activity"],
                        detail["cost"]
                    ])

        print(f"Kết quả đã được lưu vào file 'trip_plans_recommend.csv'. Chuyến đi kéo dài từ {input['start_date']} đến {end_date}.")

    except json.JSONDecodeError as e:
        print(f"Lỗi định dạng JSON từ phản hồi: {e}")
    except Exception as e:
        print(f"Lỗi khi xử lý: {e}")

# Thông tin người dùng nhập
user_input = {
    "startLocation": "Hội An",
    "destination": "Đà Nẵng",
    "days": 4,
    "start_date": "05/12/2024",  # Ngày bắt đầu chuyến đi
    "budget": 5000000,
    "transport": "xe máy"
}

# Gọi hàm để gợi ý lịch trình
suggest_trip_plan(user_input)
