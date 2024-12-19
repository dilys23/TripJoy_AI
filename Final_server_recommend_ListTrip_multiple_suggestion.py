import json
import openai
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import pandas as pd
from playwright.sync_api import sync_playwright
from flask_cors import CORS
import requests


app = Flask(__name__)
CORS(app)


import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
distance_matrix_api_key = os.getenv("DISTANCE_MATRIX_API_KEY")


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
        for detail in trip["details"]:
            detail["cost"] = (
                int(detail["cost"]) if isinstance(detail["cost"], (int, float)) else 0
            )
            try:
                detail["date"] = datetime.strptime(detail["date"], "%d %B %Y").strftime(
                    "%d/%m/%Y"
                )
            except ValueError:
                detail["date"] = "Invalid Date"
        cleaned_data.append(trip)
    return cleaned_data


def suggest_trip_plan(input):
    dates, end_date = generate_dates(input["start_date"], input["days"])
    prompt = f"""
You are a travel assistant. The user provides details about their trip, and you will suggest a detailed itinerary for each day.
The information provided by the user:
- Departure point: {input['startLocation']}
- Destination: {input['destination']}
- Duration: {input['days']} days (from {input['start_date']} to {input['end_date']})
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
      "suggestion": "Gợi ý 1 : Khám phá văn hóa",
      "theme": "Khám phá văn hóa",
      "details": [
        {{
          "date": "Day Month", // e.g., "5/12/2024"
          "time_range": "Time range", // e.g., "7:00 AM - 8:00 AM"
          "location": "Specific place name", // e.g., "Phở Bát Đàn"
          "province_city": "Province or city name", // e.g., "Hà Nội"
          "activity": "Activity", // e.g., "Eating breakfast"
          "cost": "Cost" // e.g., 50000
        }}
      ]
    }},
    {{
      "suggestion": "Gợi ý 2: Khám phá ẩm thực",
      "theme": "Khám phá ẩm thực",
      "details": [
        {{
          "date": "Day Month", // e.g., "5/12/2024"
          "time_range": "Time range", // e.g., "7:00 AM - 8:00 AM"
          "location": "Specific place name", // e.g., "Bánh Cuốn Gia Truyền"
          "province_city": "Province or city name", // e.g., "Hà Nội"
          "activity": "Activity", // e.g., "Eating breakfast"
          "cost": "Cost" // e.g., 40000
        }}
      ]
    }},
    {{
      "suggestion": "Gợi ý 3: Khám phá nền văn hóa",
      "theme": "Khám phá nền văn hóa",
      "details": [
        {{
          "date": "Day Month", // e.g., "5/12/2024"
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

      "date": "5/12/2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Phở Bát Đàn",

      "province_city": "Hà Nội",

      "activity": "Eating breakfast",

      "cost": 50000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "8:30 AM - 12:00 PM",

      "location": "Tam Đảo National Park",

      "province_city": "Vĩnh Phúc",

      "activity": "Hiking and sightseeing",

      "cost": 100000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "12:30 PM - 1:30 PM",

      "location": "Nhà Hàng Tam Đảo",

      "province_city": "Vĩnh Phúc",

      "activity": "Eating lunch",

      "cost": 80000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "2:00 PM - 5:30 PM",

      "location": "Ba Vì Mountain",

      "province_city": "Hà Nội",

      "activity": "Exploring nature trails",

      "cost": 100000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "6:00 PM - 7:00 PM",

      "location": "Quán Ăn Dân Tộc",

      "province_city": "Hà Nội",

      "activity": "Dinner with local cuisine",

      "cost": 80000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "9:00 PM - Overnight",

      "location": "Mai Châu Homestay",

      "province_city": "Hòa Bình",

      "activity": "Resting in nature",

      "cost": 200000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Café Mai",

      "province_city": "Hà Nội",

      "activity": "Morning coffee",

      "cost": 30000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "9:00 AM - 12:00 PM",

      "location": "Cúc Phương National Park",

      "province_city": "Ninh Bình",

      "activity": "Exploring biodiversity",

      "cost": 150000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "12:30 PM - 1:30 PM",

      "location": "Nhà Hàng Đất Ninh",

      "province_city": "Ninh Bình",

      "activity": "Lunch with local dishes",

      "cost": 90000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "2:00 PM - 5:30 PM",

      "location": "Tràng An Scenic Landscape Complex",

      "province_city": "Ninh Bình",

      "activity": "Boat tour",

      "cost": 200000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "6:00 PM - 7:00 PM",

      "location": "Quán Cơm Niêu",

      "province_city": "Ninh Bình",

      "activity": "Dinner",

      "cost": 100000

    }},

    {{

      "date": "6/12/2024",

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

      "date": "5/12/2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Bánh Cuốn Gia Truyền",

      "province_city": "Hà Nội",

      "activity": "Eating breakfast",

      "cost": 40000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "8:30 AM - 10:30 AM",

      "location": "Chợ Đồng Xuân",

      "province_city": "Hà Nội",

      "activity": "Trying local street food",

      "cost": 80000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "12:00 PM - 1:30 PM",

      "location": "Bún Chả Hương Liên",

      "province_city": "Hà Nội",

      "activity": "Eating lunch",

      "cost": 50000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "2:00 PM - 4:00 PM",

      "location": "Làng Vũ Đại",

      "province_city": "Hà Nam",

      "activity": "Trying Cá Kho Làng Vũ Đại",

      "cost": 120000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "6:00 PM - 8:00 PM",

      "location": "Quán Lẩu Bò Nhúng Dấm",

      "province_city": "Nam Định",

      "activity": "Dinner",

      "cost": 150000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "9:00 PM - Overnight",

      "location": "Homestay Xứ Nam",

      "province_city": "Nam Định",

      "activity": "Resting",

      "cost": 250000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Trà Chanh Bụi Phố",

      "province_city": "Nam Định",

      "activity": "Morning tea",

      "cost": 20000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "9:00 AM - 11:00 AM",

      "location": "Quán Phở Gia Truyền",

      "province_city": "Hà Nội",

      "activity": "Trying Phở",

      "cost": 60000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "12:00 PM - 1:30 PM",

      "location": "Chả Cá Lã Vọng",

      "province_city": "Hà Nội",

      "activity": "Eating lunch",

      "cost": 120000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "2:00 PM - 4:30 PM",

      "location": "Café Duy Trí",

      "province_city": "Hà Nội",

      "activity": "Coffee tasting",

      "cost": 40000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "5:00 PM - 7:00 PM",

      "location": "Chợ Hồ Tây",

      "province_city": "Hà Nội",

      "activity": "Street food dinner",

      "cost": 70000

    }},

    {{

      "date": "6/12/2024",

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

      "date": "5/12/2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Phở Thìn",

      "province_city": "Hà Nội",

      "activity": "Eating breakfast",

      "cost": 50000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "9:00 AM - 12:00 PM",

      "location": "Hoàng Thành Thăng Long",

      "province_city": "Hà Nội",

      "activity": "Exploring ancient citadel",

      "cost": 150000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "12:30 PM - 1:30 PM",

      "location": "Nhà Hàng Bún Ốc Phủ Tây Hồ",

      "province_city": "Hà Nội",

      "activity": "Eating lunch",

      "cost": 80000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "2:00 PM - 5:00 PM",

      "location": "Văn Miếu - Quốc Tử Giám",

      "province_city": "Hà Nội",

      "activity": "Learning about Vietnam's educational history",

      "cost": 100000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "6:00 PM - 8:00 PM",

      "location": "Chợ Đêm Đồng Xuân",

      "province_city": "Hà Nội",

      "activity": "Shopping and cultural exploration",

      "cost": 50000

    }},

    {{

      "date": "5/12/2024",

      "time_range": "9:00 PM - Overnight",

      "location": "Khách Sạn Ảnh Phố",

      "province_city": "Hà Nội",

      "activity": "Resting",

      "cost": 300000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "7:00 AM - 8:00 AM",

      "location": "Café Giảng",

      "province_city": "Hà Nội",

      "activity": "Egg coffee experience",

      "cost": 40000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "9:00 AM - 11:00 AM",

      "location": "Bảo Tàng Lịch Sử Quốc Gia",

      "province_city": "Hà Nội",

      "activity": "Visiting historical museum",

      "cost": 100000

    }},

    {{

      "date": "6/12/2024",

      "time_range": "11:30 AM - 1:00 PM",

      "location": "Quán Bún Đậu Mắm Tôm",

      "province_city": "Hà Nội",

      "activity": "Lunch with traditional dish",

      "cost": 50000

    }},

    {{

      "date": "6/12/2024",

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
            temperature=0.7,
        )
        print("response", response["choices"][0]["message"]["content"].strip())

        trip_data = json.loads(response["choices"][0]["message"]["content"].strip())
        trip_plans = trip_data.get("trip_plans", [])

        updated_trip_plans = scrape_and_update_trip_plans(trip_plans)
        print("Total distance:", calculate_total_distance(updated_trip_plans))
        return {"trip_plans": updated_trip_plans}

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}


def get_lat_lng(address):
    # URL của API và API key của bạn
    api_key = distance_matrix_api_key
    base_url = "https://api.distancematrix.ai/maps/api/geocode/json"

    url = f"{base_url}?address={address}&key={api_key}"
    print("\n url : ", url)
    response = requests.get(url)
    print("\n response : ", response)

    if response.status_code == 200:
        data = response.json()

        if data["status"] == "OK":
            lat = data["result"][0]["geometry"]["location"]["lat"]
            lng = data["result"][0]["geometry"]["location"]["lng"]
            print("\n lat : ", lat, " lng : ", lng)
            return lat, lng
        else:
            print("Không tìm thấy kết quả cho địa chỉ.")
            return None, None
    else:
        print(f"Yêu cầu không thành công. Mã lỗi: {response.status_code}")
        return None, None


def scrape_and_update_trip_plans(trip_plans):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Sử dụng headless=True cho tự động
        page = browser.new_page()

        for trip in trip_plans:
            for detail in trip["details"]:
                location = detail.get("location", "")
                province_city = detail.get("province_city", "")
                search_query = f"{location}, {province_city}".strip(", ")
                try:
                    page.goto("https://maps.google.com", timeout=60000)

                    search_box = page.locator('//input[@id="searchboxinput"]')
                    search_box.fill(search_query)
                    page.press('//input[@id="searchboxinput"]', "Enter")

                    page.wait_for_load_state("networkidle", timeout=60000)

                    has_location_list = page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).count()
                    if has_location_list > 0:
                        page.hover(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        )
                        page.click(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        )
                        page.wait_for_load_state("networkidle", timeout=60000)

                    try:
                        address = page.locator(
                            '//div[contains(@class, "Io6YTe")]'
                        ).first.inner_text(timeout=10000)
                    except Exception:
                        address = "N/A"

                    try:
                        latitude, longitude = get_lat_lng(address)
                    except Exception:
                        latitude = "N/A"
                        longitude = "N/A"

                    detail["address"] = address
                    detail["latitude"] = latitude
                    detail["longitude"] = longitude

                    print(
                        f"Location: {location}, Address: {address}, Latitude: {latitude}, Longitude: {longitude}"
                    )
                except Exception as e:
                    print(f"Failed to process location '{location}': {e}")
                    detail["address"] = "Error"
                    detail["latitude"] = "Error"
                    detail["longitude"] = "Error"

        browser.close()

    return trip_plans


def is_within_vietnam(lat, lon):
    lat_min = 8.179
    lat_max = 23.393
    lon_min = 102.144
    lon_max = 109.465
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max


def calculate_total_distance(trip_plans):
    for trip in trip_plans:
        origins = []
        for detail in trip["details"]:
            lat = detail["latitude"]
            lon = detail["longitude"]
            if is_within_vietnam(lat, lon):
                origins.append(f"{lat},{lon}")
            else:
                print(
                    f"Coordinate ({lat}, {lon}) is outside of Vietnam and will be excluded."
                )

        if not origins:
            print(f"No valid origins for trip suggestion: {trip['suggestion']}")
            continue

        destination = (
            f"{trip['details'][-1]['latitude']},{trip['details'][-1]['longitude']}"
        )

        origins_str = "|".join(origins)
        url = f"https://api-v2.distancematrix.ai/maps/api/distancematrix/json?origins={origins_str}&destinations={destination}&key={distance_matrix_api_key}"
        print(url)
        response = requests.get(url)
        print(response)
        data = response.json()
        print(data)
        if data["status"] == "OK":
            total_distance = 0
            for row in data["rows"]:
                for element in row["elements"]:
                    if element["status"] == "OK":
                        total_distance += element["distance"]["value"]  # in meters

            total_distance_km = total_distance / 1000
            trip["total_distance_km"] = total_distance_km
            print(f"{trip['suggestion']}: {total_distance_km:.2f} km")
        else:
            print(f"Error fetching data for trip suggestion: {trip['suggestion']}")
            trip["total_distance_km"] = 0


@app.route("/")
def home():
    return "Welcome to the Trip Planner API!"


@app.route("/api/trip-planner", methods=["POST"])
def trip_planner():
    try:
        input_data = request.json
        result = suggest_trip_plan(input_data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
