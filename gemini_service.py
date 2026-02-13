import os
import time
import requests
import json
from dotenv import load_dotenv

# ==========================================
# 1. LOAD KEY
# ==========================================
load_dotenv() 
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ [Service] Lỗi: Không đọc được GEMINI_API_KEY từ .env")
else:
    print(f"✅ [Service] Key loaded: {API_KEY[:5]}...*****")

# ==========================================
# 2. DANH SÁCH MODEL (CẬP NHẬT THEO KEY CỦA BẠN)
# ==========================================
# Đây là danh sách dựa trên kết quả check_model.py của bạn
# Sắp xếp theo thứ tự: Ổn định/Nhẹ -> Mạnh mẽ -> Mới nhất
MODEL_LIST = [
    "gemini-flash-latest",     # 1. Alias an toàn nhất (thường trỏ về bản ổn định hiện tại)
    "gemini-2.0-flash-lite",   # 2. Bản Lite (Nhẹ, nhanh, ít bị lỗi Quota 429 nhất)
    "gemini-2.0-flash",        # 3. Bản Flash 2.0 chuẩn (Nếu Lite lỗi thì dùng cái này)
    "gemini-2.5-flash",        # 4. Bản 2.5 mới nhất (Mạnh nhưng có thể chưa ổn định)
    "gemini-2.0-flash-001",    # 5. Bản backup cụ thể
]

def delay(seconds):
    time.sleep(seconds)

# ==========================================
# 3. HÀM GỌI API (REST)
# ==========================================
def call_gemini_smart_fallback(rules_content, code_content, language, style_code):
    if not API_KEY:
        return "❌ Lỗi: Chưa có API Key."

    # ==============================
    # 1. STYLE CONFIG
    # ==============================
    if style_code == "en_vi":
        style_instruction = """
        Write the report in English (technical tone).
        After each section, add Vietnamese explanation.
        """
    else:
        style_instruction = """
        Write the report in English.
        Add Japanese explanation.
        Add Vietnamese explanation.
        """

    # ==============================
    # 2. BUILD PROMPT
    # ==============================
    user_prompt = f"""
ROLE: Senior Code Auditor ({language})

TASK:
Check the SOURCE CODE against the RULES.

================ RULES ================
{rules_content}

================ SOURCE CODE ================
{code_content}

================ REPORT STYLE ================
{style_instruction}

OUTPUT REQUIREMENTS:
1. List violations
2. Quote problematic code
3. Explain briefly
4. Suggest fix
5. If clean, say: "✅ CLEAN CODE"
"""

    print("🚀 Bắt đầu quy trình Smart Fallback...")
    last_error = None

    # ==============================
    # 3. MODEL LOOP
    # ==============================
    for model_name in MODEL_LIST:
        try:
            print(f"🔄 Đang thử model: {model_name}...")

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"

            headers = {'Content-Type': 'application/json'}
            payload = {
                "contents": [
                    {"parts": [{"text": user_prompt}]}
                ]
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                try:
                    data = response.json()
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ THÀNH CÔNG: {model_name}")
                    return f"🚀 **Model: {model_name}**\n\n{text}"
                except:
                    print(f"⚠️ {model_name}: 200 OK nhưng không có nội dung.")
                    continue

            elif response.status_code == 429:
                print(f"⚠️ {model_name}: Quota 429. Thử model tiếp theo...")
                last_error = "Quota Exceeded"
                delay(1)
                continue

            elif response.status_code == 404:
                print(f"⚠️ {model_name}: 404 Not Found.")
                continue

            else:
                print(f"⚠️ {model_name}: HTTP {response.status_code}")
                last_error = response.text
                continue

        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            last_error = str(e)
            delay(1)
            continue

    return f"❌ **THẤT BẠI:** Không model nào chạy được.\nLỗi cuối cùng: {last_error}"