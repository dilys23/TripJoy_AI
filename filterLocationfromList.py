import openai
import csv

# Thay thế bằng API key của bạn
openai.api_key = "my_api_key"


# Hàm đọc dữ liệu từ file CSV
def read_schedule_from_csv(file_path):
    schedule = ""
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Bỏ qua tiêu đề
            for row in reader:
                schedule += f"{row[1]}\n"  # Lấy nội dung lịch trình
    except Exception as e:
        print(f"Lỗi khi đọc file CSV: {e}")
    return schedule

# Hàm sử dụng OpenAI API để lọc các địa điểm
def extract_locations_from_schedule(schedule_text):
    prompt = f"""
    Tôi có một danh sách lịch trình du lịch như sau:
    {schedule_text}

    Hãy liệt kê tất cả các địa điểm trong từng lịch trình. Mỗi địa điểm cần được tách biệt rõ ràng. Trả kết quả dưới dạng danh sách, ví dụ:
    - Cầu Vàng (Golden Bridge)
    - Bà Nà Hills
    - Hải Sản Biển Đà Nẵng
    ...
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )
        locations = response['choices'][0]['message']['content'].strip()
        return locations
    except openai.error.OpenAIError as e:
        print(f"Lỗi từ OpenAI API: {e}")
    return ""

# Ghi danh sách địa điểm vào file CSV
def save_locations_to_csv(locations, output_file):
    try:
        with open(output_file, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Địa điểm"])  # Tiêu đề cột
            for location in locations.split("\n"):
                writer.writerow([location.strip()])
        print(f"Kết quả đã được lưu vào file '{output_file}'.")
    except Exception as e:
        print(f"Lỗi khi ghi file CSV: {e}")

# Đọc lịch trình từ file CSV gốc
schedule_file = "trip_plans.csv"  # Đường dẫn file CSV
schedule_text = read_schedule_from_csv(schedule_file)

# Gọi API để trích xuất địa điểm
if schedule_text:
    locations = extract_locations_from_schedule(schedule_text)
    if locations:
        print("Danh sách địa điểm đã được trích xuất:")
        print(locations)

        # Lưu địa điểm vào file CSV mới
        output_file = "locations.csv"
        save_locations_to_csv(locations, output_file)
    else:
        print("Không có địa điểm nào được trích xuất.")
else:
    print("Không thể đọc được dữ liệu từ file CSV.")
