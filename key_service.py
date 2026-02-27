import os
import streamlit as st
import time  # THÊM
from dotenv import load_dotenv
import key_service  # <--- THÊM DÒNG NÀY

# Load key hệ thống
load_dotenv()
SYSTEM_KEY = os.getenv("GEMINI_API_KEY")

# Cấu hình giới hạn
MAX_FREE_USAGE = 5

def init_usage_counter():
    """Khởi tạo bộ đếm nếu chưa có"""
    if "usage_count" not in st.session_state:
        st.session_state["usage_count"] = 0

def get_usage_info():
    """Lấy thông tin số lần đã dùng"""
    init_usage_counter()
    return st.session_state["usage_count"], MAX_FREE_USAGE

def resolve_api_key(user_input_key):
    """
    Quyết định xem dùng Key nào.
    Returns: (final_key, key_type, error_message)
    """
    init_usage_counter()

    # TRƯỜNG HỢP 1: Người dùng nhập Key riêng
    if user_input_key and user_input_key.strip():
        return user_input_key, "USER", None

    # TRƯỜNG HỢP 2: Dùng Key hệ thống
    if not SYSTEM_KEY:
        return None, "ERROR", "❌ Lỗi Server: Chưa cấu hình Key mặc định trong .env"

    # Kiểm tra hạn mức
    current_usage = st.session_state["usage_count"]
    
    if current_usage >= MAX_FREE_USAGE:
        return None, "LIMIT", f"⚠️ HẾT LƯỢT MIỄN PHÍ ({MAX_FREE_USAGE}/{MAX_FREE_USAGE}). Vui lòng nhập Key riêng của bạn để tiếp tục."

    return SYSTEM_KEY, "SYSTEM", None

def mark_as_used(key_type):
    """Tăng bộ đếm nếu dùng Key hệ thống"""
    if key_type == "SYSTEM":
        st.session_state["usage_count"] += 1