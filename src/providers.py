"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

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
                contents=contents,
                config={"max_output_tokens": 2000},
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
                messages=messages,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek Provider (deepseek-chat, deepseek-reasoner) — OpenAI-compatible API."""
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
                max_tokens=2000,
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
    """Offline Mock Provider — simulates ReAct Agent thought patterns."""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        text = prompt

        # Detect if this is a follow-up call (has observation from previous tool execution)
        has_obs = "Observation:" in text or "observation:" in text

        if has_obs:
            text_lower = text.lower()

            # After get_job_market for Data Science + course question
            if "data science" in text_lower and "search_courses" not in text_lower:
                return "Thought: Da co thong tin thi truong. Tiep theo can goi y khoa hoc.\nAction: search_courses['Machine Learning']"

            # After check_skills -> need career path too
            if "check_skills" in text_lower and "get_career_path" not in text_lower:
                return "Thought: Da co ket qua ky nang. Can them lo trinh.\nAction: get_career_path['fresher']"

            # Got tools results -> final answer
            if "get_job_market" in text_lower or "check_skills" in text_lower or "get_career_path" in text_lower:
                return "Thought: Da co du thong tin. Toi se tong hop cau tra loi.\nFinal Answer: Dua tren du lieu da tra cuu: nganh Data Science co muc luong 25-40M Junior, nhu cau tang 35%/nam. Voi Python va SQL ban can bo sung them ML, Statistics. Lo trinh: Fresher (8-12M) -> Junior (15-25M) -> Mid (25-40M). Hay bat dau voi khoa Andrew Ng ML tren Coursera!"

            # Edge case - tool returned error
            if "chưa có dữ liệu" in text_lower or "không tìm thấy" in text_lower:
                return "Thought: Tool khong co du lieu cho yeu cau nay.\nFinal Answer: Xin loi, toi khong tim thay thong tin cho yeu cau cua ban. Vui long thu lai voi tu khoa cu the hon!"

            return "Thought: Da co du thong tin.\nFinal Answer: Day la cau tra loi dua tren du lieu da tra cuu. Chuc ban thanh cong!"

        # --- First call — no observation yet ---
        text_lower = text.lower()

        # Career market queries
        if ("thị trường" in text_lower or "ngành" in text_lower) and ("data" in text_lower):
            if "khóa" in text_lower or "học" in text_lower:
                return "Thought: Nguoi dung muon biet thi truong + khoa hoc Data Science. Bat dau voi thi truong.\nAction: get_job_market['Data Science']"
            return "Thought: Nguoi dung muon biet thong tin thi truong Data Science. Can goi tool tra cuu.\nAction: get_job_market['Data Science']"
        if "thị trường" in text_lower and ("ai" in text_lower or "trí tuệ" in text_lower):
            return "Thought: Can tra cuu thi truong AI.\nAction: get_job_market['Artificial Intelligence']"
        if "thị trường" in text_lower and ("software" in text_lower or "phần mềm" in text_lower):
            return "Thought: Can tra cuu thi truong Software Engineering.\nAction: get_job_market['Software Engineering']"

        # Skill matching
        if ("kỹ năng" in text_lower or "thiếu" in text_lower) and ("biết" in text_lower or "có" in text_lower) and ("python" in text_lower or "sql" in text_lower):
            if "lộ trình" in text_lower or "thăng tiến" in text_lower:
                return "Thought: Nguoi dung muon ca doi chieu ky nang va lo trinh. Bat dau voi kiem tra ky nang.\nAction: check_skills['Python, SQL', 'Data Scientist']"
            return "Thought: Nguoi dung muon doi chieu ky nang. Can goi tool.\nAction: check_skills['Python, SQL', 'Data Scientist']"

        # Course search
        if "khóa" in text_lower or "course" in text_lower:
            if "machine learning" in text_lower or "ml" in text_lower:
                return "Thought: Nguoi dung muon tim khoa hoc Machine Learning.\nAction: search_courses['Machine Learning']"
            return "Thought: Can tim khoa hoc phu hop.\nAction: search_courses['Machine Learning']"

        # Career path
        if "lộ trình" in text_lower or "thăng tiến" in text_lower:
            if "fresher" in text_lower or "sinh viên" in text_lower:
                return "Thought: Can tra cuu lo trinh tu Fresher.\nAction: get_career_path['fresher']"
            return "Thought: Can tra cuu lo trinh thang tien.\nAction: get_career_path['fresher']"

        # Edge case: nonsense queries
        if "atlantis" in text_lower or "phù thủy" in text_lower:
            return "Thought: Nguoi dung hoi ve mot dia danh/nghe nghiep khong co that. Can goi tool de xac nhan.\nAction: get_job_market['Atlantis']"

        # Generic fallback — simple questions don't need tools
        return "Thought: Nguoi dung hoi cau hoi tu van chung, khong can goi tool.\nFinal Answer: Chao ban! Toi la Chatbot Dinh Huong Su Nghiep. Toi co the giup ban: (1) Tra cuu thi truong viec lam theo nganh, (2) Doi chieu ky nang voi yeu cau tuyen dung, (3) Goi y khoa hoc/chung chi, (4) Ve lo trinh thang tien. Hay cho toi biet ban dang quan tam den linh vuc nao nhe!"


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
