import csv
import json
import openai
from datetime import datetime, timedelta

# Đảm bảo bạn thay đổi API Key
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 
openai.api_key = os.getenv("OPENAI_API_KEY")
def generate_dates(start_date, days):
    """Tạo danh sách ngày từ ngày bắt đầu và trả về ngày kết thúc."""
    start = datetime.strptime(start_date, "%d/%m/%Y")
    dates = [(start + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(days)]
    end_date = (start + timedelta(days=days - 1)).strftime("%d/%m/%Y")
    return dates, end_date

def suggest_trip_plan(input):
    dates, end_date = generate_dates(input['start_date'], input['days'])
    prompt = f"""
You are a travel assistant. The user provides details about their trip, and you will suggest a detailed itinerary for each day.
The information provided by the user:
- Departure point: {input['startLocation']}
- Destination: {input['destination']}
- Duration: {input['days']} days (from {input['start_date']} to {end_date})
- Budget: {input['budget']} VND
- Transportation: {input['transport']}

Requirements:
1. The itinerary is divided by day, each day has time slots for morning, noon, afternoon, and evening.
2. Provide **specific and real** names of hotels, restaurants, cafes, and tourist attractions.
3. **Each city or destination should suggest only one hotel or homestay for the days you stay there**. If you stay in Hoi An from day 1 to day 2, only one hotel is needed for those two days, then you move to a different hotel when you reach Da Nang.
4. Add a coffee shop or a place for drinks every day, avoiding duplication and fitting into the schedule.
5. Each day must include activities: sightseeing, eating, resting, and visiting cafes or places for drinks.
6. Ensure the listed places are suitable with the time and budget.
7. If a real place cannot be found, return an error or refuse to suggest.
8. The places should include local famous restaurants or popular coffee shops.
9. Specify the province or city of each place.

Desired output:
1. Return the result in JSON format as follows:
{{
  "trip_plans": [
    {{
      "suggestion": "Suggestion 1: Nature Exploration Itinerary",
      "theme": "Nature Exploration",
      "details": [
        {{
          "date": "Day Month", // e.g., "5 December 2024"
          "time_range": "Time range", // e.g., "7:00 AM - 8:00 AM"
          "location": "Specific place name", // e.g., "Phở Bát Đàn"
          "province_city": "Province or city name", // e.g., "Hà Nội"
          "activity": "Activity", // e.g., "Eating breakfast"
          "cost": "Cost" // e.g., 50000
        }}
      ]
    }},
    {{
      "suggestion": "Suggestion 2: Food Exploration Itinerary",
      "theme": "Food Exploration",
      "details": [
        {{
          "date": "Day Month", // e.g., "5 December 2024"
          "time_range": "Time range", // e.g., "7:00 AM - 8:00 AM"
          "location": "Specific place name", // e.g., "Bánh Cuốn Gia Truyền"
          "province_city": "Province or city name", // e.g., "Hà Nội"
          "activity": "Activity", // e.g., "Eating breakfast"
          "cost": "Cost" // e.g., 40000
        }}
      ]
    }},
    {{
      "suggestion": "Suggestion 3: Cultural Exploration Itinerary",
      "theme": "Cultural Exploration",
      "details": [
        {{
          "date": "Day Month", // e.g., "6 December 2024"
          "time_range": "Time range", // e.g., "9:00 AM - 11:00 AM"
          "location": "Specific place name", // e.g., "Temple of Literature"
          "province_city": "Province or city name", // e.g., "Hà Nội"
          "activity": "Activity", // e.g., "Exploring cultural heritage"
          "cost": "Cost" // e.g., 70000
        }}
      ]
    }}
  ]
}}


2. Example:
Below are itinerary suggestions customized into three main themes: nature exploration, food exploration, and cultural exploration.
  Must to have them
  Every suggestion should enough all day in plan from start day to end day
   
 Suggestion 1: Nature exploration itinerary 
  {{
    "trip_plans1": [
    "theme": "Nature Exploration",
    "details": [{{

      "date": "5 December 2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Phở Bát Đàn",

      "province_city": "Hà Nội",

      "activity": "Eating breakfast",

      "cost": 50000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "8:30 AM - 12:00 PM",

      "location": "Tam Đảo National Park",

      "province_city": "Vĩnh Phúc",

      "activity": "Hiking and sightseeing",

      "cost": 100000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "12:30 PM - 1:30 PM",

      "location": "Nhà Hàng Tam Đảo",

      "province_city": "Vĩnh Phúc",

      "activity": "Eating lunch",

      "cost": 80000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "2:00 PM - 5:30 PM",

      "location": "Ba Vì Mountain",

      "province_city": "Hà Nội",

      "activity": "Exploring nature trails",

      "cost": 100000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "6:00 PM - 7:00 PM",

      "location": "Quán Ăn Dân Tộc",

      "province_city": "Hà Nội",

      "activity": "Dinner with local cuisine",

      "cost": 80000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "9:00 PM - Overnight",

      "location": "Mai Châu Homestay",

      "province_city": "Hòa Bình",

      "activity": "Resting in nature",

      "cost": 200000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Café Mai",

      "province_city": "Hà Nội",

      "activity": "Morning coffee",

      "cost": 30000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "9:00 AM - 12:00 PM",

      "location": "Cúc Phương National Park",

      "province_city": "Ninh Bình",

      "activity": "Exploring biodiversity",

      "cost": 150000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "12:30 PM - 1:30 PM",

      "location": "Nhà Hàng Đất Ninh",

      "province_city": "Ninh Bình",

      "activity": "Lunch with local dishes",

      "cost": 90000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "2:00 PM - 5:30 PM",

      "location": "Tràng An Scenic Landscape Complex",

      "province_city": "Ninh Bình",

      "activity": "Boat tour",

      "cost": 200000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "6:00 PM - 7:00 PM",

      "location": "Quán Cơm Niêu",

      "province_city": "Ninh Bình",

      "activity": "Dinner",

      "cost": 100000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "9:00 PM - Overnight",

      "location": "Ninh Bình Hidden Charm Hotel",

      "province_city": "Ninh Bình",

      "activity": "Rest",

      "cost": 250000

    }}
]

    ]
  }}
  Suggestion 2: Food exploration itinerary 
  {{
    "trip_plans2": [
    "theme": "Food Exploration",
    "details": [
    {{

      "date": "5 December 2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Bánh Cuốn Gia Truyền",

      "province_city": "Hà Nội",

      "activity": "Eating breakfast",

      "cost": 40000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "8:30 AM - 10:30 AM",

      "location": "Chợ Đồng Xuân",

      "province_city": "Hà Nội",

      "activity": "Trying local street food",

      "cost": 80000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "12:00 PM - 1:30 PM",

      "location": "Bún Chả Hương Liên",

      "province_city": "Hà Nội",

      "activity": "Eating lunch",

      "cost": 50000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "2:00 PM - 4:00 PM",

      "location": "Làng Vũ Đại",

      "province_city": "Hà Nam",

      "activity": "Trying Cá Kho Làng Vũ Đại",

      "cost": 120000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "6:00 PM - 8:00 PM",

      "location": "Quán Lẩu Bò Nhúng Dấm",

      "province_city": "Nam Định",

      "activity": "Dinner",

      "cost": 150000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "9:00 PM - Overnight",

      "location": "Homestay Xứ Nam",

      "province_city": "Nam Định",

      "activity": "Resting",

      "cost": 250000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Trà Chanh Bụi Phố",

      "province_city": "Nam Định",

      "activity": "Morning tea",

      "cost": 20000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "9:00 AM - 11:00 AM",

      "location": "Quán Phở Gia Truyền",

      "province_city": "Hà Nội",

      "activity": "Trying Phở",

      "cost": 60000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "12:00 PM - 1:30 PM",

      "location": "Chả Cá Lã Vọng",

      "province_city": "Hà Nội",

      "activity": "Eating lunch",

      "cost": 120000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "2:00 PM - 4:30 PM",

      "location": "Café Duy Trí",

      "province_city": "Hà Nội",

      "activity": "Coffee tasting",

      "cost": 40000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "5:00 PM - 7:00 PM",

      "location": "Chợ Hồ Tây",

      "province_city": "Hà Nội",

      "activity": "Street food dinner",

      "cost": 70000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "9:00 PM - Overnight",

      "location": "Khách Sạn Sunrise",

      "province_city": "Hà Nội",

      "activity": "Resting",

      "cost": 280000

    }}
]

    ]
  }}
  Suggestion 3: Culture exploration itinerary 
  {{
    "trip_plans3": [
    "theme": "Culture Exploration",
    "details": [
    {{

      "date": "5 December 2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Phở Thìn",

      "province_city": "Hà Nội",

      "activity": "Eating breakfast",

      "cost": 50000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "9:00 AM - 12:00 PM",

      "location": "Hoàng Thành Thăng Long",

      "province_city": "Hà Nội",

      "activity": "Exploring ancient citadel",

      "cost": 150000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "12:30 PM - 1:30 PM",

      "location": "Nhà Hàng Bún Ốc Phủ Tây Hồ",

      "province_city": "Hà Nội",

      "activity": "Eating lunch",

      "cost": 80000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "2:00 PM - 5:00 PM",

      "location": "Văn Miếu - Quốc Tử Giám",

      "province_city": "Hà Nội",

      "activity": "Learning about Vietnam's educational history",

      "cost": 100000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "6:00 PM - 8:00 PM",

      "location": "Chợ Đêm Đồng Xuân",

      "province_city": "Hà Nội",

      "activity": "Shopping and cultural exploration",

      "cost": 50000

    }},

    {{

      "date": "5 December 2024",

      "time_range": "9:00 PM - Overnight",

      "location": "Khách Sạn Ảnh Phố",

      "province_city": "Hà Nội",

      "activity": "Resting",

      "cost": 300000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Café Giảng",

      "province_city": "Hà Nội",

      "activity": "Egg coffee experience",

      "cost": 40000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "9:00 AM - 11:00 AM",

      "location": "Bảo Tàng Lịch Sử Quốc Gia",

      "province_city": "Hà Nội",

      "activity": "Visiting historical museum",

      "cost": 100000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "11:30 AM - 1:00 PM",

      "location": "Quán Bún Đậu Mắm Tôm",

      "province_city": "Hà Nội",

      "activity": "Lunch with traditional dish",

      "cost": 50000

    }},

    {{

      "date": "6 December 2024",

      "time_range": "2:00 PM - 4:00 PM",

      "location": "Nhà Hát Lớn Hà Nội",

      "province_city": "Hà Nội",

      "activity":}}

    ]

    ]
  }}
"""

    try:
        # Gọi API OpenAI để nhận lịch trình
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.7
        )

        # In toàn bộ phản hồi để kiểm tra dữ liệu
       

        # Kiểm tra nếu phản hồi có định dạng đúng JSON và xử lý nó
        trip_plans_json = response['choices'][0]['message']['content'].strip()
        print(trip_plans_json)
        try:
            # Thử parse lại JSON từ dữ liệu trả về
            trip_plans = json.loads(trip_plans_json)
            
            # Ghi kết quả vào file CSV
            with open("trip_plans_recommend_multiple_suggestion.csv", mode="w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Ngày", "Khung giờ", "Địa điểm", "Tỉnh thành phố", "Hoạt động", "Chi phí", "Thể loại"])

                for plan in trip_plans["trip_plans"]:
                    theme = plan["theme"]  # Lấy thể loại từ kế hoạch chuyến đi
                    for detail in plan["details"]:
                        writer.writerow([
                            detail["date"],
                            detail["time_range"],
                            detail["location"],
                            detail["province_city"],
                            detail["activity"],
                            detail["cost"],
                            theme  # Thêm thể loại vào dòng CSV
                        ])

            print(f"Kết quả đã được lưu vào file 'trip_plans_recommend1_copy.csv'. Chuyến đi kéo dài từ {user_input['start_date']}.")

        except json.JSONDecodeError as e:
            print(f"Lỗi định dạng JSON từ phản hồi: {e}")
        except Exception as e:
            print(f"Lỗi khi xử lý dữ liệu: {e}")

    except Exception as e:
        print(f"Lỗi khi gọi API OpenAI: {e}")

# Thông tin người dùng nhập
user_input = {
    "startLocation": "Đà Nẵng",
    "destination": "Hội An",
    "days": 2,
    "start_date": "05/12/2024",  # Ngày bắt đầu chuyến đi
    "budget": 5000000,
    "transport": "xe máy"
}

# Gọi hàm để gợi ý lịch trình
suggest_trip_plan(user_input)