import openai
import csv

import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 
openai.api_key = os.getenv("OPENAI_API_KEY")

def suggest_trip_plan(input):
    prompt = f"""
     Bạn là một trợ lý du lịch. Người dùng cung cấp thông tin về chuyến đi, và bạn sẽ gợi ý nhiều lịch trình khác nhau. 

    Thông tin người dùng cung cấp:
    - Điểm khởi hành: {input['startLocation']}
    - Điểm đến: {input['destination']}
    - Số ngày: {input['days']} ngày
    - Ngân sách: {input['budget']} VNĐ
    - Phương tiện: {input['transport']}

    Hãy tạo 3 lịch trình khác nhau, mỗi lịch trình theo một chủ đề:
    1. Khám phá thiên nhiên.
    2. Du lịch ẩm thực.
    3. Văn hóa - lịch sử.

    Mỗi lịch trình phải chi tiết và kèm thông tin chi phí, ăn uống, lưu trú.
    Hãy tách biệt ra theo khung giờ trong ngày như 8h đến 9h và các địa chỉ phải có tên rõ ràng cụ thể, các điểm ăn uống cần rõ ràng tên quán, hãy kèm thêm giá tiền sau mỗi địa điểm, nếu khôn tốn phí thì ghi 0 đồng
    {{
    
  "trip_plans": [
    {{
      "theme": "Nature Exploration",
      "details": [
        {{
          "date": "2 December 2024",
          "time_range": "7:00 AM - 8:00 AM",
          "location": "Mì Quảng Ếch Trang",
          "province_city": "Đà Nẵng",
          "activity": "Eating breakfast",
          "cost": 50000
        }}, 
        {{
          "date": "2 December 2024",
          "time_range": "8:30 AM - 12:00 PM",
          "location": "Bán Đảo Sơn Trà",
          "province_city": "Đà Nẵng",
          "activity": "Hiking and sightseeing",
          "cost": 100000
        }},
        {{
          "date": "2 December 2024",
          "time_range": "12:30 PM - 1:30 PM",
          "location": "Bánh xèo bà Dưỡng",
          "province_city": "Đà Nẵng",
          "activity": "Eating lunch",
          "cost": 80000
        }},
        {{
          "date": "2 December 2024",
          "time_range": "2:00 PM - 5:30 PM",
          "location": "Bãi biển Mỹ Khê",
          "province_city": "Đà Nẵng",
          "activity": "Exploring nature trails",
          "cost": 100000
        }},
        {{
          "date": "2 December 2024",
          "time_range": "6:00 PM - 7:00 PM",
          "location": "Bánh canh Ruộng cô Cúc",
          "province_city": "Đà Nẵng",
          "activity": "Dinner with local cuisine",
          "cost": 80000
        }},
        {{
          "date": "2 December 2024",
          "time_range": "9:00 PM - Overnight",
          "location": "Mộc Nhiên Homestay",
          "province_city": "Đà Nẵng",
          "activity": "Resting in nature",
          "cost": 200000
        }},
        {{
          "date": "3 December 2024",
          "time_range": "7:00 AM - 8:00 AM",
          "location": "Mộc Nhiên Homestay",
          "province_city": "Hòa Bình",
          "activity": "Resting in nature",
          "cost": 200000
        }},
        {{
          "date": "3 December 2024",
          "time_range": "8:30 AM - 12:00 PM",
          "location": "Chùa Linh Ứng",
          "province_city": "Hòa Bình",
          "activity": "Boat ride and sightseeing",
          "cost": 120000
        }},
        {{
          "date": "3 December 2024",
          "time_range": "12:30 PM - 1:30 PM",
          "location": "Bún Chả cá ",
          "province_city": "Hòa Bình",
          "activity": "Eating lunch",
          "cost": 90000
        }},
        {{
          "date": "3 December 2024",
          "time_range": "2:00 PM - 4:00 PM",
          "location": "Bảo Tàng Đà Nẵng",
          "province_city": "Đà Nẵng",
          "activity": "Sightseeing and walking",
          "cost": 0
        }},
        {{
          "date": "3 December 2024",
          "time_range": "6:00 PM - 7:00 PM",
          "location": "Cao Lầu Hội An",
          "province_city": "Hội An",
          "activity": "Dinner with local food",
          "cost": 100000
        }},
        {{
          "date": "3 December 2024",
          "time_range": "9:00 PM - Overnight",
          "location": "Lala Homestay",
          "province_city": "Hội An",
          "activity": "Resting in nature",
          "cost": 200000
        }},
        {{
          "date": "4 December 2024",
          "time_range": "7:00 AM - 8:00 AM",
          "location": "Bánh bèo Hội An",
          "province_city": "Hội An",
          "activity": "Resting and preparing to leave",
          "cost": 200000
        }},
        {{
          "date": "4 December 2024",
          "time_range": "9:00 AM - 12:00 PM",
          "location": "Phố cổ Hội An",
          "province_city": "Hội An",
          "activity": "Travel back",
          "cost": 0
        }}
      ]
    }},
    {{
      "theme": "Culinary Tour",
      "details": [
        {{
          "date": "2 December 2024",
          "time_range": "7:00 AM - 8:00 AM",
          "location": "Bánh Mì Phượng",
          "province_city": "Đà Nẵng",
          "activity": "Eating breakfast",
          "cost": 35000
        }},
        {{
          "date": "2 December 2024",
          "time_range": "9:00 AM - 12:00 PM",
          "location": "Chợ Cồn",
          "province_city": "Đà Nẵng",
          "activity": "Trying local food stalls",
          "cost": 50000
        }},
        {{
          "date": "2 December 2024",
          "time_range": "12:30 PM - 1:30 PM",
          "location": "Quán Bánh Xèo",
          "province_city": "Đà Nẵng",
          "activity": "Eating lunch",
          "cost": 70000
        }},
        {{
          "date": "2 December 2024",
          "time_range": "2:00 PM - 4:00 PM",
          "location": "Bảo tàng Đà Nẵng",
          "province_city": "Đà Nẵng",
          "activity": "Museum tour",
          "cost": 20000
        }},
        {{
          "date": "2 December 2024",
          "time_range": "6:00 PM - 7:30 PM",
          "location": "Nhà Hàng Hải Sản",
          "province_city": "Đà Nẵng",
          "activity": "Eating seafood",
          "cost": 250000
        }},
        {{
          "date": "2 December 2024",
          "time_range": "9:00 PM - Overnight",
          "location": "Khách sạn Duyên Hải",
          "province_city": "Đà Nẵng",
          "activity": "Resting in hotel",
          "cost": 800000
        }},
        {{
          "date": "3 December 2024",
          "time_range": "7:00 AM - 8:00 AM",
          "location": "Café Trung Nguyên",
          "province_city": "Đà Nẵng",
          "activity": "Morning coffee",
          "cost": 30000
        }},
        {{
          "date": "3 December 2024",
          "time_range": "8:30 AM - 12:00 PM",
          "location": "Bà Nà Hills",
          "province_city": "Đà Nẵng",
          "activity": "Cable car ride and sightseeing",
          "cost": 400000
        }},
        {{
          "date": "3 December 2024",
          "time_range": "12:30 PM - 1:30 PM",
          "location": "Nhà Hàng Bà Nà",
          "province_city": "Đà Nẵng",
          "activity": "Eating lunch",
          "cost": 150000
        }},
        {{
          "date": "3 December 2024",
          "time_range": "2:00 PM - 4:00 PM",
          "location": "Chùa Linh Ứng",
          "province_city": "Đà Nẵng",
          "activity": "Sightseeing and cultural visit",
          "cost": 0
        }},
        {{
          "date": "3 December 2024",
          "time_range": "6:00 PM - 7:30 PM",
          "location": "Quán Ăn Phố Cổ",
          "province_city": "Đà Nẵng",
          "activity": "Dinner with local cuisine",
          "cost": 100000
        }},
        {{
          "date": "3 December 2024",
          "time_range": "9:00 PM - Overnight",
          "location": "Khách sạn Duyên Hải",
          "province_city": "Đà Nẵng",
          "activity": "Resting in hotel",
          "cost": 800000
        }}
      ]
    }},
    {{
      "theme": "Cultural & Historical Tour",
      "details": [
        {{
          "date": "2 December 2024",
          "time_range": "7:00 AM - 8:00 AM",
          "location": "Chùa Linh Ứng",
          "province_city": "Đà Nẵng",
          "activity": "Morning temple visit",
          "cost": 0
        }},
        {{
          "date": "2 December 2024",
          "time_range": "9:00 AM - 12:00 PM",
          "location": "Cố đô Huế",
          "province_city": "Thừa Thiên Huế",
          "activity": "Visit historical sites",
          "cost": 300000
        }},
        {{
          "date": "2 December 2024",
          "time_range": "12:30 PM - 1:30 PM",
          "location": "Nhà Hàng Huế",
          "province_city": "Thừa Thiên Huế",
          "activity": "Eating lunch",
          "cost": 150000
        }},
        {{
          "date": "2 December 2024",
          "time_range": "2:00 PM - 5:00 PM",
          "location": "Công viên Huế",
          "province_city": "Thừa Thiên Huế",
          "activity": "Cultural walk and exploration",
          "cost": 0
        }},
        {{
          "date": "2 December 2024",
          "time_range": "6:00 PM - 7:00 PM",
          "location": "Nhà Hàng Phố Cổ",
          "province_city": "Thừa Thiên Huế",
          "activity": "Dinner",
          "cost": 150000
        }},
        {{ 
          "date": "2 December 2024",
          "time_range": "9:00 PM - Overnight",
          "location": "Khách sạn Huế",
          "province_city": "Thừa Thiên Huế",
          "activity": "Resting in hotel",
          "cost": 800000
        }}
      ]
    }}
  ]
}}

    """

    try:
        # Gọi API OpenAI để lấy gợi ý lịch trình
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Hoặc "gpt-4" nếu bạn muốn sử dụng GPT-4
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.7
        )

        # Kiểm tra xem API trả về dữ liệu hợp lệ
        if 'choices' in response and len(response['choices']) > 0:
            trip_plans = response['choices'][0]['message']['content'].strip()
            print("Kết quả:", trip_plans)
        else:
            print("Không có dữ liệu trả về từ API.")
            return

        # Xuất kết quả ra file CSV
        with open("trip_plans123.csv", mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)

            # Ghi tiêu đề
            writer.writerow(["Theme", "Date", "Time Range", "Location", "Province/City", "Activity", "Cost"])

            # Phân tách các lịch trình, loại bỏ các phần không phải lịch trình (ví dụ: phần mô tả chung)
            trip_plans = trip_plans.split("\n\n")  # Mỗi lịch trình cách nhau một dòng trống
            for theme in trip_plans:
                # Nếu đoạn văn bản chứa thông tin về các hoạt động, tiếp tục xử lý
                if "Ngày" in theme:
                    lines = theme.split("\n")
                    theme_name = lines[0].strip()  # Lấy tên chủ đề

                    # Duyệt qua từng ngày trong lịch trình
                    for line in lines[1:]:
                        if ":" in line:
                            parts = line.split(":")
                            date = parts[0].strip()
                            activities = parts[1].strip().split("\n")  # Các hoạt động theo từng dòng

                            for activity in activities:
                                activity_parts = activity.split(",")
                                if len(activity_parts) > 1:
                                    time_range = activity_parts[0].strip()
                                    location = activity_parts[1].strip()
                                    province_city = activity_parts[2].strip() if len(activity_parts) > 2 else "N/A"
                                    activity_description = activity_parts[3].strip() if len(activity_parts) > 3 else "N/A"
                                    cost = int(activity_parts[4].replace("VNĐ", "").strip()) if len(activity_parts) > 4 and "VNĐ" in activity_parts[4] else 0
                                else:
                                    time_range = "N/A"
                                    location = activity.strip()
                                    province_city = "N/A"
                                    activity_description = "N/A"
                                    cost = 0

                                # Ghi thông tin vào file CSV
                                writer.writerow([theme_name, date, time_range, location, province_city, activity_description, cost])

        print("Kết quả đã được lưu vào file 'trip_plans123.csv'.")

    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")

# Thông tin người dùng nhập
user_input = {
    "startLocation": "Quy Nhơn",
    "destination": "Đà Lạt",
    "days": 3,
    "budget": 3000000,
    "transport": "xe máy"
}

# Gọi hàm để gợi ý lịch trình
suggest_trip_plan(user_input)