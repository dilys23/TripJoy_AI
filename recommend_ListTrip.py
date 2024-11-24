import openai
import csv

# Đảm bảo rằng bạn thay đổi OPENAI_API_KEY bằng API key của bạn
openai.api_key = ""

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
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Hoặc "gpt-4" nếu bạn muốn sử dụng GPT-4
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.7
        )

        # Lấy nội dung gợi ý từ OpenAI
        trip_plans = response['choices'][0]['message']['content'].strip()

        # Xuất kết quả ra file CSV
        with open("trip_plans.csv", mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)

            # Ghi tiêu đề
            writer.writerow(["Chủ đề", "Lịch trình"])

            # Phân chia theo 3 chủ đề và lưu vào file
            plans = trip_plans.split("\n")
            for plan in plans:
                if ":" in plan:  # Chỉ lấy các phần có định dạng "Chủ đề: Nội dung"
                    title, details = plan.split(":", 1)
                    writer.writerow([title.strip(), details.strip()])

        print("Kết quả đã được lưu vào file 'trip_plans.csv'.")

    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")

# Thông tin người dùng nhập
user_input = {
    "startLocation": "Hội An",
    "destination": "Đà Nẵng",
    "days": 3,
    "budget": 3000000,
    "transport": "xe máy"
}

# Gọi hàm để gợi ý lịch trình
suggest_trip_plan(user_input)
