"""
TOOL REGISTRY & SCHEMAS (Danh cho Role 2: Tool Engineer)
Dinh nghia cac cong cu (Tools) cho Chatbot Dinh Huong Su Nghiep.
"""

from __future__ import annotations

import re
from typing import Any


TOOL_DATA_SOURCE = "mock"
SENSITIVE_INPUT_RE = re.compile(
    r"(?:\b(?:api[_ -]?key|password|mat[_ ]?khau|mật[_ ]?khẩu|cccd)\b|"
    r"\bsk-[A-Za-z0-9_-]{12,}\b|\b\d{12}\b)",
    flags=re.IGNORECASE,
)


def contains_sensitive_data(value: str) -> bool:
    """Phat hien bi mat/PII khong can thiet truoc khi gui input vao tool."""
    return bool(SENSITIVE_INPUT_RE.search(value))


def _tool_error(code: str, message: str) -> str:
    return f"LOI: {message}\nerror_code={code}"


def _mock_result(payload: str) -> str:
    """Gan nhan bat buoc de UI/Agent khong trinh bay mock nhu du lieu that."""
    return f'status=ok\nsource="{TOOL_DATA_SOURCE}"\n{payload}'


def _validate_text(value: str, field_name: str) -> tuple[str, str | None]:
    """Chuan hoa input; tra LOI nghiep vu thay vi lam tool crash."""
    if not isinstance(value, str):
        return "", _tool_error("INVALID_INPUT_TYPE", f"Tham so '{field_name}' phai la chuoi.")
    value = value.strip()
    if not value:
        return "", _tool_error("INVALID_INPUT_EMPTY", f"Tham so '{field_name}' khong duoc de trong.")
    if len(value) > 100:
        return "", _tool_error("INVALID_INPUT_LENGTH", f"Tham so '{field_name}' vuot qua 100 ky tu.")
    if contains_sensitive_data(value):
        return "", _tool_error(
            "SENSITIVE_INPUT",
            f"Tham so '{field_name}' co the chua du lieu nhay cam; hay che du lieu truoc.",
        )
    return value, None


def get_career_info(career_name: str) -> str:
    """
    Tra cuu thong tin chi tiet ve mot nganh nghe cu the.

    Args:
        career_name (str): Ten nganh nghe (VD: 'Lap trinh vien', 'Bac si', 'Kien truc su')

    Returns:
        str: Thong tin chi tiet gom mo ta, muc luong, ky nang yeu cau, trien vong
    """
    career_name, error = _validate_text(career_name, "career_name")
    if error:
        return error
    data = {
        "lap trinh vien": (
            "Nganh: Lap trinh vien (Software Developer)\n"
            "- Mo ta: Thiet ke, phat trien va bao tri phan mem, ung dung web, di dong.\n"
            "- Muc luong: 15-40 trieu VND/thang (1-3 nam kn), 40-80 trieu VND/thang (3-5 nam kn).\n"
            "- Ky nang: Python, JavaScript, SQL, Giai thuat, Tieng Anh, Lam viec nhom.\n"
            "- Trien vong: Rat cao - chuyen doi so, AI, Cloud dang phat trien manh."
        ),
        "bac si": (
            "Nganh: Bac si (Medical Doctor)\n"
            "- Mo ta: Chan benh, dieu tri, cham soc suc khoe benh nhan.\n"
            "- Muc luong: 20-50 trieu VND/thang (bac si da khoa), 50-150 trieu VND/thang (chuyen khoa).\n"
            "- Ky nang: Kien thuc y hoc, tu duy phan tich, giao tiep, kien nhan.\n"
            "- Trien vong: On dinh - nhu cau cham soc suc khoe ngay cang tang."
        ),
        "kien truc su": (
            "Nganh: Kien truc su (Architect)\n"
            "- Mo ta: Thiet ke, lap ke hoach va giam sat thi cong cac cong trinh xay dung.\n"
            "- Muc luong: 15-35 trieu VND/thang (moi ra truong), 40-100 trieu VND/thang (nhieu nam kn).\n"
            "- Ky nang: AutoCAD, Revit, SketchUp, Tu duy tham my, Quan ly du an.\n"
            "- Trien vong: Kha - do thi hoa va phat trien ha tang lien tuc."
        ),
        "nhan vien marketing": (
            "Nganh: Nhan vien Marketing\n"
            "- Mo ta: Xay dung chien luoc, to chuc chien dich quang ba, quan tri thuong hieu.\n"
            "- Muc luong: 10-25 trieu VND/thang (junior), 30-60 trieu VND/thang (senior/manager).\n"
            "- Ky nang: Content SEO, Facebook/Google Ads, Phan tich du lieu, Tieng Anh.\n"
            "- Trien vong: Cao - Marketing so dang phat trien manh me."
        ),
        "data analyst": (
            "Nganh: Data Analyst\n"
            "- Mo ta: Thu thap, lam sach, phan tich va truc quan hoa du lieu de ho tro quyet dinh.\n"
            "- Muc luong tham khao: 15-30 trieu VND/thang (junior), tuy nguon va thoi diem.\n"
            "- Ky nang: Excel, SQL, Power BI/Tableau, thong ke, Python va giao tiep.\n"
            "- Trien vong: Cao trong tai chinh, thuong mai dien tu, san pham va van hanh."
        ),
        "ai engineer": (
            "Nganh: AI Engineer\n"
            "- Mo ta: Xay dung, danh gia va trien khai mo hinh AI/ML.\n"
            "- Ky nang: Python, dai so, xac suat, Machine Learning, Git, API va MLOps co ban.\n"
            "- Lo trinh intern: Python -> ML co ban -> 2 du an portfolio -> luyen phong van.\n"
            "- Trien vong: Cao nhung yeu cau nen tang ky thuat va kha nang tu hoc."
        ),
        "ui/ux": (
            "Nganh: UI/UX Designer\n"
            "- Mo ta: Nghien cuu nguoi dung, thiet ke luong, wireframe, prototype va kiem thu.\n"
            "- Ky nang: Figma, user research, information architecture, prototyping va giao tiep.\n"
            "- Portfolio: Can 2-3 case study trinh bay van de, quy trinh, quyet dinh va ket qua.\n"
            "- Trien vong: Kha trong cong ty san pham, agency va startup."
        ),
    }
    key = career_name.lower().strip()
    for k, v in data.items():
        if k in key or key in k:
            return _mock_result(v)
    return _tool_error(
        "NO_DATA",
        f"Chua co du lieu cho nganh nghe '{career_name}'. "
        "Vui long thu tu khoa khac (VD: Lap trinh vien, Bac si, Kien truc su, Nhan vien Marketing).",
    )


def suggest_careers_by_interest(interest: str) -> str:
    """
    Goi y cac nganh nghe phu hop voi so thich / ky nang cua nguoi dung.

    Args:
        interest (str): So thich hoac ky nang (VD: 'thich may tinh', 'thich giao tiep', 'gioi toan')

    Returns:
        str: Danh sach cac nganh nghe phu hop
    """
    interest, error = _validate_text(interest, "interest")
    if error:
        return error
    data = {
        "may tinh": (
            "Cac nganh phu hop voi so thich may tinh / cong nghe:\n"
            "1. Lap trinh vien (Software Developer)\n"
            "2. Chuyen vien An ninh mang (Cybersecurity)\n"
            "3. Khoa hoc du lieu (Data Scientist)\n"
            "4. Chuyen vien AI/Machine Learning\n"
            "5. Quan tri he thong (System Admin)"
        ),
        "giao tiep": (
            "Cac nganh phu hop voi so thich giao tiep / tuong tac:\n"
            "1. Nhan vien Marketing\n"
            "2. Chuyen vien Quan he cong chung (PR)\n"
            "3. Nhan vien Kinh doanh (Sales)\n"
            "4. Huong dan vien Du lich\n"
            "5. Chuyen vien Nhan su (HR)"
        ),
        "toan": (
            "Cac nganh phu hop voi nguoi gioi Toan / tu duy logic:\n"
            "1. Ky su Phan tich du lieu (Data Analyst)\n"
            "2. Chuyen vien Tai chinh - Ngan hang\n"
            "3. Kieu toan (Actuary)\n"
            "4. Lap trinh vien (thuat toan can ban)\n"
            "5. Nghien cuu khoa hoc"
        ),
        "nghe thuat": (
            "Cac nganh phu hop voi so thich nghe thuat / sang tao:\n"
            "1. Thiet ke do hoa (Graphic Designer)\n"
            "2. Nhiep anh gia\n"
            "3. Kien truc su (Architect)\n"
            "4. Thiet ke thoi trang\n"
            "5. Game Designer / Animator"
        ),
        "suc khoe": (
            "Cac nganh phu hop voi so thich cham soc suc khoe:\n"
            "1. Bac si (Medical Doctor)\n"
            "2. Y ta / Dieu duong\n"
            "3. Duoc si (Pharmacist)\n"
            "4. Chuyen vien vat ly tri lieu\n"
            "5. Chuyen gia dinh duong"
        ),
    }
    key = interest.lower().strip()
    for k, v in data.items():
        if k in key:
            return _mock_result(v)
    return _mock_result(
        "Goi y chung ve dinh huong nghe nghiep:\n"
        "1. Khoi Cong nghe thong tin (IT): Lap trinh, Data, AI\n"
        "2. Khoi Kinh doanh: Marketing, Tai chinh, Nhan su\n"
        "3. Khoi Y - Duoc: Bac si, Dieu duong, Duoc si\n"
        "4. Khoi Thiet ke - Sang tao: Thiet ke hoa, Kien truc, Game\n"
        "Hay thu mot so tu kha nhu: 'may tinh', 'giao tiep', 'toan', 'nghe thuat', 'suc khoe'."
    )


def search_jobs_by_career(career: str, location: str = "Ha Noi") -> str:
    """
    Tim kiem viec lam theo nganh nghe va dia diem.

    Args:
        career (str): Nganh nghe (VD: 'Lap trinh vien', 'Marketing')
        location (str): Dia diem lam viec (VD: 'Ha Noi', 'TP.HCM', 'Da Nang')

    Returns:
        str: Danh sach tin tuyen dung
    """
    career, error = _validate_text(career, "career")
    if error:
        return error
    location, error = _validate_text(location, "location")
    if error:
        return error
    jobs = {
        "lap trinh vien": {
            "Ha Noi": (
                f"Viec lam {career} tai {location}:\n"
                "1. Full-stack Developer - FPT Software - 25-40 trieu VND\n"
                "2. Backend Developer - VNPT - 20-35 trieu VND\n"
                "3. Frontend Developer - Vingroup - 18-30 trieu VND"
            ),
            "TP.HCM": (
                f"Viec lam {career} tai {location}:\n"
                "1. Java Developer - TMA Solutions - 22-38 trieu VND\n"
                "2. React Native Dev - VNG Corp - 25-45 trieu VND\n"
                "3. DevOps Engineer - KMS Technology - 30-50 trieu VND"
            ),
        },
        "marketing": {
            "Ha Noi": (
                f"Viec lam {career} tai {location}:\n"
                "1. Digital Marketing Specialist - VCCorp - 15-25 trieu VND\n"
                "2. Content Manager - VnExpress - 18-30 trieu VND\n"
                "3. SEO Specialist - VNG - 12-20 trieu VND"
            ),
            "TP.HCM": (
                f"Viec lam {career} tai {location}:\n"
                "1. Marketing Manager - Unilever - 30-50 trieu VND\n"
                "2. Brand Executive - Masan Group - 15-25 trieu VND\n"
                "3. Performance Marketing - Shopee - 18-35 trieu VND"
            ),
        },
        "data analyst": {
            "TP.HCM": (
                f"Du lieu mau {career} tai {location} (cap nhat noi bo 07/2026):\n"
                "1. Junior Data Analyst - Cong ty Ban Le A - Excel, SQL, Power BI\n"
                "2. Product Data Intern - Cong ty Cong Nghe B - SQL, thong ke, giao tiep\n"
                "Luu y: Du lieu Lab deterministic, can kiem chung tren nguon tuyen dung chinh thuc."
            ),
            "Ha Noi": (
                f"Du lieu mau {career} tai {location} (cap nhat noi bo 07/2026):\n"
                "1. Data Analyst Intern - Cong ty Tai Chinh C - Excel, SQL, Tableau\n"
                "Luu y: Du lieu Lab deterministic, can kiem chung tren nguon tuyen dung chinh thuc."
            ),
        },
        "ai": {
            "Ha Noi": (
                f"Du lieu mau thuc tap {career} tai {location} (cap nhat noi bo 07/2026):\n"
                "1. AI/ML Intern - Lab Cong Nghe A - Python, ML co ban, Git\n"
                "2. Computer Vision Intern - Startup B - Python, PyTorch, xu ly anh\n"
                "Luu y: Khong phai tin tuyen dung truc tiep; can kiem chung truoc khi nop."
            ),
        },
        "ui/ux": {
            "Ha Noi": (
                f"Du lieu mau thuc tap {career} tai {location} (cap nhat noi bo 07/2026):\n"
                "1. UI/UX Design Intern - Product Studio A - Figma, wireframe, prototype\n"
                "2. Product Design Intern - Startup B - research, design system, portfolio\n"
                "Luu y: Khong phai tin tuyen dung truc tiep; can kiem chung truoc khi nop."
            ),
        },
    }
    career_key = career.lower().strip()
    location_key = location.lower().strip()
    for ck, locations in jobs.items():
        if ck in career_key or career_key in ck:
            for lk, result in locations.items():
                if lk.lower() in location_key:
                    return _mock_result(result)
            # fallback: return first location
            first = list(locations.values())[0]
            return _mock_result(
                first
                + f"\n(Khong co du lieu cho {location}; day la du lieu minh hoa tai dia diem mac dinh)"
            )
    return _tool_error(
        "NO_DATA",
        f"Chua co du lieu tuyen dung cho nganh '{career}'. "
        "Hien tai ho tro: Lap trinh vien, Marketing, Data Analyst, AI, UI/UX.",
    )


def get_certification_info(career: str) -> str:
    """
    Tra cuu cac chung chi/chung nhan can thiet cho mot nganh nghe.

    Args:
        career (str): Ten nganh nghe (VD: 'Lap trinh vien', 'Bac si')

    Returns:
        str: Danh sach chung chi khuyen nghi
    """
    career, error = _validate_text(career, "career")
    if error:
        return error
    certs = {
        "lap trinh vien": (
            "Chung chi can thiet cho Lap trinh vien:\n"
            "1. TOEIC 750+/IELTS 6.5+ (Tieng Anh)\n"
            "2. Chuyen nghanh: AWS Certified, Google Cloud, Azure\n"
            "3. Chuyen mon: Oracle Java Cert, Microsoft MCSD\n"
            "4. Data: Google Data Analytics, IBM Data Science\n"
            "5. AI/ML: TensorFlow Developer, AWS ML Specialty"
        ),
        "bac si": (
            "Chung chi can thiet cho Bac si:\n"
            "1. Chung chi Hanh nghe Y khoa (bat buoc)\n"
            "2. TOEIC 700+/IELTS 6.0+ (Tieng Anh y khoa)\n"
            "3. Chuyen khoa: ACC (ACLS), ATLS (Cap cuu)\n"
            "4. Chung chi theo chuyen nganh (Noi, Ngoai, San...)"
        ),
        "kien truc su": (
            "Chung chi can thiet cho Kien truc su:\n"
            "1. Chung chi Hanh nghe Kien truc (bat buoc)\n"
            "2. Chung chi Quan ly du an (PMP - khuyen nghi)\n"
            "3. Chung chi Phan mem: Autodesk Certified User (AutoCAD/Revit)\n"
            "4. LEED AP (Thiet ke xanh - quoc te)"
        ),
        "marketing": (
            "Chung chi can thiet cho Nhan vien Marketing:\n"
            "1. Google Digital Marketing Certification\n"
            "2. Facebook Blueprint (Meta Certified)\n"
            "3. Google Analytics Individual Qualification\n"
            "4. HubSpot Content Marketing & Inbound\n"
            "5. TOEIC 750+/IELTS 6.5+ (Tieng Anh)"
        ),
        "data analyst": (
            "Chung chi tham khao cho Data Analyst:\n"
            "1. Google Data Analytics\n"
            "2. Microsoft Power BI Data Analyst\n"
            "3. Portfolio SQL va dashboard quan trong hon viec chi gom chung chi."
        ),
        "ai": (
            "Chung chi tham khao cho AI Engineer:\n"
            "1. Machine Learning Specialization\n"
            "2. TensorFlow Developer/AWS ML (khong bat buoc)\n"
            "3. Du an va kha nang giai thich mo hinh la bang chung quan trong."
        ),
        "ui/ux": (
            "UI/UX khong bat buoc chung chi. Uu tien portfolio 2-3 case study, "
            "Figma, user research, prototype va kha nang trinh bay quyet dinh."
        ),
    }
    key = career.lower().strip()
    for k, v in certs.items():
        if k in key or key in k:
            return _mock_result(v)
    return _tool_error(
        "NO_DATA",
        f"Chua co du lieu chung chi cho nganh '{career}'. "
        "Hien tai ho tro: Lap trinh vien, Bac si, Kien truc su, Marketing.",
    )


def compare_careers(career_1: str, career_2: str) -> str:
    """
    So sanh hai nganh nghe ve luong, ky nang, trien vong.

    Args:
        career_1 (str): Nganh thu nhat (VD: 'Lap trinh vien')
        career_2 (str): Nganh thu hai (VD: 'Bac si')

    Returns:
        str: Bang so sanh chi tiet
    """
    career_1, error = _validate_text(career_1, "career_1")
    if error:
        return error
    career_2, error = _validate_text(career_2, "career_2")
    if error:
        return error
    if career_1.casefold() == career_2.casefold():
        return _tool_error("DUPLICATE_INPUT", "Hai nganh nghe can so sanh phai khac nhau.")
    first = get_career_info(career_1)
    second = get_career_info(career_2)
    if first.startswith("LOI:") or second.startswith("LOI:"):
        return _tool_error(
            "NO_DATA",
            "Khong du du lieu mock cho ca hai nganh; khong tao bang so sanh suy doan.",
        )
    return _mock_result(
        f"SO SANH DU LIEU MINH HOA: {career_1} vs {career_2}\n"
        f"--- {career_1} ---\n{first}\n"
        f"--- {career_2} ---\n{second}\n"
        "Luu y: So sanh chi dua tren mock dataset, khong phai du lieu thi truong hien hanh."
    )


def get_job_market(field: str) -> str:
    """Giữ Tool thị trường của origin/main dưới dạng dữ liệu mock có nhãn."""
    field, error = _validate_text(field, "field")
    if error:
        return error
    data = {
        "data science": "Data Science: luong mock 25-40M junior, 50-80M senior; ky nang Python, SQL, ML, Statistics.",
        "software engineering": "Software Engineering: luong mock 20-35M junior, 45-70M senior; ky nang Java, Python, Cloud, System Design.",
        "artificial intelligence": "AI/ML Engineer: luong mock 30-50M junior, 60-100M senior; ky nang Python, Deep Learning, NLP, Computer Vision.",
        "cybersecurity": "Cybersecurity: luong mock 25-40M junior, 50-90M senior; ky nang Network, Ethical Hacking, Cloud Security.",
        "product management": "Product Management: luong mock 30-45M mid, 60-90M senior; ky nang UX Research, Data Analysis, Stakeholder Management.",
        "ui/ux design": "UI/UX Design: luong mock 20-30M junior, 40-60M senior; ky nang Figma, User Research, Prototyping.",
    }
    for key, value in data.items():
        if key in field.casefold():
            return _mock_result(
                value
                + "\nLuu y: So lieu chi de minh hoa Lab, khong phai thong ke thi truong."
            )
    return _tool_error("NO_DATA", f"Chua co du lieu thi truong mock cho '{field}'.")


def check_skills(skills_text: str, job_title: str) -> str:
    """Đối chiếu danh sách kỹ năng với yêu cầu mock của một vị trí."""
    skills_text, error = _validate_text(skills_text, "skills_text")
    if error:
        return error
    job_title, error = _validate_text(job_title, "job_title")
    if error:
        return error
    skills = [item.strip().casefold() for item in skills_text.split(",") if item.strip()]
    requirements = {
        "data scientist": [
            "python",
            "sql",
            "machine learning",
            "statistics",
            "data visualization",
            "communication",
        ],
        "software engineer": [
            "python",
            "java",
            "git",
            "data structures",
            "algorithms",
            "system design",
        ],
        "ai engineer": [
            "python",
            "deep learning",
            "tensorflow/pytorch",
            "nlp",
            "computer vision",
            "mlops",
        ],
        "product manager": [
            "data analysis",
            "ux research",
            "stakeholder management",
            "roadmap planning",
            "sql",
        ],
        "ux designer": [
            "figma",
            "user research",
            "prototyping",
            "usability testing",
            "design systems",
        ],
    }
    required = requirements.get(job_title.casefold())
    if not required:
        return _tool_error(
            "NO_DATA",
            f"Chua co yeu cau ky nang mock cho vi tri '{job_title}'.",
        )
    matched = [
        skill
        for skill in skills
        if any(requirement in skill or skill in requirement for requirement in required)
    ]
    missing = [
        requirement
        for requirement in required
        if not any(requirement in skill or skill in requirement for skill in skills)
    ]
    match_pct = len(matched) / len(required) * 100
    return _mock_result(
        f"Doi chieu ky nang cho '{job_title}':\n"
        f"- Do khop: {match_pct:.0f}% ({len(matched)}/{len(required)})\n"
        f"- Da co: {', '.join(matched) if matched else 'Chua co'}\n"
        f"- Can bo sung: {', '.join(missing) if missing else 'Khong thieu'}"
    )


def search_courses(field: str) -> str:
    """Tra danh sách khóa học minh họa, không xác nhận giá/hiệu lực hiện hành."""
    field, error = _validate_text(field, "field")
    if error:
        return error
    courses = {
        "machine learning": "Andrew Ng ML Specialization; Fast.ai Practical Deep Learning; Google ML Crash Course.",
        "data science": "IBM Data Science Professional; DataCamp Data Scientist Track; Kaggle Learn.",
        "web development": "The Odin Project; Full Stack Open; freeCodeCamp.",
        "cybersecurity": "Google Cybersecurity Certificate; CompTIA Security+; TryHackMe.",
        "cloud computing": "AWS Cloud Practitioner; Google Cloud Skills Boost; Azure Fundamentals AZ-900.",
    }
    for key, value in courses.items():
        if key in field.casefold():
            return _mock_result(
                f"Khoa hoc minh hoa cho {field}: {value}\n"
                "Can kiem tra lai noi dung, hoc phi va hieu luc tren trang chinh thuc."
            )
    return _tool_error("NO_DATA", f"Chua co khoa hoc mock cho '{field}'.")


def get_career_path(current_role: str) -> str:
    """Tra lộ trình thăng tiến minh họa của Tool cũ từ origin/main."""
    current_role, error = _validate_text(current_role, "current_role")
    if error:
        return error
    paths = {
        "junior developer": "Junior Developer -> Mid Developer -> Senior Developer -> Tech Lead/Architect.",
        "data analyst": "Junior Analyst -> Data Analyst -> Senior Analyst/BI Lead -> Analytics Manager.",
        "fresher": "Fresher/Trainee -> Junior -> Mid-level -> Senior -> Lead/Manager.",
        "student": "Sinh vien -> Thuc tap -> Fresher -> Junior -> Mid-level.",
    }
    for key, value in paths.items():
        if key in current_role.casefold():
            return _mock_result(
                f"Lo trinh minh hoa: {value}\n"
                "Toc do thang tien phu thuoc nang luc, doanh nghiep va thi truong."
            )
    return _tool_error("NO_DATA", f"Chua co lo trinh mock cho '{current_role}'.")


def _tool_spec(
    *,
    purpose: str,
    when_to_use: str,
    when_not_to_use: str,
    inputs: dict[str, dict[str, Any]],
    output: str,
    example_input: dict[str, Any],
    example_output: str,
) -> dict[str, Any]:
    """Tao specification dong nhat; executor van giu registry callable cu."""
    return {
        "purpose": purpose,
        "when_to_use": when_to_use,
        "when_not_to_use": when_not_to_use,
        "inputs": inputs,
        "required_fields": [name for name, item in inputs.items() if item.get("required")],
        "optional_fields": [name for name, item in inputs.items() if not item.get("required")],
        "input_validation": "Chuoi 1-100 ky tu; khong rong; khong chua secret/CCCD.",
        "outputs": output,
        "error_codes": [
            "INVALID_INPUT_TYPE",
            "INVALID_INPUT_EMPTY",
            "INVALID_INPUT_LENGTH",
            "SENSITIVE_INPUT",
            "NO_DATA",
            "DUPLICATE_INPUT",
            "TOOL_NOT_FOUND",
            "TOOL_SPEC_MISSING",
            "INVALID_TOOL_INPUT",
            "SENSITIVE_TOOL_INPUT",
            "TOOL_TIMEOUT",
            "TOOL_UNAVAILABLE",
            "EMPTY_RESULT",
            "SCHEMA_MISMATCH",
            "UNSAFE_TOOL_OUTPUT",
        ],
        "error_handling": "Tra status loi co error_code; Agent khong duoc tu tao ket qua thay the.",
        "timeout_handling": "Executor timeout sau 10 giay, retry toi da 1 lan roi fallback minh bach.",
        "empty_result_handling": "Tra NO_DATA; hoi lai/doi tu khoa, khong suy doan.",
        "example_input": example_input,
        "example_output": example_output,
        "source": TOOL_DATA_SOURCE,
    }


TOOL_SPECS: dict[str, dict[str, Any]] = {
    "get_career_info": _tool_spec(
        purpose="Tra cuu mo ta, ky nang va thong tin minh hoa cua mot nghe.",
        when_to_use="Khi can doi chieu ho so/roadmap voi yeu cau cua mot nghe cu the.",
        when_not_to_use="Khong dung de khang dinh luong hay xu huong thi truong hien hanh.",
        inputs={"career_name": {"type": "string", "required": True}},
        output='Chuoi status=ok, source="mock" va thong tin nghe; hoac LOI + error_code.',
        example_input={"career_name": "Data Analyst"},
        example_output='status=ok; source="mock"; Nganh: Data Analyst...',
    ),
    "suggest_careers_by_interest": _tool_spec(
        purpose="Tra bang goi y mock theo mot nhom so thich/ky nang.",
        when_to_use="Chi khi can tra bang mapping demo cua Lab.",
        when_not_to_use="Khong dung neu LLM co the tu van truc tiep tu ho so day du.",
        inputs={"interest": {"type": "string", "required": True}},
        output='Chuoi status=ok, source="mock" va danh sach goi y.',
        example_input={"interest": "may tinh"},
        example_output='status=ok; source="mock"; Cac nganh phu hop...',
    ),
    "search_jobs_by_career": _tool_spec(
        purpose="Tim ban ghi tuyen dung minh hoa theo nghe va dia diem.",
        when_to_use="Khi nguoi dung hoi viec lam/thuc tap va da cung cap dia diem.",
        when_not_to_use="Khong dung cho kien thuc on dinh; khong trinh bay mock nhu tin dang tuyen.",
        inputs={
            "career": {"type": "string", "required": True},
            "location": {"type": "string", "required": False, "default": "Ha Noi"},
        },
        output='Chuoi status=ok, source="mock", pham vi/thoi diem va ban ghi minh hoa.',
        example_input={"career": "AI", "location": "Ha Noi"},
        example_output='status=ok; source="mock"; Du lieu mau thuc tap AI...',
    ),
    "get_certification_info": _tool_spec(
        purpose="Tra danh sach chung chi/portfolio minh hoa cho mot nghe.",
        when_to_use="Khi can kiem tra chung chi cu the trong mock dataset.",
        when_not_to_use="Khong dung de xac nhan chung chi con hieu luc hoac bat buoc hien hanh.",
        inputs={"career": {"type": "string", "required": True}},
        output='Chuoi status=ok, source="mock" va goi y; hoac NO_DATA.',
        example_input={"career": "Data Analyst"},
        example_output='status=ok; source="mock"; Google Data Analytics...',
    ),
    "compare_careers": _tool_spec(
        purpose="Doi chieu hai nghe khi mock dataset co thong tin cho ca hai.",
        when_to_use="Khi can tong hop du lieu tool cua dung hai nghe.",
        when_not_to_use="Khong dung cho ba nghe, luong hien tai, hoac khi LLM du suc so sanh kien thuc on dinh.",
        inputs={
            "career_1": {"type": "string", "required": True},
            "career_2": {"type": "string", "required": True},
        },
        output='Chuoi status=ok, source="mock" gom hai ban ghi; hoac NO_DATA.',
        example_input={"career_1": "Data Analyst", "career_2": "UI/UX"},
        example_output='status=ok; source="mock"; SO SANH DU LIEU MINH HOA...',
    ),
    "get_job_market": _tool_spec(
        purpose="Tra thong tin thi truong minh hoa cua mot linh vuc.",
        when_to_use="Khi can demo tra cuu thi truong cua Tool cu tu origin/main.",
        when_not_to_use="Khong dung nhu thong ke luong/nhu cau hien hanh.",
        inputs={"field": {"type": "string", "required": True}},
        output='Chuoi status=ok, source="mock" va du lieu minh hoa; hoac NO_DATA.',
        example_input={"field": "Data Science"},
        example_output='status=ok; source="mock"; Data Science...',
    ),
    "check_skills": _tool_spec(
        purpose="Doi chieu ky nang nguoi dung voi yeu cau vi tri trong mock dataset.",
        when_to_use="Khi da co danh sach ky nang va vi tri muc tieu ro rang.",
        when_not_to_use="Khong dung khi thieu ky nang hoac muc tieu.",
        inputs={
            "skills_text": {"type": "string", "required": True},
            "job_title": {"type": "string", "required": True},
        },
        output='Chuoi status=ok, source="mock", do khop va ky nang thieu.',
        example_input={"skills_text": "Python, SQL", "job_title": "Data Scientist"},
        example_output='status=ok; source="mock"; Do khop: 33%...',
    ),
    "search_courses": _tool_spec(
        purpose="Tra danh sach khoa hoc minh hoa theo linh vuc.",
        when_to_use="Khi can demo goi y khoa hoc sau khi da biet linh vuc.",
        when_not_to_use="Khong dung de xac nhan hoc phi, lich hoc hay chung chi hien hanh.",
        inputs={"field": {"type": "string", "required": True}},
        output='Chuoi status=ok, source="mock" va khoa hoc minh hoa; hoac NO_DATA.',
        example_input={"field": "Machine Learning"},
        example_output='status=ok; source="mock"; Andrew Ng ML Specialization...',
    ),
    "get_career_path": _tool_spec(
        purpose="Tra lo trinh thang tien minh hoa theo vai tro hien tai.",
        when_to_use="Khi can du lieu lo trinh tu mock dataset cu.",
        when_not_to_use="Khong dung de cam ket thoi gian thang tien hay thu nhap.",
        inputs={"current_role": {"type": "string", "required": True}},
        output='Chuoi status=ok, source="mock" va chuoi vai tro; hoac NO_DATA.',
        example_input={"current_role": "fresher"},
        example_output='status=ok; source="mock"; Fresher -> Junior -> Mid...',
    ),
}


# Danh sach cac tool duoc dang ky de Agent su dung
AVAILABLE_TOOLS = {
    "get_career_info": get_career_info,
    "suggest_careers_by_interest": suggest_careers_by_interest,
    "search_jobs_by_career": search_jobs_by_career,
    "get_certification_info": get_certification_info,
    "compare_careers": compare_careers,
    "get_job_market": get_job_market,
    "check_skills": check_skills,
    "search_courses": search_courses,
    "get_career_path": get_career_path,
}
