"""
🛠️ TOOL REGISTRY & SCHEMAS (Role 2: Tool & Spec Engineer)
Career Guidance Agent — tools for job market, skills, courses, career paths.
"""

def get_job_market(field: str) -> str:
    """
    Tra cứu thông tin thị trường việc làm cho một lĩnh vực.
    Args: field (str): Lĩnh vực (vd: 'Data Science', 'Software Engineering')
    Returns: str: Mức lương, nhu cầu tuyển dụng, xu hướng
    """
    data = {
        "data science": "Data Science: Lương TB 25-40M VND/tháng (Junior), 50-80M (Senior). Nhu cầu tăng 35%/năm. Top skills: Python, SQL, Machine Learning, Statistics.",
        "software engineering": "Software Engineering: Lương TB 20-35M VND/tháng (Junior), 45-70M (Senior). Nhu cầu ổn định. Top skills: Java, Python, Cloud, System Design.",
        "artificial intelligence": "AI/ML Engineer: Lương TB 30-50M VND/tháng (Junior), 60-100M (Senior). Nhu cầu tăng 45%/năm. Top skills: Python, Deep Learning, NLP, Computer Vision.",
        "cybersecurity": "Cybersecurity: Lương TB 25-40M VND/tháng (Junior), 50-90M (Senior). Nhu cầu tăng 30%/năm. Top skills: Network Security, Ethical Hacking, Cloud Security.",
        "product management": "Product Management: Lương TB 30-45M VND/tháng (Mid), 60-90M (Senior). Nhu cầu tăng 20%/năm. Top skills: UX Research, Data Analysis, Stakeholder Management.",
        "ui/ux design": "UI/UX Design: Lương TB 20-30M VND/tháng (Junior), 40-60M (Senior). Nhu cầu tăng 25%/năm. Top skills: Figma, User Research, Prototyping.",
        "software engineering": "Software Engineering: Lương TB 20-35M VND/tháng (Junior), 45-70M (Senior). Nhu cầu ổn định. Top skills: Java, Python, Cloud, System Design. Top companies: FPT, VNG, Momo, VNPay. Career paths: Backend, Frontend, Fullstack, DevOps, Mobile.",
    }
    for key, val in data.items():
        if key in field.lower():
            return val
    return f"Chưa có dữ liệu chi tiết cho lĩnh vực '{field}'. Gợi ý: Data Science, Software Engineering, AI, Cybersecurity, Product Management, UI/UX Design."


def check_skills(skills_text: str, job_title: str) -> str:
    """
    Đối chiếu kỹ năng hiện có với yêu cầu của vị trí mục tiêu.
    Args: skills_text (str): Danh sách kỹ năng (vd: 'Python, SQL, Excel')
          job_title (str): Vị trí mục tiêu (vd: 'Data Scientist')
    Returns: str: Kết quả đối chiếu + kỹ năng còn thiếu
    """
    skills = [s.strip().lower() for s in skills_text.split(",")]
    
    job_requirements = {
        "data scientist": ["python", "sql", "machine learning", "statistics", "data visualization", "communication"],
        "software engineer": ["python", "java", "git", "data structures", "algorithms", "system design"],
        "ai engineer": ["python", "deep learning", "tensorflow/pytorch", "nlp", "computer vision", "mlops"],
        "product manager": ["data analysis", "ux research", "stakeholder management", "roadmap planning", "sql"],
        "ux designer": ["figma", "user research", "prototyping", "usability testing", "design systems"],
    }
    
    required = job_requirements.get(job_title.lower(), [])
    if not required:
        return f"Chưa có dữ liệu yêu cầu kỹ năng cho vị trí '{job_title}'. Hãy thử: Data Scientist, Software Engineer, AI Engineer, Product Manager, UX Designer."
    
    matched = [s for s in skills if any(r in s or s in r for r in required)]
    missing = [r for r in required if not any(r in s or s in r for s in skills)]
    
    match_pct = len(matched) / len(required) * 100 if required else 0
    
    result = f"Đối chiếu kỹ năng cho '{job_title}':\n"
    result += f"Độ khớp: {match_pct:.0f}% ({len(matched)}/{len(required)} kỹ năng)\n"
    result += f"Kỹ năng đã có: {', '.join(matched).title() if matched else 'Chưa có'}\n"
    result += f"Kỹ năng cần bổ sung: {', '.join(missing).title() if missing else 'Không thiếu!'}"
    return result


def search_courses(field: str) -> str:
    """
    Tìm kiếm khóa học/chứng chỉ phù hợp cho lĩnh vực.
    Args: field (str): Lĩnh vực muốn học (vd: 'Machine Learning')
    Returns: str: Danh sách khóa học gợi ý kèm nền tảng
    """
    courses = {
        "machine learning": "Khóa học ML:\n1. Andrew Ng ML Specialization (Coursera) — 3 tháng, FREE audit\n2. Fast.ai Practical Deep Learning — 2 tháng, FREE\n3. Google ML Crash Course — 2 tuần, FREE",
        "data science": "Khóa học Data Science:\n1. IBM Data Science Professional (Coursera) — 6 tháng, ~$39/tháng\n2. DataCamp Data Scientist Track — 3 tháng, ~$25/tháng\n3. Kaggle Learn — FREE, tự học",
        "web development": "Khóa học Web Dev:\n1. The Odin Project — 6-12 tháng, FREE\n2. Full Stack Open (Helsinki Uni) — 3 tháng, FREE\n3. freeCodeCamp — tự học, FREE",
        "cybersecurity": "Khóa học Cybersecurity:\n1. Google Cybersecurity Certificate (Coursera) — 6 tháng, ~$39/tháng\n2. CompTIA Security+ — tự học + thi ~$370\n3. TryHackMe — hands-on, FREE tier available",
        "cloud computing": "Khóa học Cloud:\n1. AWS Cloud Practitioner — 1 tháng, FREE training + thi $100\n2. Google Cloud Skills Boost — FREE tier\n3. Azure Fundamentals AZ-900 — FREE learning path",
        "software engineering": "Khóa học Software Engineering:\n1. The Odin Project — 6-12 tháng, FREE\n2. Full Stack Open (Helsinki Uni) — 3 tháng, FREE\n3. CS50 (Harvard) — 12 tuần, FREE\n4. Clean Code (Udemy) — ~$15 khi sale",
    }
    for key, val in courses.items():
        if key in field.lower():
            return val
    return f"Chưa có danh sách khóa học cho '{field}'. Gợi ý: Machine Learning, Data Science, Web Development, Cybersecurity, Cloud Computing."


def get_career_path(current_role: str) -> str:
    """
    Gợi ý lộ trình thăng tiến cho một vị trí.
    Args: current_role (str): Vị trí hiện tại hoặc mục tiêu (vd: 'Junior Developer')
    Returns: str: Lộ trình thăng tiến 3-5 năm
    """
    paths = {
        "junior developer": "Lộ trình Junior Developer:\nYear 1-2: Junior Dev (15-25M) -> Year 2-3: Mid Developer (25-40M) -> Year 3-5: Senior Dev (40-60M) -> Year 5+: Tech Lead / Architect (60-90M). Focus: fundamentals -> system design -> leadership.",
        "data analyst": "Lộ trình Data Analyst:\nYear 1-2: Junior Analyst (15-20M) -> Year 2-3: Data Analyst (20-30M) -> Year 3-5: Senior Analyst / BI Lead (30-45M) -> Year 5+: Data Scientist / Analytics Manager (45-70M). Focus: SQL -> Python -> ML -> Strategy.",
        "fresher": "Lộ trình từ Fresher:\nYear 1: Fresher/Trainee (8-12M) -> Year 1-2: Junior (15-25M) -> Year 2-4: Mid-level (25-40M) -> Year 4-6: Senior (40-60M) -> Year 6+: Lead/Manager (60M+). Tip: Chọn 1 chuyên môn + 1 domain để đi sâu.",
        "student": "Lộ trình từ Sinh viên:\nNăm 3-4: Thực tập (3-6M) -> Tốt nghiệp: Fresher (8-12M) -> +1 năm: Junior (15-25M) -> +2 năm: Mid (25-40M). Tip: Làm project thực tế + đóng góp open source + network qua LinkedIn.",
        "software engineer": "Lộ trình Software Engineer:\nYear 1-2: Junior Dev (15-25M) -> Year 2-3: Mid Developer (25-40M) -> Year 3-5: Senior Dev (40-60M) -> Year 5+: Tech Lead / Architect (60-90M). Focus: fundamentals -> system design -> leadership. Popular stacks: MERN, Java Spring, .NET, Python Django.",
        "backend developer": "Lộ trình Backend Developer:\nYear 1-2: Junior Backend (15-22M) → Year 2-3: Mid Backend (25-35M) → Year 3-5: Senior Backend (35-55M) → Year 5+: Backend Architect (55-80M). Core: REST APIs → Microservices → System Design. Stack: Java Spring, Node.js, Python Django, Go.",
        "frontend developer": "Lộ trình Frontend Developer:\nYear 1-2: Junior Frontend (12-20M) → Year 2-3: Mid Frontend (22-35M) → Year 3-5: Senior Frontend (35-55M) → Year 5+: Frontend Architect (50-75M). Core: HTML/CSS → React/Vue → Performance → Design Systems.",
    }
    for key, val in paths.items():
        if key in current_role.lower():
            return val
    return f"Chưa có lộ trình cụ thể cho '{current_role}'. Gợi ý: Junior Developer, Data Analyst, Fresher, Student."


AVAILABLE_TOOLS = {
    "get_job_market": get_job_market,
    "check_skills": check_skills,
    "search_courses": search_courses,
    "get_career_path": get_career_path,
    "web_search": web_search,
}

def web_search(query: str) -> str:
    """
    Tìm kiếm thông tin thực tế trên web cho bất kỳ câu hỏi nào.
    Args: query (str): Từ khóa tìm kiếm
    Returns: str: Kết quả tìm kiếm
    """
    try:
        from duckduckgo_search import DDGS
        results = list(DDGS().text(query, max_results=3))
        if not results:
            return f"Không tìm thấy kết quả cho '{query}'."
        output = []
        for r in results:
            output.append(f"- {r['title']}: {r['body'][:200]}")
        return "\n".join(output)
    except Exception as e:
        return f"Lỗi tìm kiếm: {str(e)}"
