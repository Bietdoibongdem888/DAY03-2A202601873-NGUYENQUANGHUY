# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
## Career Guidance Agent | Nguyễn Quang Huy — 2A202601873

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | Cần suy luận nhiều bước: phân tích kỹ năng → đối chiếu yêu cầu → gợi ý khóa học → vẽ lộ trình. Mỗi bước phụ thuộc kết quả bước trước. |
| 🛠️ **Tool Interaction** | `5/5` | Cần 4 tools: get_job_market, check_skills, search_courses, get_career_path. Mỗi tool truy xuất dữ liệu thực tế khác nhau. |
| 🔀 **Dynamic Decision** | `4/5` | Agent phải quyết định gọi tool nào dựa trên câu hỏi. Ví dụ: "thiếu kỹ năng gì" → check_skills; "học gì" → search_courses. |
| ⏳ **Long Horizon** | `4/5` | Quy trình có thể kéo dài 3-5 bước cho câu hỏi phức tạp (market → skills → courses → career path). |
| **TỔNG ĐIỂM FIT** | **18/20** | **KẾT LUẬN: BÀI TOÁN RẤT NÊN DÙNG REACT AGENT!** |

---

## 🔍 2. SO SÁNH PHẢN HỒI (TEST CASE #3)

**Câu hỏi**: *"Thị trường việc làm ngành Data Science hiện nay ra sao và cần học những khóa học gì để bắt đầu?"*

### 🤖 Chatbot Baseline:
* **Phản hồi**: *"Tôi là Chatbot tư vấn sự nghiệp. Ngành Data Science đang phát triển mạnh với nhu cầu cao. Bạn nên học Python, SQL, Machine Learning..."*
* **Nhận xét**: Trả lời chung chung, không có số liệu thực tế về mức lương, không biết khóa học cụ thể nào đang có sẵn.

### 🧠 ReAct Agent:
* **Step 1**: 
  * Thought: Người dùng muốn biết thông tin thị trường Data Science. Cần gọi tool.
  * Action: `get_job_market['Data Science']`
  * Observation: *"Data Science: Lương TB 25-40M VND/tháng (Junior), Nhu cầu tăng 35%/năm..."*
* **Step 2**: 
  * Thought: Đã có thông tin thị trường. Tiếp theo cần gợi ý khóa học.
  * Action: `search_courses['Machine Learning']`
  * Observation: *"Khóa học ML: 1. Andrew Ng ML Specialization (Coursera) FREE..."*
* **Final Answer**: *"Ngành Data Science đang rất hot với mức lương 25-40M Junior, nhu cầu tăng 35%/năm. Bạn nên bắt đầu với khóa Andrew Ng ML trên Coursera (FREE) hoặc IBM Data Science Professional."*
* **Nhận xét**: Hoàn thành xuất sắc — vừa có số liệu thực, vừa có khóa học cụ thể.

---

## 🔍 3. SO SÁNH PHẢN HỒI (TEST CASE #4 — Multi-Tool)

**Câu hỏi**: *"Em biết Python và SQL, muốn trở thành Data Scientist. Kỹ năng em còn thiếu gì và lộ trình thăng tiến từ fresher như thế nào?"*

### 🤖 Chatbot Baseline:
* **Phản hồi**: *"Để trở thành Data Scientist bạn cần học thêm Statistics, Machine Learning... Lộ trình: thực tập → junior → senior."*
* **Nhận xét**: Không biết chính xác thiếu bao nhiêu %, không có số liệu lương cụ thể theo từng cấp.

### 🧠 ReAct Agent:
* **Step 1**: 
  * Thought: Người dùng muốn cả đối chiếu kỹ năng và lộ trình.
  * Action: `check_skills['Python, SQL', 'Data Scientist']`
  * Observation: *"Độ khớp: 33% (2/6 kỹ năng). Thiếu: Machine Learning, Statistics, Data Visualization, Communication."*
* **Step 2**: 
  * Thought: Đã có kết quả đối chiếu kỹ năng. Cần thêm lộ trình thăng tiến.
  * Action: `get_career_path['fresher']`
  * Observation: *"Fresher (8-12M) → Junior (15-25M sau 1 năm) → Mid (25-40M sau 2-3 năm) → Senior (40-60M sau 4-6 năm)."*
* **Final Answer**: *"Với Python và SQL bạn đã có 33% nền tảng. Cần bổ sung ML, Statistics, Data Viz, Communication. Lộ trình: Fresher (8-12M) → Junior (15-25M) → Mid DS (25-40M). Hãy làm project thực tế!"*
* **Nhận xét**: Kết hợp 2 tools cho câu trả lời toàn diện, có % khớp kỹ năng và số lương thực tế.

---

## 🔍 4. TEST EDGE CASE (#5)

**Câu hỏi**: *"Tra cứu thị trường việc làm ở thành phố Atlantis cho nghề Phù Thủy Cấp Cao năm 3026."*

### 🤖 Chatbot Baseline:
* **Phản hồi**: *"Xin lỗi, tôi không có thông tin về thành phố Atlantis hoặc nghề Phù Thủy."*
* **Nhận xét**: Từ chối lịch sự — đúng behavior.

### 🧠 ReAct Agent:
* **Step 1**: Action: `get_job_market['Atlantis']` → Observation: *"Chưa có dữ liệu chi tiết cho lĩnh vực 'Atlantis'."*
* **Step 2**: Thought: Tool không tìm thấy dữ liệu.
* **Final Answer**: *"Xin lỗi, tôi không tìm thấy thông tin cho yêu cầu của bạn."*
* **Nhận xét**: Guardrail hoạt động — Agent thử gọi tool, nhận lỗi, trả về thông báo lịch sự mà không crash.

---

## 📋 5. TỔNG KẾT TRACE LOG

| Test # | Category | Chatbot | ReAct Agent | Tools Called | Guardrail |
|:---:|:---|:---|:---|:---|:---:|
| 1 | 🟢 Simple | Static knowledge | Static knowledge | None | N/A |
| 2 | 🟢 Simple | General advice | General advice | None | N/A |
| 3 | 🟡 Multi-step | Generic answer | Specific data + courses | get_job_market, search_courses | N/A |
| 4 | 🟡 2+ Tools | Vague roadmap | % skill match + salary path | check_skills, get_career_path | N/A |
| 5 | 🔴 Edge Case | Polite refusal | Tool error → polite refusal | get_job_market | Error handled gracefully |

---

## 🏁 KẾT LUẬN

- **Chatbot (Level 2)**: Chỉ trả lời từ kiến thức tĩnh, không có số liệu thực tế. Phù hợp cho câu hỏi tư vấn chung chung.
- **ReAct Agent (Level 3)**: Gọi tools để lấy dữ liệu thực (mức lương, % khớp kỹ năng, khóa học cụ thể). Trả về câu trả lời chính xác và cá nhân hóa.
- **Guardrails**: MAX_ITERATIONS=5 hoạt động tốt. Edge case được xử lý an toàn.
