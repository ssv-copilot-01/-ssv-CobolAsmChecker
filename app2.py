import streamlit as st
import docx
import gemini_service 
import os
from dotenv import load_dotenv

load_dotenv()
api_key_status = os.getenv("GEMINI_API_KEY")

# ==========================================
# UI HELPER
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
st.set_page_config(page_title="AI Code Auditor", page_icon="🛡️", layout="wide")

st.title("🛡️ SSV CODE CHECKER")
st.caption("Support: English-Vietnamese & English-Japanese (Bilingual)")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Language Settings")
    
    # === MENU CHỌN NGÔN NGỮ ===
    lang_choice = st.radio(
        "Report Language:",
        options=[
            "🇻🇳 Anh - Việt (Technical)", 
            "🇯🇵 Anh - Nhật (+Việt)"
        ]
    )
    
    # Map sang mã code
    style_code = 'en_vi' if "Anh - Việt" in lang_choice else 'en_jp'
    
    st.info(f"👉 **Mode:** {style_code.upper()}")
    if style_code == 'en_vi':
        st.caption("Technical Terms: English\nExplanation: Vietnamese")
    else:
        st.caption("Technical Terms: English\nExplanation: Japanese\nSub: Vietnamese")

    st.markdown("---")
    st.header("2. Input Data")
    uploaded_rule = st.file_uploader("Upload Rules (.docx)", type=["docx"])
    
    if api_key_status:
        st.success("✅ API Key: OK")
    else:
        st.error("❌ API Key: Missing")

# --- MAIN ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("3. Source Code")
    language = st.radio("Program Language:", ["COBOL", "ASSEMBLY"], horizontal=True)
    
    tab1, tab2 = st.tabs(["📝 Paste Code", "📁 Upload File"])
    
    final_code = ""
    with tab1:
        code_text = st.text_area("Paste code here:", height=400)
        if code_text: final_code = code_text
            
    with tab2:
        up_file = st.file_uploader("Choose file (.cbl, .asm)", type=['cbl', 'cob', 'asm', 'txt'])
        if up_file: final_code = read_code_file(up_file)

    st.markdown("---")
    btn_run = st.button("🚀 START AUDIT", type="primary", use_container_width=True)

with col2:
    st.header("4. Audit Result")
    
    if btn_run:
        if not api_key_status:
            st.error("❌ Error: Missing .env file")
        elif not uploaded_rule:
            st.error("❌ Error: Missing Rules file")
        elif not final_code.strip():
            st.error("❌ Error: Missing Source Code")
        else:
            with st.spinner(f"AI is analyzing ({lang_choice})..."):
                rules_content = read_docx(uploaded_rule)
                
                # Gọi Service với style_code
                result = gemini_service.call_gemini_smart_fallback(
                    rules_content, 
                    final_code, 
                    language,
                    style_code
                )
                
                st.markdown(result)