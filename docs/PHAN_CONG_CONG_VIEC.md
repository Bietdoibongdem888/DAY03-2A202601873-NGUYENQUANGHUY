# 📋 SỔ TAY PHÂN CÔNG & CHECKLIST THỰC HÀNH (ZERO-CONFLICT WORKFLOW)

> 💡 **Hướng dẫn**: Mỗi thành viên mở đúng file được phân công trong thư mục dự án và thực hiện checklist theo từng Mốc.

---

## 👥 1. BẢNG PHÂN VAI & FILE ĐẢM NHẬN

| Vai trò (Role)                               | File đảm nhận           | Nhiệm vụ chính                                                                                          | Người đảm nhận  |
| :-------------------------------------------- | :------------------------- | :--------------------------------------------------------------------------------------------------------- | :------------------- |
| **Role 1: Product Architect**           | `config/test_cases.json` | Định hướng bài toán & soạn bộ câu test case                                                       | 2A202601769 - Trần Tuấn Trung |
| **Role 2: Tool Engineer**               | `src/tools.py`           | Định nghĩa các công cụ (Tools) cho Agent                                                             | 2A202601689 - Diêm Công Thành |
| **Role 3: Prompt Engineer**             | `src/prompts.py`         | Viết ReAct System Prompt & phanh Guardrails                                                               | 2A202601739 - Chu Thị Yến Khanh |
| **Role 4: Core Developer / Integrator** | `src/app.py`             | **Đầu mối kéo code/file của nhóm (`git pull`), Vibe Code lắp ráp thành App hoàn chỉnh** | 2A202601873 - Nguyễn Quang Huy |
| **Role 5: Observability**               | `docs/trace_eval.md`     | Lập bảng Scoring Matrix & Soi nhật ký Trace Log                                                        | 2A202601545 - Vũ Quang Tùng <br> 2A202601737 - Nguyễn Quốc Việt |

*Note: Nếu nhóm 6 người, Role 5 tách thành 5A (Trace Analyst) và 5B (Flowchart Architect).*

> 🌟 **VAI TRÒ NÒNG NỐT CỦA ROLE 4 (ĐẦU MỐI LẮP RÁP APP HOÀN CHỈNH)**:
>
> - **Role 4** đóng vai trò là **Tổ trưởng Lắp ráp**: Sau khi các bạn Role 1, 2, 3 đẩy file lên Git, **Role 4 sẽ gõ `git pull`** để gom toàn bộ dữ liệu về máy.
> - **Role 4** sau đó dùng AI (Vibe Code) để kết nối `tools.py`, `prompts.py`, `test_cases.json` vào file `src/app.py`, biến các mảnh ghép thành **một Ứng dụng AI Agent hoàn chỉnh** cho cả nhóm chạy nghiệm thu.

---

## ⏱️ 2. CHECKLIST THỰC HÀNH THEO 4 MỐC

### 📍 MỐC 1: Định hình & Đánh giá độ phù hợp (Agentic Fit) (20 phút)

*Mục tiêu: Chứng minh bài toán này CẦN dùng Agent chứ không chỉ Chatbot.*

- [x] **Role 1 & Cả nhóm**: Đã chọn chủ đề **OreoAI – Chatbot định hướng sự nghiệp**.
- [x] **Role 5**: Đã điền bảng **Scoring Matrix** (18/20) vào `docs/trace_eval.md`.
- [x] **Role 2**: Đã khai báo 5 công cụ định hướng nghề nghiệp trong `src/tools.py`.
- [x] **Role 3**: Đã xác định các trường hợp tool có thể bị lỗi (Failure Modes).
- [x] **Role 4**: Mở Terminal gõ `python src/app.py` kiểm tra xem môi trường sẵn sàng chưa.
- [ ] 🤝 **Cả nhóm**: Gật đầu thống nhất bài toán trước khi sang Mốc 2.
- [ ] 🔄 **Đồng bộ Git Mốc 1**: Cả nhóm lưu file, đẩy code lên Git: `git add .` ➔ `git commit -m "Moc 1: Scoring Matrix & Dinh hinh"` ➔ `git push`.

---

### 📍 MỐC 2: Baseline Chatbot & Khai báo Tool Specs (30 phút)

*Mục tiêu: Thấy rõ hạn chế của Chatbot gốc và chuẩn hóa công cụ cho Agent.*

- [x] **Role 1**: Đã viết 17 **Test Cases** gồm câu đơn giản, multi-step và câu bẫy.
- [x] **Role 2**: Đã bổ sung Docstring / mô tả cho 5 hàm trong `src/tools.py`.
- [x] **Role 3**: Đã soạn `CHATBOT_BASELINE_PROMPT` trong `src/prompts.py`.
- [x] **Role 4 (Đầu mối Lắp ráp)**: Đã nối `run_baseline_chatbot()` trong `src/app.py` và chạy thử thành công trên đủ 17 test case.
- [x] **Role 5**: Đã ghi phản hồi và phân loại kết quả baseline trong `docs/trace_eval.md`.
- [ ] 🔄 **Đồng bộ Git Mốc 2**: Cả nhóm lưu file, đẩy code lên Git: `git add .` ➔ `git commit -m "Moc 2: Chatbot Baseline & Tool Specs"` ➔ `git push`.

---

### 📍 MỐC 3: ReAct Loop & Safeguards (60 phút)

*Mục tiêu: Dựng ReAct Agent suy luận Thought -> Action và cài phanh an toàn.*

- [x] **Role 3**: Đã soạn `REACT_SYSTEM_PROMPT`, `MAX_ITERATIONS = 4` và `TIMEOUT_SECONDS = 10`.
- [x] **Role 2**: Tool trả `LOI` cho input sai và không crash; đã đồng bộ Data Analyst, AI, UI/UX.
- [x] **Role 4 (Đầu mối Lắp ráp & Vibe App)**: ReAct V2 đã nối parser, executor, Observation và Guardrails; nghiệm thu 17/17 test case.
- [x] **Role 5**: Đã lưu trace một tool, hai tool, failed trace và RCA trong `docs/trace_eval.md`.
- [x] **Role 1**: Edge case và bộ attack test đều vượt qua guardrails.
- [ ] 🔄 **Đồng bộ Git Mốc 3**: Cả nhóm lưu file, đẩy code lên Git: `git add .` ➔ `git commit -m "Moc 3: ReAct Agent Loop & Safeguards"` ➔ `git push`.

---

### 📍 MỐC 4: Tương tác liên nhóm & Hybrid Flowchart (40 phút)

*Mục tiêu: Thử thách khả năng chịu lỗi trước đòn tấn công từ nhóm khác & Chấm chéo linh hoạt.*

> 💡 **HÌNH THỨC TƯƠNG TÁC (Tùy Giảng viên chỉ định)**:
>
> * 🎲 **Hình thức 1 (Gọi ngẫu nhiên)**: Giảng viên gọi ngẫu nhiên một thành viên đại diện trong bất kỳ nhóm nào lên trình chiếu App, phản biện và trả lời câu hỏi bẫy từ các nhóm khác.
> * 🔄 **Hình thức 2 (Chấm chéo nhóm)**: Giảng viên chỉ định 1 bạn đại diện (VD: Role 1 hoặc Role 5) đi sang nhóm khác để "tấn công" (dùng câu bẫy thử nghiệm Agent nhóm bạn) và chấm điểm chéo.

- [ ] ⚔️ **Đội Tấn Công (Đại diện/Học viên được gọi)**: Mang các câu test case của nhóm mình sang "xả" vào Agent của Nhóm bạn để kiểm thử khả năng chịu lỗi.
- [ ] 🛡️ **Đội Phòng Thủ**: Quan sát Agent nhóm mình phản ứng trước câu hỏi của nhóm bạn. Kiểm tra xem Guardrail bảo vệ an toàn không.
- [x] 📊 **Role 5B (hoặc Role 5)**: Đã vẽ **Hybrid Flowchart** OreoAI trong `docs/hybrid_flowchart.mermaid` thể hiện phân luồng:
  - Câu hỏi đơn giản ➔ Đi đường Chatbot path.
  - Câu hỏi phức tạp ➔ Đi đường ReAct Agent path.
- [ ] 🔄 **Đồng bộ Git Mốc 4 (Hoàn thành)**: Cả nhóm lưu file, đẩy bản hoàn chỉnh lên Git: `git add .` ➔ `git commit -m "Moc 4: Cross Audit & Hybrid Flowchart Hoan thanh"` ➔ `git push`.

---

Vì mỗi thành viên giữ đúng 1 file trong các thư mục riêng (`config/`, `src/`, `docs/`), bạn chỉ cần nhớ quy trình :

**Trước khi gõ code**: Kéo code mới của nhóm về:

```bash
   git pull
```

**Đẩy code lên cho nhóm**:

```bash
   git add .
   git commit -m "Role X: cap nhat noi dung"
   git push
```

*(Nếu push bị chặn do bạn khác push trước: Gõ `git pull` rồi `git push` lại là xong!)*
