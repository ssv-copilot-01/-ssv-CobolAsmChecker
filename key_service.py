import os
import json
import time
import streamlit as st
from dotenv import load_dotenv

# Load key hệ thống
load_dotenv()
SYSTEM_KEY = os.getenv("GEMINI_API_KEY")

# Cấu hình giới hạn
MAX_FREE_USAGE = 5

# File lưu trữ usage (đặt cùng thư mục với app)
USAGE_FILE = "usage_data.json"

# ==========================================
# PERSISTENT STORAGE (lưu vào file JSON)
# ==========================================

def _load_usage_data():
    """Đọc dữ liệu usage từ file JSON"""
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_usage_data(data: dict):
    """Ghi dữ liệu usage vào file JSON"""
    try:
        with open(USAGE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.warning(f"Không thể lưu usage: {e}")

def _get_session_id():
    """
    Tạo định danh duy nhất cho mỗi người dùng/browser.
    Dùng st.query_params để giữ ID qua F5.
    """
    # Nếu URL đã có session_id thì dùng lại
    params = st.query_params
    if "sid" in params:
        return params["sid"]

    # Tạo session ID mới và gắn vào URL
    new_sid = f"user_{int(time.time() * 1000)}"
    st.query_params["sid"] = new_sid
    return new_sid

# ==========================================
# PUBLIC API (giữ nguyên interface cũ)
# ==========================================

def init_usage_counter():
    """Khởi tạo bộ đếm nếu chưa có (giữ tương thích ngược)"""
    sid = _get_session_id()
    data = _load_usage_data()
    if sid not in data:
        data[sid] = 0
        _save_usage_data(data)

def get_usage_info():
    """Lấy thông tin số lần đã dùng"""
    sid = _get_session_id()
    data = _load_usage_data()
    count = data.get(sid, 0)
    return count, MAX_FREE_USAGE

def resolve_api_key(user_input_key):
    """
    Quyết định xem dùng Key nào.
    Returns: (final_key, key_type, error_message)
    """
    # TRƯỜNG HỢP 1: Người dùng nhập Key riêng
    if user_input_key and user_input_key.strip():
        return user_input_key, "USER", None

    # TRƯỜNG HỢP 2: Dùng Key hệ thống
    if not SYSTEM_KEY:
        return None, "ERROR", "❌ Lỗi Server: Chưa cấu hình Key mặc định trong .env"

    # Kiểm tra hạn mức
    sid = _get_session_id()
    data = _load_usage_data()
    current_usage = data.get(sid, 0)

    if current_usage >= MAX_FREE_USAGE:
        return None, "LIMIT", f"⚠️ HẾT LƯỢT MIỄN PHÍ ({MAX_FREE_USAGE}/{MAX_FREE_USAGE}). Vui lòng nhập Key riêng của bạn để tiếp tục."

    return SYSTEM_KEY, "SYSTEM", None

def mark_as_used(key_type):
    """Tăng bộ đếm nếu dùng Key hệ thống — lưu vào file"""
    if key_type == "SYSTEM":
        sid = _get_session_id()
        data = _load_usage_data()
        data[sid] = data.get(sid, 0) + 1
        _save_usage_data(data)