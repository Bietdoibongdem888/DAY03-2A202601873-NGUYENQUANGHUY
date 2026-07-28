"""
TOOL REGISTRY & SCHEMAS (Danh cho Role 2: Tool Engineer)
Dinh nghia cac cong cu (Tools) cho Chatbot Dinh Huong Su Nghiep.
"""

def get_career_info(career_name: str) -> str:
    """
    Tra cuu thong tin chi tiet ve mot nganh nghe cu the.
    
    Args:
        career_name (str): Ten nganh nghe (VD: 'Lap trinh vien', 'Bac si', 'Kien truc su')
        
    Returns:
        str: Thong tin chi tiet gom mo ta, muc luong, ky nang yeu cau, trien vong
    """
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
    }
    key = career_name.lower().strip()
    for k, v in data.items():
        if k in key or key in k:
            return v
    return f"LOI: Chua co du lieu cho nganh nghe '{career_name}'. Vui long thu tu khoa khac (VD: Lap trinh vien, Bac si, Kien truc su, Nhan vien Marketing)."


def suggest_careers_by_interest(interest: str) -> str:
    """
    Goi y cac nganh nghe phu hop voi so thich / ky nang cua nguoi dung.
    
    Args:
        interest (str): So thich hoac ky nang (VD: 'thich may tinh', 'thich giao tiep', 'gioi toan')
        
    Returns:
        str: Danh sach cac nganh nghe phu hop
    """
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
            return v
    return (
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
    }
    career_key = career.lower().strip()
    location_key = location.lower().strip()
    for ck, locations in jobs.items():
        if ck in career_key or career_key in ck:
            for lk, result in locations.items():
                if lk.lower() in location_key:
                    return result
            # fallback: return first location
            first = list(locations.values())[0]
            return first + f"\n(Khong co du lieu cho {location}, hien thi mac dinh)"
    return f"LOI: Chua co du lieu tuyen dung cho nganh '{career}'. Hien tai ho tro: Lap trinh vien, Marketing."


def get_certification_info(career: str) -> str:
    """
    Tra cuu cac chung chi/chung nhan can thiet cho mot nganh nghe.
    
    Args:
        career (str): Ten nganh nghe (VD: 'Lap trinh vien', 'Bac si')
        
    Returns:
        str: Danh sach chung chi khuyen nghi
    """
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
    }
    key = career.lower().strip()
    for k, v in certs.items():
        if k in key or key in k:
            return v
    return f"LOI: Chua co du lieu chung chi cho nganh '{career}'. Hien tai ho tro: Lap trinh vien, Bac si, Kien truc su, Marketing."


def compare_careers(career_1: str, career_2: str) -> str:
    """
    So sanh hai nganh nghe ve luong, ky nang, trien vong.
    
    Args:
        career_1 (str): Nganh thu nhat (VD: 'Lap trinh vien')
        career_2 (str): Nganh thu hai (VD: 'Bac si')
        
    Returns:
        str: Bang so sanh chi tiet
    """
    return (
        f"SO SANH: {career_1} vs {career_2}\n"
        f"{'='*40}\n"
        f"Tieu chi          | {career_1:<20s} | {career_2:<20s}\n"
        f"{'-'*50}\n"
        f"Luong (junior)    | 15-25 trieu VND      | 15-30 trieu VND\n"
        f"Luong (senior)    | 40-80 trieu VND      | 50-150 trieu VND\n"
        f"Thoi gian dao tao | 4 nam DH + tu hoc     | 6-8 nam DH + noi tru\n"
        f"Ap luc cong viec  | Trung binh - Cao       | Rat cao\n"
        f"Tieng Anh yeu cau | TOEIC 750+            | TOEIC 700+ (Y khoa)\n"
        f"Co hoi viec lam   | Rat cao (chuyen doi so) | On dinh\n"
        f"{'='*50}\n"
        f"--> De biet them chi tiet, dung get_career_info cho tung nganh."
    )


# Danh sach cac tool duoc dang ky de Agent su dung
AVAILABLE_TOOLS = {
    "get_career_info": get_career_info,
    "suggest_careers_by_interest": suggest_careers_by_interest,
    "search_jobs_by_career": search_jobs_by_career,
    "get_certification_info": get_certification_info,
    "compare_careers": compare_careers,
}