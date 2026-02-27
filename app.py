import streamlit as st
import docx
import gemini_service
import key_service
import os
from dotenv import load_dotenv

load_dotenv()
api_key_status = os.getenv("GEMINI_API_KEY")

# ==========================================
# 1. TỪ ĐIỂN NGÔN NGỮ (ĐÃ BỔ SUNG CÁC TỪ KHÓA BỊ THIẾU)
# ==========================================
TRANSLATIONS = {
    "Tiếng Việt (ベトナム語)": {
        "page_title": "SSV CODE AUDITOR",
        "subtitle": "Hệ thống kiểm tra quy chuẩn Code tự động",
        "sidebar_config": "⚙️ Cấu hình",
        "lang_select": "Ngôn ngữ hiển thị:",
        "input_data": "📁 Dữ liệu đầu vào",
        "upload_rules": "Upload Quy chuẩn (.docx)",
        "key_ready": "✅ Hệ thống sẵn sàng",
        "key_missing": "❌ Thiếu API Key",
        # --- CÁC KEY MỚI BỔ SUNG CHO TÍNH NĂNG KEY ---
        "key_header": "🔑 Quản lý Key",
        "key_label": "Nhập Key riêng (Tùy chọn):",
        "key_free_info": "🎁 Dùng thử miễn phí:",
        "key_limit": "⚠️ Đã hết lượt dùng thử!",
        "key_personal": "✅ Đang dùng Key cá nhân",
        # ---------------------------------------------
        "col1_title": "1. Nhập Source Code",
        "prog_lang": "Ngôn ngữ lập trình:",
        "tab_paste": "📝 Dán Code trực tiếp",
        "tab_upload": "📁 Upload File (.cbl/.asm)",
        "placeholder_code": "Dán source code vào đây...",
        "upload_btn_label": "Chọn file từ máy tính",
        "btn_run": "🚀 BẮT ĐẦU KIỂM TRA",
        "col2_title": "2. Kết quả Phân tích",
        "error_env": "❌ Lỗi: Chưa cấu hình .env",
        "error_rules": "❌ Lỗi: Thiếu file Quy chuẩn (Rules)",
        "error_code": "❌ Lỗi: Chưa có Source Code",
        "loading": "AI đang soi lỗi... Vui lòng đợi...",
        "footer": "© 2024 SSV Corporation. Internal Tool."
    },
    "日本語 (Tiếng Nhật)": {
        "page_title": "SSV コード監査ツール",
        "subtitle": "ソースコード自動チェッカーシステム(AI搭載)",
        "sidebar_config": "⚙️ 設定",
        "lang_select": "表示言語:",
        "input_data": "📁 入力データ",
        "upload_rules": "規約ファイルをアップロード (.docx)",
        "key_ready": "✅ システム準備完了",
        "key_missing": "❌ APIキーがありません",
        # --- CÁC KEY MỚI BỔ SUNG CHO TÍNH NĂNG KEY ---
        "key_header": "🔑 APIキー管理",
        "key_label": "APIキーを入力 (任意):",
        "key_free_info": "🎁 無料トライアル:",
        "key_limit": "⚠️ 上限に達しました！",
        "key_personal": "✅ 個人キーを使用中",
        # ---------------------------------------------
        "col1_title": "1. ソースコード入力",
        "prog_lang": "プログラミング言語:",
        "tab_paste": "📝 コード貼り付け",
        "tab_upload": "📁 ファイルアップロード",
        "placeholder_code": "ここにソースコードを貼り付けてください...",
        "upload_btn_label": "ファイルを選択",
        "btn_run": "🚀 チェック開始",
        "col2_title": "2. 分析結果",
        "error_env": "❌ エラー: .envファイル未設定",
        "error_rules": "❌ エラー: 規約ファイル不足 (Rules)",
        "error_code": "❌ エラー: ソースコードがありません",
        "loading": "AI分析中... お待ちください...",
        "footer": "© 2024 SSV Corporation. 社内ツール"
    }
}

# ==========================================
# 2. UI CONFIG & CSS (GIỮ NGUYÊN CSS ĐẸP)
# ==========================================
st.set_page_config(page_title="SSV Code Auditor", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .gradient-top-bar {
        height: 6px; width: 100%; background: linear-gradient(90deg, rgb(2, 3, 129) 0%, rgb(65, 88, 208) 100%);
        position: fixed; top: 0; left: 0; z-index: 99999;
    }
    .stApp { background-color: #F4F6F9 !important; color: #333 !important; font-family: 'Helvetica Neue', sans-serif; }
    h1, h2, h3, h4, strong { color: rgb(2, 3, 129) !important; font-weight: 800 !important; }
    
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important; border: 1px solid #94A3B8 !important; color: #0F172A !important;
    }
    
    div.stButton > button:first-child {
        background-image: linear-gradient(90deg, rgb(2, 3, 129) 0%, rgb(65, 88, 208) 100%);
        color: #FFFFFF !important; border: none; border-radius: 50px;
        padding: 16px 32px; font-weight: 700; text-transform: uppercase; width: 100%;
        box-shadow: 0 4px 15px rgba(2, 3, 129, 0.2); transition: all 0.3s;
    }
    div.stButton > button:first-child:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(2, 3, 129, 0.35); }

    .report-box {
        background-color: #FFFFFF; padding: 30px; border-radius: 8px;
        border: 1px solid #E2E8F0; border-left: 6px solid rgb(2, 3, 129);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); color: #333 !important;
    }
    .report-box code {
        background-color: #F1F5F9; color: #B91C1C; border: 1px solid #E2E8F0;
        padding: 2px 6px; border-radius: 4px; font-family: 'Courier New', monospace; font-weight: bold;
    }
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
# 3. SIDEBAR (LOGIC KEY SERVICE)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://ssv-corp.com/wp-content/uploads/2024/05/ssv-logo2.svg" width="160">
        </div>
    """, unsafe_allow_html=True)
    
    # CHỌN NGÔN NGỮ
    st.header("🌐 Language / 言語")
    selected_lang = st.radio(
        "Display Language:",
        options=["Tiếng Việt (ベトナム語)", "日本語 (Tiếng Nhật)"],
        index=0
    )
    T = TRANSLATIONS[selected_lang]
    
    st.markdown("---")
    
    # --- PHẦN QUẢN LÝ KEY (Đã có từ điển T['key_header'] hỗ trợ) ---
    st.header(T["key_header"])
    user_input_key = st.text_input(T["key_label"], type="password")
    
    used, limit = key_service.get_usage_info()
    
    if user_input_key:
        st.success(T["key_personal"])
    else:
        percent = int((used / limit) * 100)
        st.info(f"{T['key_free_info']} {used}/{limit}")
        st.progress(percent)
        if used >= limit:
            st.error(T["key_limit"])

    st.markdown("---")
    
    # UPLOAD RULES
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
    
    tab2, tab1 = st.tabs([T["tab_upload"], T["tab_paste"]])
    final_code = ""
    
    with tab1:
        code_text = st.text_area(T["placeholder_code"], height=400)
        if code_text: final_code = code_text
    with tab2:
        up_file = st.file_uploader(T["upload_btn_label"], type=['cbl', 'cob', 'asm', 'txt'])
        if up_file: final_code = read_code_file(up_file)

    st.write("")
    btn_run = st.button(T["btn_run"], type="primary", use_container_width=True)

with col2:
    st.markdown(f"### {T['col2_title']}")
    
    if btn_run:
        # XỬ LÝ KEY
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
                    
                    # Truyền style_code (vi/ja) cho Service
                    style_code = 'vi' if "Tiếng Việt" in selected_lang else 'ja'
                    
                    raw_result = gemini_service.call_gemini_smart_fallback(
                        rules_content, 
                        final_code, 
                        language,
                        style_code, # Truyền 'vi' hoặc 'ja'
                        final_key
                    )
                    
                    if "❌" not in raw_result:
                        key_service.mark_as_used(key_type)
                        import markdown
                        html_content = markdown.markdown(raw_result)
                        st.markdown(f'<div class="report-box">{html_content}</div>', unsafe_allow_html=True)
                        
                        # Refresh để update thanh tiến trình
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(raw_result)
                        
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #888; font-size: 12px;'>{T['footer']}</div>", unsafe_allow_html=True)