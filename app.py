import streamlit as st
import docx
import gemini_service # Import file service xịn ở trên

# ==========================================
# HÀM UI HELPER
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
# GIAO DIỆN CHÍNH
# ==========================================
st.set_page_config(page_title="Smart Code Auditor", page_icon="🛡️", layout="wide")

st.title("🛡️ SMART CODE AUDITOR")
st.caption("Chiến thuật: Auto-Switch Model (2.0 -> 1.5 Pro -> 1.5 Flash)")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("1. Input Data")
    uploaded_rule = st.file_uploader("Upload Rules (.docx)", type=["docx"])
    
    # Check trạng thái .env (Gọi vào biến trong service)
    if gemini_service.API_KEY:
        st.success("✅ API Key: Đã kết nối")
    else:
        st.error("❌ API Key: Chưa tìm thấy .env")

# Main
col1, col2 = st.columns([1, 1])

with col1:
    st.header("2. Source Code")
    language = st.radio("Ngôn ngữ:", ["COBOL", "ASSEMBLY"], horizontal=True)
    
    tab1, tab2 = st.tabs(["📝 Dán Code", "📁 Upload File"])
    
    final_code = ""
    with tab1:
        code_text = st.text_area("Paste code vào đây:", height=400)
        if code_text: final_code = code_text
            
    with tab2:
        up_file = st.file_uploader("Chọn file code (.cbl, .asm)", type=['cbl', 'cob', 'asm', 'txt'])
        if up_file: final_code = read_code_file(up_file)

    st.markdown("---")
    btn_run = st.button("🚀 BẮT ĐẦU AUDIT", type="primary", use_container_width=True)

with col2:
    st.header("3. Kết quả")
    if btn_run:
        if not gemini_service.API_KEY:
            st.error("❌ Lỗi: Chưa cấu hình file .env")
        elif not uploaded_rule:
            st.error("❌ Lỗi: Chưa upload file Rules")
        elif not final_code.strip():
            st.error("❌ Lỗi: Chưa có Code đầu vào")
        else:
            with st.spinner("🤖 Đang phân tích (Đang thử từng model)..."):
                # 1. Đọc Rules
                rules_content = read_docx(uploaded_rule)
                
                # 2. Gọi Service thông minh
                # (Toàn bộ logic try/catch/loop nằm bên kia, bên này rất gọn)
                result = gemini_service.call_gemini_smart_fallback(
                    rules_content, 
                    final_code, 
                    language
                )
                
                st.markdown(result)