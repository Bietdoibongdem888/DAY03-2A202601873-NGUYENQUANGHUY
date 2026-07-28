"""
🛠️ TOOL REGISTRY & SCHEMAS (Role 2: Tool & Spec Engineer)
Career Guidance Agent — tools for job market, skills, courses, career paths + web search.
All tools use fuzzy matching so the Agent doesn't need exact keywords.
"""


def _fuzzy_match(query: str, data: dict) -> str:
    """Find the best match in a dict using partial keyword matching."""
    query_lower = query.lower()
    # Score each key by how many words match
    scores = {}
    for key in data:
        score = 0
        for word in key.lower().split():
            if word in query_lower:
                score += 1
        for qword in query_lower.split():
            if qword in key.lower():
                score += 1
        if score > 0:
            scores[key] = score
    if scores:
        best = max(scores, key=scores.get)
        return data[best]
    return None


# ---- JOB MARKET ----
JOB_MARKET = {
    "software engineering software engineer developer lập trình phần mềm kỹ sư phần mềm": (
        "Software Engineering: Lương TB 20-35M VND/tháng (Junior), 45-70M (Senior). Nhu cầu ổn định. "
        "Top skills: Java, Python, Cloud, System Design. Top companies: FPT, VNG, Momo, VNPay. "
        "Career paths: Backend, Frontend, Fullstack, DevOps, Mobile."
    ),
    "data science data scientist khoa học dữ liệu": (
        "Data Science: Lương TB 25-40M VND/tháng (Junior), 50-80M (Senior). Nhu cầu tăng 35%/năm. "
        "Top skills: Python, SQL, Machine Learning, Statistics."
    ),
    "ai artificial intelligence machine learning deep learning trí tuệ nhân tạo": (
        "AI/ML Engineer: Lương TB 30-50M VND/tháng (Junior), 60-100M (Senior). Nhu cầu tăng 45%/năm. "
        "Top skills: Python, Deep Learning, NLP, Computer Vision."
    ),
    "cybersecurity bảo mật an ninh mạng": (
        "Cybersecurity: Lương TB 25-40M VND/tháng (Junior), 50-90M (Senior). Nhu cầu tăng 30%/năm. "
        "Top skills: Network Security, Ethical Hacking, Cloud Security."
    ),
    "product management quản lý sản phẩm": (
        "Product Management: Lương TB 30-45M VND/tháng (Mid), 60-90M (Senior). Nhu cầu tăng 20%/năm. "
        "Top skills: UX Research, Data Analysis, Stakeholder Management."
    ),
    "ui/ux design thiết kế": (
        "UI/UX Design: Lương TB 20-30M VND/tháng (Junior), 40-60M (Senior). Nhu cầu tăng 25%/năm. "
        "Top skills: Figma, User Research, Prototyping."
    ),
    "robotics robot tự động hóa automation kỹ sư robot": (
        "Robotics Engineer: Lương TB 25-45M VND/tháng (Junior), 50-80M (Senior). "
        "Nhu cầu tăng 30%/năm. Top skills: ROS, C++, Python, Embedded Systems, Computer Vision, Control Systems. "
        "Top companies: VinRobotics, FPT, Viettel, ABB, Samsung. "
        "Specialized paths: Industrial Robotics, Autonomous Vehicles, Medical Robotics."
    ),
    "cloud computing devops điện toán đám mây": (
        "Cloud/DevOps: Lương TB 20-35M VND/tháng (Junior), 45-70M (Senior). Nhu cầu tăng 30%/năm. "
        "Top skills: AWS/Azure/GCP, Docker, Kubernetes, Terraform, CI/CD."
    ),
    "iot internet of things": (
        "IoT Engineer: Lương TB 18-30M VND/tháng (Junior), 40-60M (Senior). Nhu cầu tăng 25%/năm. "
        "Top skills: Embedded C, Python, MQTT, Raspberry Pi, Arduino, Cloud IoT."
    ),
    "blockchain web3 crypto": (
        "Blockchain Developer: Lương TB 30-50M VND/tháng, Nhu cầu tăng 20%/năm. "
        "Top skills: Solidity, Rust, Go, Smart Contracts, Cryptography."
    ),
    "game developer lập trình game": (
        "Game Developer: Lương TB 15-25M VND/tháng (Junior), 35-55M (Senior). "
        "Top skills: C++, C#, Unity, Unreal Engine, 3D Math."
    ),
}


def get_job_market(field: str) -> str:
    result = _fuzzy_match(field, JOB_MARKET)
    if result:
        return result
    categories = "Data Science, Software Engineering, AI, Cybersecurity, Cloud/DevOps, Robotics, IoT, Blockchain, Game Dev, Product Management, UI/UX Design"
    return f"Chưa có dữ liệu cho '{field}'. Các lĩnh vực có dữ liệu: {categories}"


# ---- SKILLS MATCHING ----
SKILL_SETS = {
    "data scientist": ["python", "sql", "machine learning", "statistics", "data visualization", "communication"],
    "software engineer developer": ["python", "java", "git", "data structures", "algorithms", "system design"],
    "ai engineer machine learning": ["python", "deep learning", "tensorflow/pytorch", "nlp", "computer vision", "mlops"],
    "product manager": ["data analysis", "ux research", "stakeholder management", "roadmap planning", "sql"],
    "ux designer": ["figma", "user research", "prototyping", "usability testing", "design systems"],
    "robotics engineer": ["ros", "c++", "python", "embedded systems", "computer vision", "control systems"],
    "cybersecurity": ["network security", "ethical hacking", "linux", "scripting", "cloud security", "siem"],
    "devops cloud": ["aws/azure/gcp", "docker", "kubernetes", "terraform", "ci/cd", "linux"],
    "iot": ["embedded c", "python", "mqtt", "raspberry pi", "arduino", "cloud iot"],
    "blockchain": ["solidity", "rust", "go", "smart contracts", "cryptography", "defi"],
    "game developer": ["c++", "c#", "unity", "unreal engine", "3d math", "game physics"],
}


def check_skills(skills_text: str, job_title: str) -> str:
    user_skills = [s.strip().lower() for s in skills_text.split(",")]
    required = None
    for key in SKILL_SETS:
        if any(w in job_title.lower() for w in key.split()):
            required = SKILL_SETS[key]
            break
    if not required:
        jobs = ", ".join(SKILL_SETS.keys())
        return f"Chưa có dữ liệu cho '{job_title}'. Các vị trí hỗ trợ: {jobs}"

    matched = [s for s in user_skills if any(r in s or s in r for r in required)]
    missing = [r for r in required if not any(r in s or s in r for s in user_skills)]
    pct = len(matched) / len(required) * 100 if required else 0
    return (
        f"Đối chiếu '{job_title}':\n"
        f"Độ khớp: {pct:.0f}% ({len(matched)}/{len(required)})\n"
        f"Đã có: {', '.join(matched).title() if matched else 'Chưa có'}\n"
        f"Còn thiếu: {', '.join(missing).title() if missing else 'Đầy đủ!'}"
    )


# ---- COURSES ----
COURSES = {
    "machine learning ml ai deep learning": (
        "Khóa học ML/AI:\n1. Andrew Ng ML Specialization (Coursera) — 3 tháng, FREE audit\n"
        "2. Fast.ai Practical Deep Learning — 2 tháng, FREE\n"
        "3. Google ML Crash Course — 2 tuần, FREE"
    ),
    "data science khoa học dữ liệu": (
        "Khóa học Data Science:\n1. IBM Data Science Professional (Coursera) — 6 tháng, ~$39/tháng\n"
        "2. DataCamp Data Scientist Track — 3 tháng, ~$25/tháng\n"
        "3. Kaggle Learn — FREE, tự học"
    ),
    "web development lập trình web": (
        "Khóa học Web Dev:\n1. The Odin Project — 6-12 tháng, FREE\n"
        "2. Full Stack Open (Helsinki Uni) — 3 tháng, FREE\n"
        "3. freeCodeCamp — tự học, FREE"
    ),
    "cybersecurity bảo mật an ninh mạng": (
        "Khóa học Cybersecurity:\n1. Google Cybersecurity Certificate (Coursera) — 6 tháng, ~$39/tháng\n"
        "2. CompTIA Security+ — thi ~$370\n"
        "3. TryHackMe — hands-on, FREE tier"
    ),
    "cloud computing devops": (
        "Khóa học Cloud/DevOps:\n1. AWS Cloud Practitioner — 1 tháng, FREE + thi $100\n"
        "2. Google Cloud Skills Boost — FREE\n"
        "3. Azure Fundamentals AZ-900 — FREE"
    ),
    "robotics robot tự động hóa": (
        "Khóa học Robotics:\n1. Robotics Specialization (UPenn/Coursera) — 7 tháng, FREE audit\n"
        "2. Modern Robotics (Northwestern/Coursera) — 6 tháng, FREE audit\n"
        "3. ROS for Beginners (Udemy) — ~$15\n"
        "4. The Construct — ROS online academy, FREE tier available"
    ),
    "iot internet of things": (
        "Khóa học IoT:\n1. An Introduction to Programming the IoT (UC Irvine/Coursera) — 6 tháng\n"
        "2. IoT Specialization (Coursera) — 4 tháng\n"
        "3. Arduino Step by Step (Udemy) — ~$15"
    ),
    "blockchain web3": (
        "Khóa học Blockchain:\n1. Blockchain Specialization (Buffalo/Coursera) — 4 tháng\n"
        "2. Ethereum & Solidity (Udemy) — ~$15\n"
        "3. CryptoZombies — FREE, học qua game"
    ),
    "game development": (
        "Khóa học Game Dev:\n1. CS50's Intro to Game Development (Harvard) — 12 tuần, FREE\n"
        "2. Complete C# Unity Game Developer (Udemy) — ~$15\n"
        "3. Unreal Engine C++ Developer (Udemy) — ~$15"
    ),
}


def search_courses(field: str) -> str:
    result = _fuzzy_match(field, COURSES)
    if result:
        return result
    cats = "Machine Learning, Data Science, Web Development, Cybersecurity, Cloud/DevOps, Robotics, IoT, Blockchain, Game Development"
    return f"Chưa có khóa học cho '{field}'. Các lĩnh vực có dữ liệu: {cats}"


# ---- CAREER PATHS ----
CAREER_PATHS = {
    "junior developer software engineer fresher thực tập sinh sinh viên mới developer lập trình viên": (
        "Lộ trình Developer:\nYear 1-2: Junior (15-25M) -> Year 2-3: Mid (25-40M) -> "
        "Year 3-5: Senior (40-60M) -> Year 5+: Tech Lead/Architect (60-90M). "
        "Focus: fundamentals -> system design -> leadership. "
        "Stacks: MERN, Java Spring, .NET, Python Django."
    ),
    "data analyst data scientist": (
        "Lộ trình Data:\nYear 1-2: Junior Analyst (15-20M) -> Year 2-3: Data Analyst (20-30M) -> "
        "Year 3-5: Senior/BI Lead (30-45M) -> Year 5+: Data Scientist/Manager (45-70M). "
        "Focus: SQL -> Python -> ML -> Strategy."
    ),
    "ai engineer machine learning": (
        "Lộ trình AI/ML:\nYear 1-2: Junior ML Engineer (20-30M) -> Year 2-4: ML Engineer (30-50M) -> "
        "Year 4-6: Senior ML (50-80M) -> Year 6+: AI Lead/Research (80-120M). "
        "Focus: Python -> Deep Learning -> MLOps -> Research."
    ),
    "robotics engineer kỹ sư robot": (
        "Lộ trình Robotics:\nYear 1-2: Junior Robotics Eng (20-30M) -> Year 2-4: Mid (30-50M) -> "
        "Year 4-6: Senior (50-75M) -> Year 6+: Lead/Architect (75-100M). "
        "Focus: ROS basics -> perception & control -> system integration -> team lead. "
        "Key: Build real robot projects, contribute to ROS open source."
    ),
    "cybersecurity bảo mật": (
        "Lộ trình Cybersecurity:\nYear 1-2: SOC Analyst (15-25M) -> Year 2-4: Security Engineer (25-45M) -> "
        "Year 4-6: Senior (45-70M) -> Year 6+: CISO/Consultant (70-100M+). "
        "Focus: certs (Sec+ -> CEH -> CISSP), hands-on, threat hunting."
    ),
    "devops cloud": (
        "Lộ trình DevOps:\nYear 1-2: Junior DevOps (18-28M) -> Year 2-4: DevOps Engineer (28-45M) -> "
        "Year 4-6: Senior/SRE (45-65M) -> Year 6+: Architect (65-90M). "
        "Focus: Linux -> Docker/K8s -> CI/CD -> Cloud Architecture."
    ),
    "ui/ux design designer thiết kế": (
        "Lộ trình UI/UX:\nYear 1-2: Junior Designer (12-20M) -> Year 2-4: Mid (20-35M) -> "
        "Year 4-6: Senior (35-55M) -> Year 6+: Design Lead/Director (55-80M). "
        "Focus: fundamentals -> user research -> design systems -> strategy."
    ),
    "product manager": (
        "Lộ trình Product:\nYear 1-2: APM/Junior PM (20-30M) -> Year 2-4: PM (30-45M) -> "
        "Year 4-6: Senior PM (45-70M) -> Year 6+: Director/CPO (70-100M+). "
        "Focus: execution -> strategy -> vision -> org leadership."
    ),
    "backend developer": (
        "Lộ trình Backend:\nYear 1-2: Junior (15-22M) -> Year 2-3: Mid (25-35M) -> "
        "Year 3-5: Senior (35-55M) -> Year 5+: Architect (55-80M). "
        "Stack: Java Spring, Node.js, Python Django, Go."
    ),
    "frontend developer": (
        "Lộ trình Frontend:\nYear 1-2: Junior (12-20M) -> Year 2-3: Mid (22-35M) -> "
        "Year 3-5: Senior (35-55M) -> Year 5+: Architect (50-75M). "
        "Stack: React, Vue, Next.js, TypeScript."
    ),
    "blockchain web3": (
        "Lộ trình Blockchain:\nYear 1-2: Junior Dev (20-35M) -> Year 2-4: Mid (35-55M) -> "
        "Year 4-6: Senior (55-85M) -> Year 6+: Architect/CTO (85-120M+). "
        "Focus: Solidity/Rust -> DeFi protocols -> security -> architecture."
    ),
}


def get_career_path(current_role: str) -> str:
    result = _fuzzy_match(current_role, CAREER_PATHS)
    if result:
        return result
    roles = "Developer, Data Analyst/Scientist, AI/ML Engineer, Robotics, Cybersecurity, DevOps, UI/UX, Product Manager, Backend, Frontend, Blockchain"
    return f"Chưa có lộ trình cho '{current_role}'. Các vai trò có dữ liệu: {roles}"


def web_search(query: str) -> str:
    """Tìm kiếm thông tin thực tế trên web qua DuckDuckGo."""
    try:
        from ddgs import DDGS
        results = list(DDGS().text(query, max_results=3))
        if not results:
            return f"Không tìm thấy kết quả cho '{query}'."
        return "\n".join(f"- {r['title']}: {r['body'][:250]}" for r in results)
    except Exception as e:
        return f"Lỗi tìm kiếm: {str(e)}"


AVAILABLE_TOOLS = {
    "get_job_market": get_job_market,
    "check_skills": check_skills,
    "search_courses": search_courses,
    "get_career_path": get_career_path,
    "web_search": web_search,
}
