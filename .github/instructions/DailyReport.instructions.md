---
applyTo: '**'

---
applyTo: '**'

ĐỊNH DẠNG BÁO CÁO DAILYREPORT (DailyReport.instructions.md)

**1. Các task đã làm trong hôm nay**
Task 1: [Tên task 1]
- Status: [Completed/Pending]
- Progress: [x%]
- Start date: [yyyy-mm-dd]
- End date: [yyyy-mm-dd hoặc dự kiến]
Task 2: [Tên task 2]
- Status: [Completed/Pending]
- Progress: [x%]
- Start date: [yyyy-mm-dd]
- End date: [yyyy-mm-dd hoặc dự kiến]
... (Lặp lại cho các task khác)

**2. Các task sẽ làm vào ngày mai**
Task 1: [Mô tả task/nghiên cứu/nghỉ chờ...]
- Target Progress: [x%]
- End date (dự kiến): [yyyy-mm-dd]
Task 2: [Mô tả task/nghiên cứu/nghỉ chờ...]
- Target Progress: [x%]
- End date (dự kiến): [yyyy-mm-dd]
... (Lặp lại cho các task khác)

**3. Khó khăn / vướng mắc (nếu có)**
- [Liệt kê các khó khăn, vướng mắc, vấn đề kỹ thuật, rate limit, lỗi, v.v.]

**4. Tài nguyên và công cụ hỗ trợ**
Nền tảng, phần mềm:
1. [link hoặc tên nền tảng/phần mềm]
2. ...

Tài liệu tham khảo:
1. [link hoặc mô tả tham khảo]
2. ...

File báo cáo & source code:
1. [Tên file báo cáo]
2. [Tên repository/source code, link hoặc mô tả]
3. ...

**5. Lời cảm ơn/kết thúc**
- [Lời cảm ơn, chúc, ký tên...]

**Lưu ý:**
- Báo cáo nên trình bày rõ ràng, có phân chia mục, dễ đọc, dễ theo dõi tiến độ.
- Nếu có nhiều file notebook, nên mô tả ngắn gọn nội dung từng file.
- Có thể bổ sung mục “Lưu ý khác” nếu cần giải thích thêm về cách làm việc, lý do chia nhỏ file, v.v.
- Đảm bảo thông tin task, tiến độ, ngày tháng chính xác và cập nhật.

---

ĐỊNH DẠNG BÁO CÁO DAILYREPORT (DailyReport.instructions.example.md)

---

**1. Các task đã làm trong hôm nay**
Task 1: Refactor và hoàn thiện adapter cho Ollama và OpenAI (backend/app/adapters/ollama_adapter.py, openai_adapter.py)
Status: Completed
Progress: 100%
Start date: 2025-07-21
End date: 2025-07-21
Task 2: Bổ sung, chuẩn hóa factory chọn LLM/embedding provider (backend/app/services/llm_provider_factory.py)
Status: Completed
Progress: 100%
Start date: 2025-07-21
End date: 2025-07-21
Task 3: Cải tiến Milvus client, chuẩn hóa interface và debug (backend/app/db/milvus_client.py)
Status: Completed
Progress: 100%
Start date: 2025-07-21
End date: 2025-07-21
Task 4: Refactor, bổ sung class AsyncEmbeddingFunction, DocumentProcessor, IngestionService (backend/app/services/ingestion_service.py)
Status: Completed
Progress: 100%
Start date: 2025-07-21
End date: 2025-07-21

**2. Các task sẽ làm vào ngày mai**
Task 1: Viết thêm test cho các adapter và service ingestion mới refactor
Target Progress: 50%
End date (dự kiến): 2025-07-22
Task 2: Kiểm thử tích hợp end-to-end với Milvus và Ollama qua Docker Compose
Target Progress: 50%
End date (dự kiến): 2025-07-22

**3. Khó khăn / vướng mắc (nếu có)**
- Một số interface của Milvus và Ollama chưa thống nhất, cần kiểm thử thực tế để đảm bảo tương thích.
- Việc mock/test Milvus cần chú ý khi chạy pytest (đã có conftest.py hỗ trợ).

**4. Tài nguyên và công cụ hỗ trợ**
Nền tảng, phần mềm:
1. Ngrok (ngrok.com)
2. Docker Desktop
3. Postman

Tài liệu tham khảo:
Hướng dẫn custom instructions cho GitHub Copilot: https://docs.github.com/en/copilot/how-tos/custom-instructions/adding-repository-custom-instructions-for-github-copilot
https://docs.trychroma.com/docs/embeddings/embedding-functions
https://docs.trychroma.com/integrations/embedding-models/openai

File báo cáo & source code:
1. Daily Report 2025-Jul-17.docx (file báo cáo)
2. Repository GitHub (hiện tại đã có thể chạy, nhưng chưa thật sự hoàn thiện): https://github.com/MinhThuan2406/RAGChatbot

**5. Lời cảm ơn/kết thúc**
Cảm ơn anh đã xem qua báo cáo công việc hàng ngày của em. Chúc anh một buổi tối tốt lành. Em mong anh có thời gian để xem qua source code, chạy thử và review cho em để em cải thiện hơn ạ.
ThuanNM, AI/ML Intern.