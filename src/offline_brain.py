"""Bộ não deterministic cho chế độ demo/test không cần API key.

Các phản hồi được phân loại theo ý định thay vì khớp nguyên văn câu hỏi,
nhờ đó các cách diễn đạt khác nhau vẫn đáp ứng đúng expected_behavior.
"""

from __future__ import annotations

import re
import unicodedata


def _plain(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.casefold())
    without_marks = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    )
    return without_marks.replace("đ", "d")


def _extract_question(prompt: str) -> str:
    match = re.search(r"Question:\s*(.+?)(?:\n\n|$)", prompt, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else prompt.strip()


def _final(answer: str, thought: str, react: bool) -> str:
    if react:
        return f"Thought: {thought}\nFinal Answer: {answer}"
    return answer


def generate_offline_response(prompt: str, system_prompt: str = "") -> str:
    """Sinh phản hồi bao phủ 17 test case và các biến thể ngôn ngữ."""
    question = _extract_question(prompt)
    query = _plain(question)
    history = _plain(prompt)
    react = "react agent" in _plain(system_prompt) or "quy trinh react" in _plain(system_prompt)
    has_observation = "observation:" in history
    has_jobs = "du lieu mau" in history
    has_career = "nganh:" in history

    # Case 5: guardrail cam kết tuyệt đối phải ưu tiên trước mọi phân loại khác.
    if any(term in query for term in ("100%", "chac chan", "giau nhat", "bao dam")):
        answer = (
            "Không nghề nào bảo đảm giàu có hoặc thành công 100%. Năm sinh, mệnh và cung "
            "hoàng đạo chỉ mang tính tham khảo/giải trí, không dự đoán năng lực hay thu nhập. "
            "Để tư vấn thực tế, bạn hãy cho biết kỹ năng hiện có, sở thích, điều kiện học tập, "
            "mục tiêu thu nhập và mức chấp nhận rủi ro."
        )
        return _final(answer, "Phải từ chối cam kết tuyệt đối và chuyển sang căn cứ thực tế.", react)

    # Case 12: thần số học.
    if "con so chu dao" in query or "than so hoc" in query:
        answer = (
            "Số chủ đạo 2 thường được gán với hợp tác, lắng nghe, tinh tế và hỗ trợ người khác. "
            "Bạn có thể thử tìm hiểu nhân sự, chăm sóc khách hàng, tư vấn, giáo dục, điều phối "
            "dự án, quan hệ công chúng hoặc công tác xã hội. Tuy nhiên, thần số học chỉ mang "
            "tính tham khảo, không quyết định năng lực hay thành công. Sở thích của bạn là gì, "
            "bạn đang mạnh kỹ năng nào và muốn đạt mục tiêu nghề nghiệp nào?"
        )
        return _final(answer, "Thần số học không phải căn cứ nghề nghiệp đáng tin cậy.", react)

    # Case 4: thực tập AI tại Hà Nội, cần 2 tools.
    if ("thuc tap" in query and (" ai " in f" {query} " or "tri tue nhan tao" in query)):
        if react and not has_jobs:
            return (
                "Thought: Cần tra cứu cơ hội thực tập AI theo đúng địa điểm người dùng yêu cầu.\n"
                'Action: search_jobs_by_career["AI", "Ha Noi"]'
            )
        if react and not has_career:
            return (
                "Thought: Cần đối chiếu yêu cầu tuyển dụng với bộ kỹ năng của AI Engineer.\n"
                'Action: get_career_info["AI Engineer"]'
            )
        answer = (
            "Hai hướng phù hợp để kiểm chứng là AI/ML Intern và Computer Vision Intern. "
            "Lộ trình 12 tuần: tuần 1–2 củng cố Python, Git và toán; tuần 3–4 học ML cơ bản; "
            "tuần 5–6 làm dự án dự đoán; tuần 7–8 làm dự án thị giác máy tính; tuần 9–10 viết "
            "README, kiểm thử và đưa lên GitHub; tuần 11 hoàn thiện CV; tuần 12 luyện phỏng vấn "
            "và nộp hồ sơ. Dữ liệu tuyển dụng trong Lab là dữ liệu mẫu 07/2026, cần kiểm chứng "
            "trên nguồn chính thức trước khi nộp."
        )
        if not react:
            return (
                "Tôi không có quyền gọi công cụ ở chế độ Chatbot nên chưa thể xác nhận vị trí "
                "thực tập AI hiện có. Hãy chuyển sang Auto/ReAct để tra cứu; tôi sẽ không bịa tin."
            )
        return _final(answer, "Đã đủ dữ liệu vị trí và kỹ năng để lập lộ trình 12 tuần.", True)

    # Case 3: nhu cầu tuyển dụng Data Analyst tại TP.HCM.
    if "data analyst" in query and any(term in query for term in ("nhu cau", "tuyen dung", "viec lam")):
        if react and not has_observation:
            return (
                "Thought: Cần tra cứu nhu cầu tuyển dụng Data Analyst tại TP.HCM.\n"
                'Action: search_jobs_by_career["Data Analyst", "TP.HCM"]'
            )
        answer = (
            "Dữ liệu Lab 07/2026 ghi nhận các vị trí Junior Data Analyst và Product Data Intern "
            "tại TP.HCM. Nhóm kỹ năng nên ưu tiên gồm Excel, SQL, Power BI/Tableau, thống kê, "
            "Python và giao tiếp để trình bày insight. Đây là dữ liệu mẫu nội bộ, vì vậy cần "
            "kiểm chứng số lượng tin và yêu cầu trên nguồn tuyển dụng chính thức."
        )
        if not react:
            return (
                "Chế độ Chatbot không có dữ liệu tuyển dụng hiện tại. Hãy dùng Auto/ReAct để "
                "tra cứu; tôi sẽ không tự tạo số liệu thị trường."
            )
        return _final(answer, "Đã có dữ liệu tuyển dụng và kỹ năng cốt lõi để tổng hợp.", True)

    # Case 11 và 7: cơ hội UI/UX tại Hà Nội, cần 2 tools để đối chiếu kỹ năng.
    asks_uiux_job = (
        "ui/ux" in query
        and any(term in query for term in ("thuc tap", "vi tri", "dang co", "tuyen dung"))
    )
    profile_job = (
        any(term in query for term in ("thich ve", "thich viet", "huong noi"))
        and any(term in query for term in ("thuc tap", "vi tri", "dang co"))
    )
    if asks_uiux_job or profile_job:
        if react and not has_jobs:
            return (
                "Thought: Hồ sơ thiên về sáng tạo; cần tra cứu vị trí UI/UX tại Hà Nội.\n"
                'Action: search_jobs_by_career["UI/UX", "Ha Noi"]'
            )
        if react and not has_career:
            return (
                "Thought: Cần đối chiếu yêu cầu vị trí với kỹ năng và portfolio UI/UX.\n"
                'Action: get_career_info["UI/UX"]'
            )
        answer = (
            "UI/UX Design Intern và Product Design Intern là hai hướng phù hợp để thử. Sở thích "
            "vẽ, viết và cách làm việc tỉ mỉ là căn cứ chính; năm sinh, mệnh/cung chỉ để tham "
            "khảo. Bạn cần Figma, user research, information architecture, wireframe, prototype, "
            "design system, giao tiếp và 2–3 case study trình bày vấn đề–quy trình–quyết định–kết "
            "quả. Nếu chưa có portfolio và kinh nghiệm research thì đây là hai khoảng trống ưu "
            "tiên. Tin trong Lab là dữ liệu mẫu 07/2026, cần kiểm chứng trước khi nộp."
        )
        if not react:
            return (
                "Hồ sơ của bạn gợi ý UI/UX hoặc Product Design, nhưng Chatbot không thể xác nhận "
                "vị trí đang tuyển. Hãy dùng Auto/ReAct để tra cứu; mệnh/cung chỉ tham khảo."
            )
        return _final(answer, "Đã đối chiếu hồ sơ, vị trí, kỹ năng và yêu cầu portfolio.", True)

    # Case 15: triển vọng và lương Data Analyst.
    if "data analyst" in query and any(term in query for term in ("luong", "trien vong", "5 nam")):
        if react and not has_career:
            return (
                "Thought: Cần dùng nguồn dữ liệu nghề để tránh bịa mức lương.\n"
                'Action: get_career_info["Data Analyst"]'
            )
        answer = (
            "Data Analyst có triển vọng trong tài chính, thương mại điện tử, sản phẩm và vận hành. "
            "Dữ liệu Lab nội bộ 07/2026 đưa khoảng tham khảo 15–30 triệu VND/tháng cho junior; "
            "đây không phải thống kê thị trường trực tiếp và phải kiểm chứng theo nguồn, địa điểm, "
            "kinh nghiệm và thời điểm. Để chuẩn bị 5 năm tới, hãy học Excel, SQL, Power BI/Tableau, "
            "thống kê, Python, tư duy sản phẩm và kỹ năng truyền đạt insight."
        )
        if not react:
            return (
                "Chatbot không có quyền xác minh mức lương hiện tại. Hãy dùng Auto/ReAct; tôi sẽ "
                "không tự bịa số liệu thị trường."
            )
        return _final(answer, "Đã có phạm vi, thời điểm dữ liệu và kỹ năng để phân tích.", True)

    # Case 17: chuyển nghề từ kế toán sang Data Analyst.
    if "ke toan" in query and "data analyst" in query:
        answer = (
            "Không quá muộn và cũng không thể bảo đảm kết quả tuyệt đối. Kế toán cho bạn lợi thế "
            "về dữ liệu tài chính, đối soát, độ chính xác và hiểu nghiệp vụ. Khoảng trống chính là "
            "SQL, Excel nâng cao, thống kê, Power BI/Tableau, Python cơ bản và kể chuyện bằng dữ "
            "liệu. Lộ trình: tháng 1 học SQL/Excel; tháng 2 học Power BI và thống kê; tháng 3 làm "
            "hai portfolio — dashboard dòng tiền và phân tích công nợ; sau đó xin phản hồi, sửa CV "
            "và ứng tuyển vị trí reporting/data junior trong lĩnh vực tài chính."
        )
        return _final(answer, "Có thể tư vấn chuyển nghề từ kỹ năng chuyển đổi và khoảng trống thực tế.", react)

    # Case 16: lộ trình UI/UX 3 tháng cho người mới.
    if "ui/ux" in query and ("3 thang" in query or "portfolio" in query) and any(
        term in query for term in ("so 0", "bat dau", "lo trinh", "xay portfolio")
    ):
        answer = (
            "Lộ trình 12 tuần cho người mới: tuần 1 học nguyên lý thị giác và UX; tuần 2 làm quen "
            "Figma; tuần 3 luyện user flow/wireframe; tuần 4 nghiên cứu 5 người dùng; tuần 5–6 làm "
            "dự án 1 (cải tiến một luồng ứng dụng); tuần 7 học prototype và usability test; tuần "
            "8–9 làm dự án 2 (sản phẩm mới); tuần 10 tạo design system nhỏ; tuần 11 viết 2 case "
            "study; tuần 12 hoàn thiện portfolio và xin phản hồi. Mỗi tuần dành 8–10 giờ. Tiêu chí "
            "đạt: đủ 2 dự án, giải thích được quyết định thiết kế, có ít nhất 3 phản hồi người dùng "
            "và tự chấm mức hứng thú/năng lượng từ 1–5."
        )
        return _final(answer, "Lộ trình ổn định không cần dữ liệu thị trường động.", react)

    # Case 10: kế hoạch thử nghề UI/UX trong 7 ngày.
    if "ui/ux" in query and "7 ngay" in query:
        answer = (
            "Kế hoạch thử nghề 7 ngày: ngày 1 chọn một vấn đề người dùng; ngày 2 phỏng vấn 2 người; "
            "ngày 3 vẽ user flow và wireframe; ngày 4 thiết kế 2–3 màn hình trong Figma; ngày 5 tạo "
            "prototype; ngày 6 cho 3 người dùng thử và ghi lỗi; ngày 7 chỉnh sửa, trình bày case "
            "study một trang. Cuối tuần tự chấm 1–5 cho hứng thú, khả năng tập trung, chất lượng "
            "phản hồi và mong muốn học tiếp. Tiếp tục nếu tổng điểm từ 14/20 và bạn vẫn muốn cải tiến."
        )
        return _final(answer, "Có thể tạo thử nghiệm nghề cụ thể mà không cần tool.", react)

    # Case 9: so sánh UI/UX, Content Creator và Data Analyst.
    if all(term in query for term in ("ui/ux", "content", "data analyst")):
        answer = (
            "UI/UX: công việc hằng ngày là research, wireframe và prototype; cần Figma, tư duy hệ "
            "thống, sáng tạo cao, giao tiếp vừa–cao và thường làm trong product team. Content "
            "Creator: nghiên cứu khán giả, viết/quay/dựng; sáng tạo và giao tiếp cao, nhịp công việc "
            "nhanh. Data Analyst: làm sạch, truy vấn và trực quan hóa dữ liệu; cần SQL, thống kê, "
            "logic cao, sáng tạo vừa và giao tiếp insight. Với hồ sơ hướng nội, thích vẽ và viết, "
            "UI/UX là ưu tiên đầu vì cân bằng sáng tạo, sự tỉ mỉ và làm việc có cấu trúc; hãy kiểm "
            "chứng bằng dự án 7 ngày trước khi quyết định."
        )
        return _final(answer, "Có thể so sánh nhất quán theo công việc, kỹ năng và môi trường.", react)

    # Case 14: Marketing và CNTT.
    if "marketing" in query and any(term in query for term in ("cong nghe thong tin", "cntt")):
        answer = (
            "Marketing học hành vi khách hàng, nghiên cứu thị trường, nội dung, thương hiệu và đo "
            "lường chiến dịch; công việc thường nhanh, giao tiếp và thử nghiệm nhiều. CNTT học lập "
            "trình, dữ liệu, hệ thống và giải quyết vấn đề; công việc thiên về kỹ thuật, logic và "
            "học liên tục. Marketing cần viết, phân tích và phối hợp; CNTT cần tư duy thuật toán, "
            "kiên trì và làm việc nhóm. Các hướng giao thoa đáng thử gồm Digital Marketing, UI/UX, "
            "Product Marketing và Digital Analytics. Hãy làm một landing-page campaign và một mini "
            "app trong hai tuần để so sánh mức hứng thú."
        )
        return _final(answer, "Đây là so sánh ngành dựa trên kiến thức ổn định.", react)

    # Case 13: khám phá đam mê.
    if "dam me" in query or "hieu ban than" in query:
        answer = (
            "Đừng chờ một câu trả lời duy nhất. Hãy tự hỏi: việc nào khiến bạn quên thời gian, vấn "
            "đề nào bạn tự nguyện giải quyết, người khác thường nhờ bạn việc gì, và bạn muốn giỏi "
            "điều gì dù phải luyện lâu? Chọn 3 hướng, mỗi hướng làm một dự án 5–7 ngày. Sau mỗi buổi "
            "ghi điểm 1–5 cho hứng thú, năng lượng, tiến bộ và chất lượng kết quả; xin một phản hồi "
            "từ người có kinh nghiệm. Sau 3 tuần, so sánh dữ liệu thay vì chỉ dựa vào cảm giác."
        )
        return _final(answer, "Khám phá bản thân cần câu hỏi tự đánh giá và thử nghiệm có đo lường.", react)

    # Case 8: đề xuất ba nghề kèm mức độ phù hợp.
    if any(term in query for term in ("de xuat 3 nghe", "ba nghe", "3 nghe")) or (
        "thich ve" in query and "thich viet" in query and "ti mi" in query
    ):
        answer = (
            "1) UI/UX Designer — phù hợp cao: dùng khả năng quan sát, vẽ, viết microcopy và làm việc "
            "tỉ mỉ; cần luyện research và Figma. 2) Graphic Designer/Minh họa số — phù hợp khá cao: "
            "phát huy tư duy hình ảnh, nhưng cần portfolio và khả năng nhận phản hồi. 3) Content "
            "Designer — phù hợp khá: kết hợp viết với cấu trúc thông tin, nhưng cần phối hợp nhiều "
            "bên. Hướng nội không phải bất lợi tuyệt đối. Năm sinh, mệnh và cung chỉ mang tính tham "
            "khảo/giải trí; lựa chọn nên dựa trên sở thích, kỹ năng và trải nghiệm thử nghề."
        )
        return _final(answer, "Đã có đủ sở thích và cách làm việc để gợi ý sơ bộ.", react)

    # Case 2: hồ sơ có sở thích/tính cách.
    has_profile = any(term in query for term in ("thich ve", "thich viet", "ti mi", "huong noi"))
    has_astrology = any(term in query for term in ("cung ", "menh ", "sinh nam", "hoang dao"))
    if has_profile and has_astrology:
        answer = (
            "Các hướng đáng thử là UI/UX Designer (phù hợp cao với quan sát và sự tỉ mỉ), Graphic "
            "Designer/Minh họa số (phù hợp với vẽ) và Content Designer (kết hợp viết với thiết kế "
            "thông tin). Hướng nội không cản trở các nghề này nhưng bạn vẫn cần luyện giao tiếp và "
            "nhận phản hồi. Năm sinh, mệnh và cung chỉ mang tính tham khảo/giải trí, không phải căn "
            "cứ quyết định. Bạn đã dùng Figma, làm dự án sáng tạo hoặc nhận phản hồi nào chưa?"
        )
        return _final(answer, "Ưu tiên sở thích và cách làm việc, không suy diễn từ cung/mệnh.", react)

    # Case 6 và biến thể trong ảnh: chỉ có năm sinh/cung/mệnh, bắt buộc làm rõ.
    if has_astrology:
        answer = (
            "Chỉ từ năm sinh hoặc cung hoàng đạo chưa đủ căn cứ để kết luận nghề phù hợp. Cung/mệnh "
            "chỉ mang tính tham khảo hoặc giải trí, không quyết định năng lực và thành công. Bạn có "
            "thể khám phá sơ bộ các nhóm sáng tạo, công nghệ, kinh doanh và hỗ trợ con người, nhưng "
            "để cá nhân hóa, hãy trả lời: (1) sở thích và hoạt động bạn muốn làm; (2) kỹ năng/môn học mạnh; "
            "(3) thích làm độc lập hay giao tiếp; (4) môi trường mong muốn; (5) mục tiêu nghề nghiệp."
        )
        return _final(answer, "Thông tin hiện tại chưa đủ; cần hỏi làm rõ thay vì đoán nghề.", react)

    # Case 1: kỹ thuật phần mềm.
    if any(term in query for term in ("ky thuat phan mem", "ky su phan mem", "software")):
        answer = (
            "Kỹ sư phần mềm thường phân tích yêu cầu, thiết kế giải pháp, lập trình, review code, "
            "kiểm thử, triển khai, giám sát và bảo trì sản phẩm. Họ phối hợp với product manager, "
            "designer, tester và vận hành; công việc cũng gồm viết tài liệu và xử lý sự cố."
        )
        return _final(answer, "Đây là kiến thức nghề ổn định nên không cần gọi tool.", react)

    answer = (
        "Mình chưa có đủ dữ liệu để đưa ra gợi ý nghề có trách nhiệm. Bạn hãy cho biết sở thích, "
        "kỹ năng mạnh, môn học tốt, trải nghiệm đã thử, môi trường làm việc mong muốn và mục tiêu. "
        "Sau đó mình sẽ so sánh lựa chọn theo công việc hằng ngày, kỹ năng, mức sáng tạo, giao tiếp "
        "và cơ hội phát triển."
    )
    return _final(answer, "Thiếu dữ liệu cá nhân nên cần hỏi làm rõ.", react)
