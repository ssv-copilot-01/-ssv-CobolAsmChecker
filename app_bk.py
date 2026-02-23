import streamlit as st
import docx
import gemini_service 
import os
from dotenv import load_dotenv
import markdown

load_dotenv()
api_key_status = os.getenv("GEMINI_API_KEY")

# ==========================================
# 1. CẤU HÌNH TRANG & CSS (FIX LỖI MÀU CHỮ)
# ==========================================
st.set_page_config(page_title="SSV Code Checker", page_icon="🛡️", layout="wide")
#----------------------------------------------------------------------------------------------------------------------
st.markdown("""
<style>
    /* ====================================================================
       1. CẤU TRÚC CHUNG & MÀU SẮC
       ==================================================================== */
    
    /* Thanh gradient trên cùng */
    .gradient-top-bar {
        height: 6px;
        width: 100%;
        background: linear-gradient(90deg, rgb(2, 3, 129) 0%, rgb(65, 88, 208) 100%);
        position: fixed;
        top: 0;
        left: 0;
        z-index: 99999;
    }

    /* Nền tổng thể và Font chữ */
    .stApp {
        background-color: #F4F6F9 !important; /* Xám xanh rất nhạt hiện đại */
        color: #333333 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Các đoạn văn bản */
    p, li, span, label {
        color: #1e293b !important;
    }

    /* Tiêu đề (Header) */
    h1, h2, h3, h4, strong {
        color: rgb(2, 3, 129) !important;
        font-weight: 800 !important;
    }

    /* ====================================================================
       2. INPUTS (CÓ VIỀN RÕ RÀNG)
       ==================================================================== */
    
    /* Khung nhập liệu */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border: 1px solid #94A3B8 !important; /* Viền xám xanh đậm hơn cho rõ */
        border-radius: 4px !important;
        color: #0F172A !important;
    }

    /* Focus */
    .stTextArea textarea:focus, .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: rgb(65, 88, 208) !important;
        box-shadow: 0 0 0 1px rgb(65, 88, 208) !important;
    }

    /* ====================================================================
    3. NÚT BẤM CHÍNH - CHUẨN SSV CORP (NHƯ NÚT 資料請求/お問い合わせ)
    ==================================================================== */

    /* Nút BẮT ĐẦU KIỂM TRA - NỀN TRẮNG, CHỮ XANH */
    div.stButton > button:first-child {
        /* Nền trắng tinh */
        background-image: linear-gradient(90deg, rgb(255, 255, 255) 0%, rgb(255, 255, 255) 100%) !important;
        background-color: rgb(255, 255, 255) !important;
        
        /* Typography - Chữ xanh đậm SSV */
        color: rgb(2, 3, 129) !important;
        font-weight: 700;
        font-size: 16px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        text-decoration: none;
        
        /* Border & Shape - Viền xanh đậm */
        border: 2px solid rgb(2, 3, 129) !important;
        border-radius: 50px !important;
        
        /* Spacing */
        padding: 14px 32px !important;
        width: 100%;
        margin: 0.5rem 0;
        
        /* Effects - Shadow nhẹ */
        box-shadow: 0 4px 15px rgba(2, 3, 129, 0.08);
        transition: all 0.25s cubic-bezier(0.02, 0.01, 0.1, 1);
        
        /* Position cho hiệu ứng hover */
        position: relative;
        overflow: hidden;
    }

    /* Hiệu ứng hover - nền xanh nhạt, viền đậm hơn */
    div.stButton > button:first-child:hover {
        background-image: linear-gradient(90deg, rgb(245, 247, 255) 0%, rgb(245, 247, 255) 100%) !important;
        background-color: rgb(245, 247, 255) !important;
        color: rgb(2, 3, 129) !important;
        border: 2px solid rgb(2, 3, 129) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(2, 3, 129, 0.15);
    }

    /* Hiệu ứng active (khi click) */
    div.stButton > button:first-child:active {
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(2, 3, 129, 0.1);
    }

    /* Icon rocket cho button - màu xanh */
    div.stButton > button:first-child p {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        margin: 0 !important;
        color: rgb(2, 3, 129) !important;
    }

    div.stButton > button:first-child p::before {
        content: "";
        font-size: 1.2em;
        margin-right: 4px;
    }

    /* ====================================================================
       4. CÁC THÀNH PHẦN KHÁC
       ==================================================================== */
    
    /* Vùng Upload */
    [data-testid="stFileUploader"] {
        border: 2px dashed #94A3B8;
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }

    /* Khung kết quả (Report Box) */
    .report-box {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        border-left: 6px solid rgb(2, 3, 129);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        color: #333333 !important;
    }
    
    /* Code block */
    .report-box code {
        background-color: #F1F5F9;
        color: #B91C1C;
        border: 1px solid #E2E8F0;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
    }

    /* Tab Header */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #FFFFFF;
        border-top: 3px solid rgb(2, 3, 129);
        color: rgb(2, 3, 129);
        font-weight: bold;
    }
</style>
<div class="gradient-top-bar"></div>
""", unsafe_allow_html=True)
#----------------------------------------------------------------------------------------------------------------------
# ==========================================
# 2. HÀM UI HELPER
# ==========================================
def read_docx(file):
    try:
        doc = docx.Document(file)
        texts = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(texts) if texts else "File Rules rỗng."
    except Exception as e:
        return f"Lỗi đọc file Word: {e}"

def read_code_file(uploaded_file):
    try:
        return uploaded_file.getvalue().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"Lỗi đọc file code: {e}"

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://ssv-corp.com/wp-content/uploads/2024/05/ssv-logo2.svg" width="160" alt="SSV Logo">
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("⚙️ Cấu hình")
    
    lang_choice = st.radio(
        "Ngôn ngữ báo cáo:",
        options=["🇻🇳 Anh - Việt (Technical)", "🇯🇵 Anh - Nhật (+Việt)"]
    )
    style_code = 'en_vi' if "Anh - Việt" in lang_choice else 'en_jp'
    
    st.markdown("---")
    st.subheader("📁 Dữ liệu đầu vào")
    uploaded_rule = st.file_uploader("Upload Quy chuẩn (.docx)", type=["docx"])
    
    st.markdown("---")
    if api_key_status:
        st.success("✅ System Ready")
    else:
        st.error("❌ API Key Missing")

# ==========================================
# 4. MAIN CONTENT
# ==========================================
st.markdown("# 🛡️ SSV CODE CHECKER")
st.write("")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1. Source Code Input")
    language = st.selectbox("Ngôn ngữ lập trình:", ["COBOL", "ASSEMBLY"], index=0)
    
    tab1, tab2 = st.tabs(["📝 Dán Code trực tiếp", "📁 Upload File (.cbl/.asm)"])
    final_code = ""
    with tab1:
        code_text = st.text_area("Dán source code vào đây:", height=400)
        if code_text: final_code = code_text
    with tab2:
        up_file = st.file_uploader("Chọn file từ máy tính", type=['cbl', 'cob', 'asm', 'txt'])
        if up_file: final_code = read_code_file(up_file)

    st.write("")
    btn_run = st.button("🚀 BẮT ĐẦU KIỂM TRA", type="primary", use_container_width=True)

with col2:
    st.markdown("### 2. Audit Report")
    
    if btn_run:
        if not api_key_status:
            st.error("❌ Lỗi: Chưa cấu hình .env")
        elif not uploaded_rule:
            st.error("❌ Lỗi: Thiếu file Quy chuẩn (Rules)")
        elif not final_code.strip():
            st.error("❌ Lỗi: Chưa có Source Code")
        else:
            with st.spinner("AI đang phân tích... Vui lòng đợi..."):
                try:
                    rules_content = read_docx(uploaded_rule)
                    
                    # Gọi Service
                    raw_result = gemini_service.call_gemini_smart_fallback(
                        rules_content, 
                        final_code, 
                        language,
                        style_code
                    )
                    
                    # Xử lý format markdown để hiển thị đẹp trong HTML div
                    import markdown
                    html_content = markdown.markdown(raw_result)
                    
                    # Bọc kết quả vào khung HTML có class 'report-box' để ép màu chữ
                    st.markdown(f"""
                    <div class="report-box">
                        {html_content}
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #888; font-size: 12px;'>© 2024 SSV Corporation.</div>", unsafe_allow_html=True)