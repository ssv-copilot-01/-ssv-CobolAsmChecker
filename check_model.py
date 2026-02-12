# Do Google thay đổi model liên tục, file này để bạn kiểm tra model nào đang hoạt động với API Key của bạn
# Hãy chạy lại python check_model.py.
# Lấy tên model mới cập nhật vào MODEL_LIST trong file gemini_service.py.
# cau lenh de check: python check_model.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
response = requests.get(url)

if response.status_code == 200:
    models = response.json().get('models', [])
    print("✅ DANH SÁCH MODEL KHẢ DỤNG CHO KEY CỦA BẠN:")
    for m in models:
        # Chỉ lấy model nào hỗ trợ generateContent
        if "generateContent" in m.get('supportedGenerationMethods', []):
            print(f" - {m['name'].replace('models/', '')}")
else:
    print(f"❌ Lỗi: {response.text}")