const { Configuration, OpenAIApi } = require("openai");

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});

const openai = new OpenAIApi(configuration);

async function suggestTripPlan(input) {
  const prompt = `
  Bạn là một trợ lý du lịch. Người dùng cung cấp thông tin về chuyến đi, và bạn sẽ gợi ý nhiều lịch trình khác nhau. 

  Thông tin người dùng cung cấp:
  - Điểm khởi hành: ${input.startLocation}
  - Điểm đến: ${input.destination}
  - Số ngày: ${input.days} ngày
  - Ngân sách: ${input.budget} VNĐ
  - Phương tiện: ${input.transport}

  Hãy tạo 3 lịch trình khác nhau, mỗi lịch trình theo một chủ đề:
  1. Khám phá thiên nhiên.
  2. Du lịch ẩm thực.
  3. Văn hóa - lịch sử.

  Mỗi lịch trình phải chi tiết và kèm thông tin chi phí, ăn uống, lưu trú.
  `;

  try {
    const response = await openai.createCompletion({
      model: "text-davinci-003",
      prompt,
      max_tokens: 3000,
      temperature: 0.7,
    });

    console.log("Các lịch trình gợi ý:");
    console.log(response.data.choices[0].text.trim());
  } catch (error) {
    console.error("Lỗi khi gọi API:", error.message);
  }
}

const userInput = {
  startLocation: "Huế",
  destination: "Đà Nẵng",
  days: 3,
  budget: 3000000,
  transport: "xe máy",
};

suggestTripPlan(userInput);
