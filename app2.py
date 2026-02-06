import streamlit as st
import docx
import google.generativeai as genai

# ==================================================
# 0. CẤU HÌNH API KEY (SET CỨNG – KHÔNG NHẬP TAY)
# ==================================================
GEMINI_API_KEY = "AIzaSyDCSIqgoNl-3Hz0bTsgsf-R4JnL6XcBjf8"

# ==================================================
# 1. ĐỌC FILE WORD (.docx)
# ==================================================
def read_docx(file):
    try:
        doc = docx.Document(file)
        texts = []
        for p in doc.paragraphs:
            if p.text.strip():
                texts.append(p.text)
        return "\n".join(texts) if texts else "File Rules rỗng."
    except Exception as e:
        return f"Lỗi đọc file Word: {e}"

# ==================================================
# 2. ĐỌC FILE SOURCE CODE (.CBL / .COB)
# ==================================================
def read_code_file(file):
    try:
        content = file.read().decode("utf-8", errors="ignore")
        return content if content.strip() else "File code rỗng."
    except Exception as e:
        return f"Lỗi đọc file code: {e}"

# ==================================================
# 3. GỌI GEMINI (FLASH – FREE TIER SAFE)
# ==================================================
def analyze_with_gemini(rules_text, source_code, language):
    try:
        genai.configure(api_key=GEMINI_API_KEY)

        model = genai.GenerativeModel(
            model_name="models/gemini-1.5-flash"
        )

        prompt = f"""
Bạn là Senior Code Auditor chuyên về {language}.

[RULES]
{rules_text}

[CODE]
{source_code}

YÊU CẦU:
- Chỉ liệt kê lỗi vi phạm
- Trích dẫn dòng code sai
- Giải thích ngắn gọn
- Nếu không có lỗi, ghi đúng một dòng: ✅ CLEAN CODE
"""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        msg = str(e)
        if "429" in msg or "Quota" in msg:
            return "⚠️ Hết quota tạm thời. Chờ 1–2 phút rồi thử lại."
        if "404" in msg:
            return "❌ Model không tồn tại hoặc API Key sai."
        return f"❌ Lỗi hệ thống: {msg}"

# ==================================================
# 4. GIAO DIỆN STREAMLIT
# ==================================================
st.set_page_config(
    page_title="SSV CODE CHECKER",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ SSV CODE CHECKER")
st.caption("Gemini Flash – Free Tier – Internal Tool")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Rules")
    rules_file = st.file_uploader(
        "Upload file Quy chuẩn (.docx)",
        type=["docx"]
    )

# Main
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input Code")

    language = st.radio(
        "Ngôn ngữ",
        ["COBOL", "ASSEMBLY"],
        horizontal=True
    )

    input_mode = st.radio(
        "Cách nhập code",
        ["📁 Upload file (.CBL / .COB)", "✍️ Copy từng đoạn"],
        horizontal=False
    )

    code_text = ""

    if input_mode.startswith("📁"):
        code_file = st.file_uploader(
            "Upload file code",
            type=["cbl", "cob"]
        )
        if code_file:
            code_text = read_code_file(code_file)
    else:
        code_text = st.text_area(
            "Dán code vào đây",
            height=400
        )

    run_btn = st.button(
        "🚀 KIỂM TRA",
        type="primary",
        use_container_width=True
    )

with col2:
    st.subheader("Kết quả")

    if run_btn:
        if not rules_file:
            st.error("❌ Chưa upload file Rules (.docx)")
        elif not code_text or code_text.startswith("File"):
            st.error("❌ Chưa có code hợp lệ")
        else:
            with st.spinner("⚡ Gemini Flash đang phân tích..."):
                rules = read_docx(rules_file)

                if rules.startswith("Lỗi"):
                    st.error(rules)
                else:
                    result = analyze_with_gemini(
                        rules,
                        code_text,
                        language
                    )
                    st.markdown(result)
