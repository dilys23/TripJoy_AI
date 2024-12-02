import csv
import json
import openai
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import pandas as pd
from playwright.sync_api import sync_playwright

app = Flask(__name__)

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

def clean_trip_data(trip_data):
    """Clean the trip data to ensure it is in the correct format."""
    cleaned_data = []
    
    for trip in trip_data:
        # Ensure cost is an integer
        for detail in trip['details']:
            detail['cost'] = int(detail['cost']) if isinstance(detail['cost'], (int, float)) else 0
            # Ensure date is correctly formatted
            try:
                detail['date'] = datetime.strptime(detail['date'], "%d %B %Y").strftime("%d/%m/%Y")
            except ValueError:
                detail['date'] = "Invalid Date"
        cleaned_data.append(trip)
    return cleaned_data

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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.7
        )
        print("response",response['choices'][0]['message']['content'].strip())
        # return response['choices'][0]['message']['content'].strip()
         # Process and clean the response
        # Trích xuất và làm sạch dữ liệu từ phản hồi
        trip_data = json.loads(response['choices'][0]['message']['content'].strip())
        trip_plans = clean_trip_data(trip_data['trip_plans'])
        print ("trip_plans",trip_plans)
        # Lấy danh sách các địa điểm từ kế hoạch chuyến đi
        locations = [f"{detail['location']}, {detail['province_city']}" for plan in trip_plans for detail in plan['details']]
        print("locations list", locations)

# Gọi hàm scrape_locations với danh sách chuỗi locations
        location_details = scrape_locations(locations)


        # Gọi hàm scrape_locations để lấy thông tin chi tiết từ Google Maps
        location_details = scrape_locations(locations)

        # Kết hợp dữ liệu từ trip_plans và location_details
        for plan in trip_plans:
          for detail, location_detail in zip(plan['details'], location_details):
              detail['address'] = location_detail.get('address', 'N/A')
              detail['latitude'] = location_detail.get('latitude', 'N/A')
              detail['longitude'] = location_detail.get('longitude', 'N/A')

        # Trả về dữ liệu kết hợp
        return {"trip_plans": trip_plans}

    except Exception as e:
        return {"error": str(e)}
    
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


# API endpoint để xử lý yêu cầu
@app.route('/')
def home():
    return "Welcome to the Trip Planner API!"

@app.route('/api/trip-planner', methods=['POST'])
def trip_planner():
    try:
        # Nhận dữ liệu từ request
        input_data = request.json
        # Gọi hàm suggest_trip_plan
        result = suggest_trip_plan(input_data)
        # print(r)
        # Trả về kết quả dưới dạng JSON
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Chạy ứng dụng Flask
if __name__ == '__main__':
    app.run(debug=True)