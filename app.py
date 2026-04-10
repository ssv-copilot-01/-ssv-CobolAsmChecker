import streamlit as st
import docx
import gemini_service
import key_service
import os
import time
import markdown
from dotenv import load_dotenv

load_dotenv()
api_key_status = os.getenv("GEMINI_API_KEY")

# ==========================================
# 1. TỪ ĐIỂN NGÔN NGỮ (VIỆT - NHẬT 100%)
# ==========================================
TRANSLATIONS = {
    "🇻🇳 Tiếng Việt": {
        "lang_header": "🌐 Ngôn ngữ",
        "lang_select": "Chọn ngôn ngữ hiển thị:",
        "page_title": "SSV CODE AUDITOR",
        "subtitle": "Hệ thống kiểm tra quy chuẩn Code tự động (AI)",
        "sidebar_config": "⚙️ Cấu hình hệ thống",
        "input_data": "📁 Dữ liệu đầu vào",
        "upload_rules": "1. Tải lên file Quy chuẩn (.docx)",
        "uploader_hint": "Kéo thả file vào đây",
        "uploader_button": "Chọn file",
        "uploader_limit": "Giới hạn 200MB mỗi file • DOCX",
        "key_header": "🔑 Quản lý API Key",
        "key_label": "Nhập API Key cá nhân (Tùy chọn):",
        "key_free_info": "🎁 Lượt dùng thử hệ thống:",
        "key_limit": "⚠️ Đã hết lượt dùng thử!",
        "key_personal": "✅ Đang sử dụng Key cá nhân",
        "key_ready": "✅ Hệ thống sẵn sàng",
        "key_missing": "❌ Thiếu API Key",
        "col1_title": "1. Nhập Source Code",
        "prog_lang": "Ngôn ngữ lập trình:",
        "tab_paste": "📝 Dán Code trực tiếp",
        "tab_upload": "📁 Tải lên File",
        "placeholder_code": "Dán mã nguồn vào đây...",
        "upload_btn_label": "Chọn file từ máy tính (.cbl, .asm, .txt)",
        "btn_run": "🚀 BẮT ĐẦU KIỂM TRA",
        "col2_title": "2. Kết quả Phân tích",
        "error_rules": "❌ Vui lòng upload file Quy chuẩn!",
        "error_code": "❌ Vui lòng nhập Source Code!",
        "loading": "AI đang phân tích từng dòng code... Vui lòng đợi...",
        "footer": "© 2024 SSV Corporation. Công cụ nội bộ."
    },
    "🇯🇵 日本語": {
        "lang_header": "🌐 言語設定",
        "lang_select": "表示言語を選択してください:",
        "page_title": "SSV コード監査ツール",
        "subtitle": "ソースコード自動チェッカー (AI搭載)",
        "sidebar_config": "⚙️ システム設定",
        "input_data": "📁 入力データ",
        "upload_rules": "1. 規約ファイルをアップロード (.docx)",
        "uploader_hint": "ファイルをドラッグ＆ドロップ",
        "uploader_button": "ファイルを選択",
        "uploader_limit": "最大200MBまで • DOCX",
        "key_header": "🔑 APIキー管理",
        "key_label": "個人用APIキーを入力 (任意):",
        "key_free_info": "🎁 無料試用枠:",
        "key_limit": "⚠️ 試用制限に達しました！",
        "key_personal": "✅ 個人キーを使用中",
        "key_ready": "✅ システム準備完了",
        "key_missing": "❌ APIキーがありません",
        "col1_title": "1. ソースコード入力",
        "prog_lang": "プログラミング言語:",
        "tab_paste": "📝 コード貼り付け",
        "tab_upload": "📁 ファイルアップロード",
        "placeholder_code": "ここにソースコードを貼り付けてください...",
        "upload_btn_label": "パソコンからファイルを選択",
        "btn_run": "🚀 チェック開始",
        "col2_title": "2. 分析結果",
        "error_rules": "❌ 規約ファイルをアップロードしてください！",
        "error_code": "❌ ソースコードを入力してください！",
        "loading": "AIがコードを分析中... お待ちください...",
        "footer": "© 2024 SSV Corporation. 社内ツール"
    }
}

# ==========================================
# 2. UI CONFIG & CSS (BỔ SUNG CSS FIX CỨNG NGÔN NGỮ)
# ==========================================
st.set_page_config(page_title="SSV Code Auditor", page_icon="🛡️", layout="wide")

# Hàm khởi tạo ngôn ngữ để lấy Text cho CSS
if "language" not in st.session_state:
    st.session_state["language"] = "🇻🇳 Tiếng Việt"

T = TRANSLATIONS[st.session_state["language"]]

st.markdown(f"""
<style>
    .gradient-top-bar {{
        height: 6px; width: 100%; background: linear-gradient(90deg, rgb(2, 3, 129) 0%, rgb(65, 88, 208) 100%);
        position: fixed; top: 0; left: 0; z-index: 99999;
    }}
    .stApp {{ background-color: #F4F6F9 !important; color: #333 !important; font-family: 'Helvetica Neue', sans-serif; }}
    h1, h2, h3, h4, strong {{ color: rgb(2, 3, 129) !important; font-weight: 800 !important; }}
    
    /* ẨN VÀ THAY THẾ CHỮ TRONG FILE UPLOADER */
    /* 1. Thay thế chữ 'Drag and drop file here' */
    section[data-testid="stFileUploaderDropzone"] div div span {{
        display: none;
    }}
    section[data-testid="stFileUploaderDropzone"] div div::before {{
        content: "{T['uploader_hint']}";
        font-weight: bold;
        color: #475569;
    }}
    /* 2. Thay thế chữ 'Limit 200MB...' */
    section[data-testid="stFileUploaderDropzone"] div div small {{
        display: none;
    }}
    section[data-testid="stFileUploaderDropzone"] div div div::after {{
        content: "{T['uploader_limit']}";
        display: block;
        font-size: 0.8em;
        color: #94A3B8;
        margin-top: 5px;
    }}
    /* 3. Thay thế chữ 'Browse files' trên nút bấm */
    button[data-testid="stBaseButton-secondary"] div p {{
        display: none;
    }}
    button[data-testid="stBaseButton-secondary"] div::before {{
        content: "{T['uploader_button']}";
        font-size: 14px;
    }}

    /* CSS STYLE CŨ CỦA BẠN */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: #FFFFFF !important; border: 1px solid #94A3B8 !important; color: #0F172A !important;
    }}
    div.stButton > button:first-child {{
        background-image: linear-gradient(90deg, rgb(2, 3, 129) 0%, rgb(65, 88, 208) 100%);
        color: #FFFFFF !important; border: none; border-radius: 50px;
        padding: 16px 32px; font-weight: 700; text-transform: uppercase; width: 100%;
        box-shadow: 0 4px 15px rgba(2, 3, 129, 0.2); transition: all 0.3s;
    }}
    .report-box {{
        background-color: #FFFFFF; padding: 30px; border-radius: 8px;
        border: 1px solid #E2E8F0; border-left: 6px solid rgb(2, 3, 129);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); color: #333 !important;
    }}
</style>
<div class="gradient-top-bar"></div>
""", unsafe_allow_html=True)

# Helper functions
def read_docx(file):
    try:
        doc = docx.Document(file)
        texts = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(texts) if texts else "Empty File."
    except Exception as e: return str(e)

def read_code_file(f):
    try: return f.getvalue().decode("utf-8", errors="ignore")
    except Exception as e: return str(e)

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><img src="https://ssv-corp.com/wp-content/uploads/2024/05/ssv-logo2.svg" width="160"></div>', unsafe_allow_html=True)
    
    # CHỌN NGÔN NGỮ (FIX CHỈ HIỆN 🇻🇳 Tiếng Việt / TIẾNG NHẬT)
    st.header(T["lang_header"])
    lang_choice = st.radio(
        T["lang_select"],
        options=["🇻🇳 Tiếng Việt", "🇯🇵 日本語"],
        index=0 if st.session_state["language"] == "🇻🇳 Tiếng Việt" else 1,
        key="lang_radio"
    )
    
    # Nếu đổi ngôn ngữ, cập nhật session_state và rerun
    if lang_choice != st.session_state["language"]:
        st.session_state["language"] = lang_choice
        st.rerun()

    st.markdown("---")
    st.header(T["key_header"])
    user_input_key = st.text_input(T["key_label"], type="password")
    
    used, limit = key_service.get_usage_info()
    if user_input_key:
        st.success(T["key_personal"])
    else:
        percent = int((used / limit) * 100)
        st.info(f"{T['key_free_info']} {used}/{limit}")
        st.progress(min(percent/100, 1.0))

    st.markdown("---")
    st.header(T["sidebar_config"])
    uploaded_rule = st.file_uploader(T["upload_rules"], type=["docx"])
    
    st.markdown("---")
    if api_key_status:
        st.success(T["key_ready"])
    else:
        st.error(T["key_missing"])

# ==========================================
# 4. MAIN CONTENT
# ==========================================
st.markdown(f"# {T['page_title']}")
st.caption(T['subtitle'])
st.write("")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"### {T['col1_title']}")
    language = st.selectbox(T["prog_lang"], ["COBOL", "ASSEMBLY"], index=0)
    
    tab_up, tab_ps = st.tabs([T["tab_upload"], T["tab_paste"]])
    
    final_code = ""
    with tab_ps:
        code_text = st.text_area(T["placeholder_code"], height=400, key="code_area")
        if code_text: final_code = code_text
    with tab_up:
        up_file = st.file_uploader(T["upload_btn_label"], type=['cbl', 'cob', 'asm', 'txt'], key="code_uploader")
        if up_file: final_code = read_code_file(up_file)

    st.write("")
    btn_run = st.button(T["btn_run"], type="primary", use_container_width=True)

with col2:
    st.markdown(f"### {T['col2_title']}")
    
    if btn_run:
        final_key, key_type, error_msg = key_service.resolve_api_key(user_input_key)
        
        if error_msg:
            st.error(error_msg)
        elif not uploaded_rule:
            st.error(T["error_rules"])
        elif not final_code.strip():
            st.error(T["error_code"])
        else:
            with st.spinner(T["loading"]):
                try:
                    rules_content = read_docx(uploaded_rule)
                    style_code = 'vi' if st.session_state["language"] == "🇻🇳 Tiếng Việt" else 'ja'
                    
                    raw_result = gemini_service.call_gemini_smart_fallback(
                        rules_content, final_code, language, style_code, final_key
                    )
 
                    if not raw_result.startswith("❌"):
                        key_service.mark_as_used(key_type)
 
                        # Đếm số lỗi để hiển thị summary
                        error_count = raw_result.count("#### ❌")
                        if error_count == 0 and "CLEAN" not in raw_result and "クリーン" not in raw_result:
                            error_count = raw_result.count("❌")
 
                        # Hiển thị summary badge
                        if style_code == 'vi':
                            summary_error = f"🔍 Phát hiện **{error_count} lỗi** trong source code."
                            summary_clean = "✅ Source code không có lỗi!"
                        else:
                            summary_error = f"🔍 **{error_count} 件のエラー**が検出されました。"
                            summary_clean = "✅ エラーは検出されませんでした！"

                        if error_count > 0:
                            st.error(summary_error, icon="❌")
                        else:
                            st.success(summary_clean, icon="✅")
 
                        # Render kết quả markdown vào report-box
                        html_content = markdown.markdown(
                            raw_result,
                            extensions=['extra', 'nl2br']  # 'extra' hỗ trợ table, fenced code...
                        )
                        st.markdown(
                            f'<div class="report-box">{html_content}</div>',
                            unsafe_allow_html=True
                        )
                        st.toast("Hoàn thành!", icon="✅")
                    else:
                        st.error(raw_result)
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #888; font-size: 12px;'>{T['footer']}</div>", unsafe_allow_html=True)