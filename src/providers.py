"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from offline_brain import generate_offline_response

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho tất cả các LLM Provider"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env!"
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (GPT-4o, GPT-3.5-turbo, etc.)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env!"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek Provider qua API tương thích OpenAI."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "deepseek-chat"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key:
            return "[DeepSeek Error]: Chưa cấu hình DEEPSEEK_API_KEY trong file .env!"
        try:
            import openai

            client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
            )
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[DeepSeek Exception]: {str(e)}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Provider (Claude 3.5 Sonnet, Claude 3 Haiku)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: Chưa cấu hình ANTHROPIC_API_KEY trong file .env!"
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                kwargs["system"] = system_prompt
                
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            return f"[Anthropic Exception]: {str(e)}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter Provider (Hỗ trợ gọi mọi model qua OpenRouter API)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: Chưa cấu hình OPENROUTER_API_KEY trong file .env!"
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[OpenRouter API Error {res.status_code}]: {res.text}"
        except Exception as e:
            return f"[OpenRouter Exception]: {str(e)}"


class MockProvider(BaseLLMProvider):
    """Provider deterministic để demo/test toàn bộ ReAct loop không cần API key."""

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return generate_offline_response(prompt, system_prompt)

        # Legacy response table kept below as historical reference.
        text = prompt.lower()
        system = system_prompt.lower()
        is_react = "react agent" in system or "quy trình react" in system

        if not is_react:
            if any(term in text for term in ("tuyển dụng", "thực tập", "mức lương")):
                return (
                    "Tôi không có công cụ tra cứu dữ liệu thị trường hiện tại, "
                    "nên chưa thể xác nhận tin tuyển dụng hoặc mức lương. Bạn "
                    "nên kiểm chứng trên nguồn tuyển dụng chính thức."
                )
            if "con số chủ đạo" in text:
                return (
                    "Số chủ đạo 2 thường được gắn với hợp tác và lắng nghe, "
                    "nhưng chỉ mang tính tham khảo. Bạn có thể khám phá nhân sự, "
                    "giáo dục hoặc điều phối; hãy bổ sung sở thích và kỹ năng."
                )
            if "đề xuất 3 nghề" in text or (
                "nên chọn nghề gì" in text and "thích vẽ" in text
            ):
                return (
                    "Ba hướng đáng thử là UI/UX Designer, Graphic Designer và "
                    "Content Designer. Sở thích vẽ, viết và làm việc tỉ mỉ là "
                    "căn cứ chính; mệnh/cung chỉ mang tính giải trí."
                )
            if "tôi nên làm nghề gì" in text and "mệnh" in text:
                return (
                    "Chưa đủ dữ liệu để chọn nghề. Mệnh/cung chỉ tham khảo; bạn "
                    "hãy cho biết sở thích, kỹ năng mạnh, môn học tốt và mục tiêu."
                )
            if any(
                term in text
                for term in ("mệnh", "song ngư", "thần số học", "con số chủ đạo")
            ):
                return (
                    "Mệnh, cung hoàng đạo và thần số học chỉ nên xem như tham "
                    "khảo hoặc giải trí, không quyết định năng lực hay thành "
                    "công. Hãy ưu tiên sở thích, kỹ năng và mục tiêu thực tế."
                )
            if "7 ngày" in text:
                return (
                    "Kế hoạch 7 ngày: tìm hiểu nghề, nghiên cứu người dùng, vẽ "
                    "wireframe, thiết kế hai màn hình, xin phản hồi, chỉnh sửa "
                    "và tự đánh giá mức hứng thú cùng chất lượng sản phẩm."
                )
            if "3 tháng" in text:
                return (
                    "Tháng 1 học nền tảng và công cụ; tháng 2 làm hai dự án nhỏ; "
                    "tháng 3 hoàn thiện portfolio, nhận phản hồi và luyện phỏng vấn."
                )
            if "kỹ thuật phần mềm" in text:
                return (
                    "Kỹ sư phần mềm thường phân tích yêu cầu, phát triển, kiểm "
                    "thử, triển khai và bảo trì phần mềm, đồng thời phối hợp với "
                    "nhóm sản phẩm."
                )
            if "ui/ux designer, content creator" in text:
                return (
                    "UI/UX phù hợp nhất với vẽ và tư duy tỉ mỉ; Content Creator "
                    "phù hợp với viết nhưng cần giao tiếp; Data Analyst cần logic, "
                    "SQL và thống kê. Hãy thử một dự án UI/UX trước."
                )
            if "đam mê điều gì" in text:
                return (
                    "Hãy thử ba dự án nhỏ, ghi lại mức hứng thú, năng lượng, "
                    "chất lượng kết quả và phản hồi, rồi so sánh sau mỗi tuần."
                )
            if "marketing hay công nghệ thông tin" in text:
                return (
                    "Marketing thiên về khách hàng/nội dung; CNTT thiên về hệ "
                    "thống và giải quyết vấn đề. Hướng giao thoa gồm UI/UX, "
                    "Product Marketing và Digital Analytics."
                )
            if "chuyển sang data analyst" in text:
                return (
                    "Không quá muộn. Kinh nghiệm kế toán hỗ trợ tư duy số liệu; "
                    "hãy bổ sung SQL, Excel nâng cao, thống kê, Power BI và làm "
                    "portfolio phân tích dữ liệu tài chính."
                )
            return (
                "Hãy so sánh lựa chọn theo công việc hằng ngày, kỹ năng, mức "
                "sáng tạo, giao tiếp và cơ hội thử nghiệm thực tế. Nếu chưa đủ "
                "thông tin, hãy bổ sung sở thích, kỹ năng mạnh và mục tiêu."
            )

        has_observation = "observation:" in text
        has_job_observation = "du lieu mau" in text
        has_career_observation = "nganh:" in text

        if has_observation and ("loi:" in text or "lỗi:" in text):
            return (
                "Thought: Tool chưa có dữ liệu phù hợp; tôi không được bịa.\n"
                "Final Answer: Xin lỗi, dữ liệu mẫu chưa hỗ trợ yêu cầu này. "
                "Bạn nên kiểm chứng trên nguồn nghề nghiệp chính thức."
            )

        # Các test cần dữ liệu động/multi-step.
        if "data analyst" in text and "nhu cầu tuyển dụng" in text:
            if not has_job_observation:
                return (
                    "Thought: Cần tra cứu nhu cầu tuyển dụng Data Analyst.\n"
                    "Action: search_jobs_by_career[\"Data Analyst\", \"TP.HCM\"]"
                )
            return (
                "Thought: Observation đã có nhu cầu và các kỹ năng cốt lõi.\n"
                "Final Answer: Dữ liệu Lab cho thấy có nhu cầu Data Analyst tại "
                "TP.HCM. Bạn nên học Excel, SQL, Power BI/Tableau, thống kê, "
                "Python và giao tiếp; hãy kiểm chứng tin trên nguồn chính thức."
            )

        if "thực tập ai" in text:
            if not has_job_observation:
                return (
                    "Thought: Cần tìm cơ hội thực tập AI tại Hà Nội.\n"
                    "Action: search_jobs_by_career[\"AI\", \"Ha Noi\"]"
                )
            if not has_career_observation:
                return (
                    "Thought: Cần đối chiếu yêu cầu thực tập với kỹ năng AI.\n"
                    "Action: get_career_info[\"AI Engineer\"]"
                )
            return (
                "Thought: Đã đủ dữ liệu để lập lộ trình ba tháng.\n"
                "Final Answer: Có thể thử AI/ML Intern hoặc Computer Vision "
                "Intern. Tháng 1 củng cố Python, toán và ML; tháng 2 làm hai dự "
                "án; tháng 3 hoàn thiện GitHub/CV và luyện phỏng vấn. Hãy kiểm "
                "chứng tin tuyển dụng trước khi nộp."
            )

        if "vị trí thực tập ui/ux" in text:
            if not has_job_observation:
                return (
                    "Thought: Cần tìm vị trí thực tập UI/UX tại Hà Nội.\n"
                    "Action: search_jobs_by_career[\"UI/UX\", \"Ha Noi\"]"
                )
            if not has_career_observation:
                return (
                    "Thought: Cần đối chiếu tin thực tập với kỹ năng UI/UX.\n"
                    "Action: get_career_info[\"UI/UX\"]"
                )
            return (
                "Thought: Đã đủ dữ liệu vị trí và kỹ năng.\n"
                "Final Answer: Có thể tham khảo UI/UX Design Intern và Product "
                "Design Intern. Bạn cần Figma, research, wireframe, prototype, "
                "design system và 2-3 case study; hãy kiểm chứng tin trước khi nộp."
            )

        if "data analyst" in text and any(
            term in text for term in ("mức lương", "triển vọng")
        ):
            if not has_career_observation:
                return (
                    "Thought: Cần tra cứu thông tin Data Analyst có căn cứ.\n"
                    "Action: get_career_info[\"Data Analyst\"]"
                )
            return (
                "Thought: Đã có thông tin nghề và phạm vi dữ liệu.\n"
                "Final Answer: Data Analyst có triển vọng trong nhiều lĩnh vực. "
                "Mức tham khảo trong dữ liệu Lab là 15-30 triệu/tháng cho junior, "
                "nhưng phải kiểm chứng lại theo nguồn, địa điểm và thời điểm."
            )

        if "vị trí thực tập đang có" in text:
            if not has_job_observation:
                return (
                    "Thought: Hồ sơ thiên về sáng tạo; cần tra cứu UI/UX intern.\n"
                    "Action: search_jobs_by_career[\"UI/UX\", \"Ha Noi\"]"
                )
            return (
                "Thought: Đã có dữ liệu thực tập để tổng hợp.\n"
                "Final Answer: UI/UX hoặc Product Design phù hợp để thử. Hãy học "
                "Figma, research, wireframe và xây case study; mệnh/cung chỉ mang "
                "tính tham khảo. Kiểm chứng tin tuyển dụng trước khi nộp."
            )

        # Câu hỏi ổn định/an toàn: không gọi tool để tránh orchestration thừa.
        if "100%" in text and "giàu" in text:
            return (
                "Thought: Phải từ chối cam kết nghề nghiệp tuyệt đối.\n"
                "Final Answer: Không nghề nào bảo đảm giàu 100%. Mệnh chỉ mang "
                "tính tham khảo; hãy đánh giá kỹ năng, sở thích, điều kiện học "
                "và mức chấp nhận rủi ro."
            )
        if "con số chủ đạo" in text:
            return (
                "Thought: Thần số học không phải căn cứ nghề nghiệp đáng tin cậy.\n"
                "Final Answer: Số 2 thường được gắn với hợp tác và lắng nghe, "
                "nhưng chỉ mang tính tham khảo. Bạn có thể khám phá nhân sự, giáo "
                "dục hoặc điều phối rồi kiểm chứng bằng trải nghiệm và kỹ năng."
            )
        if "đề xuất 3 nghề" in text or (
            "nên chọn nghề gì" in text and "thích vẽ" in text
        ):
            return (
                "Thought: Có đủ sở thích để gợi ý sơ bộ mà không cần tool.\n"
                "Final Answer: Ba hướng đáng thử là UI/UX Designer, Graphic "
                "Designer và Content Designer. Sở thích vẽ, viết và sự tỉ mỉ là "
                "căn cứ chính; mệnh/cung chỉ mang tính giải trí."
            )
        if "tôi nên làm nghề gì" in text and "mệnh" in text:
            return (
                "Thought: Thiếu dữ liệu thiết yếu nên cần hỏi làm rõ.\n"
                "Final Answer: Mệnh/cung chỉ mang tính tham khảo. Bạn hãy cho "
                "biết sở thích, kỹ năng mạnh, môn học tốt và mục tiêu nghề nghiệp."
            )
        if "7 ngày" in text:
            return (
                "Thought: Có thể lập kế hoạch thử nghề mà không cần dữ liệu động.\n"
                "Final Answer: Trong 7 ngày, hãy tìm hiểu UI/UX, nghiên cứu một "
                "vấn đề, vẽ wireframe, làm prototype, xin phản hồi, chỉnh sửa và "
                "tự đánh giá hứng thú cùng chất lượng sản phẩm."
            )
        if "3 tháng" in text:
            return (
                "Thought: Có thể lập lộ trình học chung mà không cần tool.\n"
                "Final Answer: Tháng 1 học nền tảng/Figma; tháng 2 làm hai case "
                "study; tháng 3 hoàn thiện portfolio, nhận phản hồi và luyện "
                "phỏng vấn. Đánh giá tiến độ mỗi tuần."
            )
        if "kỹ thuật phần mềm" in text:
            return (
                "Thought: Đây là kiến thức nghề ổn định, không cần tool.\n"
                "Final Answer: Kỹ sư phần mềm phân tích yêu cầu, phát triển, "
                "kiểm thử, triển khai và bảo trì sản phẩm, đồng thời phối hợp "
                "với thiết kế, kiểm thử và quản lý sản phẩm."
            )
        if "ui/ux designer, content creator" in text:
            return (
                "Thought: Có thể so sánh ba nghề bằng tiêu chí ổn định.\n"
                "Final Answer: UI/UX phù hợp nhất với vẽ và sự tỉ mỉ; Content "
                "Creator hợp với viết nhưng cần giao tiếp; Data Analyst cần SQL, "
                "thống kê và logic. Hãy thử một dự án UI/UX trước."
            )
        if "đam mê điều gì" in text:
            return (
                "Thought: Khám phá bản thân không cần dữ liệu động.\n"
                "Final Answer: Hãy thử ba dự án ngắn, ghi mức hứng thú, năng "
                "lượng, kết quả và phản hồi sau mỗi trải nghiệm rồi so sánh."
            )
        if "marketing hay công nghệ thông tin" in text:
            return (
                "Thought: Có thể so sánh ngành bằng kiến thức ổn định.\n"
                "Final Answer: Marketing thiên về khách hàng/nội dung; CNTT "
                "thiên về hệ thống và giải quyết vấn đề. Hướng giao thoa gồm "
                "UI/UX, Product Marketing và Digital Analytics."
            )
        if "chuyển sang data analyst" in text:
            return (
                "Thought: Đây là tư vấn chuyển nghề, chưa cần dữ liệu động.\n"
                "Final Answer: Không quá muộn. Kế toán tạo lợi thế về số liệu; "
                "hãy học SQL, Excel nâng cao, thống kê, Power BI và làm portfolio "
                "phân tích dữ liệu tài chính."
            )
        return (
            "Thought: Đây là tư vấn kiến thức ổn định, không cần tool.\n"
            "Final Answer: Hãy so sánh nghề theo công việc hằng ngày, kỹ năng, "
            "mức sáng tạo, giao tiếp và cơ hội thử nghiệm. Ưu tiên trải nghiệm "
            "thực tế và bổ sung thông tin trước khi quyết định."
        )


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Factory function tự chọn Provider từ biến môi trường LLM_PROVIDER"""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()
    
    if name == "gemini":
        return GeminiProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "deepseek":
        return DeepSeekProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name == "openrouter":
        return OpenRouterProvider()
    else:
        return MockProvider()


if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"✅ Provider đang dùng: {provider.__class__.__name__}")
    print(f"🤖 User Query: Hello")
    print(f"💬 Response  : {provider.generate('Hello')}")
