import time
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Ưu tiên Lite và Flash mới nhất
MODEL_LIST = [
    "gemini-2.0-flash-lite", 
    "gemini-flash-lite-latest",
    "gemini-1.5-flash",
    "gemini-2.0-flash"
]

def delay(seconds):
    time.sleep(seconds)

def add_ruler_to_code(source_code):
    ruler = "....+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8"
    return f"RULER:\n{ruler}\n{source_code}"

# ==========================================
# PROMPT BUILDER (ROBOT MODE - NO CHITCHAT)
# ==========================================
def build_prompt(lang_code, rules_text, source_code, lang_prog):
    
    code_with_ruler = add_ruler_to_code(source_code)

    hard_rules = """
    QUY TẮC CỨNG VỀ CỘT (HARD COLUMN RULES):
    1. DIVISION/SECTION Header: Phải bắt đầu ở Cột 41 (Area B sâu).
    2. PIC/PICTURE: Phải bắt đầu ở Cột 41.
    3. Level 01: Cột 8-11 (Area A).
    4. Độ dài dòng: Tối đa 72 ký tự.
    """

    # CẤU HÌNH NGÔN NGỮ (VIỆT)
    if lang_code == 'vi':
        system_instruction = """
        BẠN LÀ MỘT ROBOT LINTER. NHIỆM VỤ CỦA BẠN LÀ TRẢ VỀ DANH SÁCH LỖI.
        
        ⛔️ QUY ĐỊNH CẤM (STRICT FORBIDDEN):
        1. KHÔNG được chào hỏi ("Chào mừng...", "Dưới đây là...").
        2. KHÔNG được giải thích quy trình ("Phân tích mã nguồn...", "Kiểm tra theo...").
        3. KHÔNG chia nhóm lỗi ("Lỗi cột:", "Lỗi cú pháp:").
        4. KHÔNG viết kết luận.
        
        ✅ YÊU CẦU OUTPUT DUY NHẤT:
        Chỉ trả về các dòng lỗi nối tiếp nhau theo đúng định dạng sau:
        
        ❌ `[Line <Số dòng>] <Code gốc>`
           ↳ **Lỗi:** <Tên lỗi ngắn gọn> (Theo Rule X).
        
        (Xuống dòng 2 lần giữa các lỗi)
        
        ❌ `[Line <Số dòng>] ...`
           ↳ **Lỗi:** ...
           
        Nếu không có lỗi nào, chỉ ghi đúng 1 từ: "✅ CLEAN CODE".
        """

    # CẤU HÌNH NGÔN NGỮ (NHẬT)
    else: 
        system_instruction = """
        あなたは厳格なコード検査ロボットです。
        
        ⛔️ 禁止事項 (STRICT FORBIDDEN):
        1. 挨拶や導入文は一切禁止です ("こんにちは", "分析結果は..." 等)。
        2. カテゴリ分け禁止 ("カラムエラー:", "構文エラー:" 等)。
        3. 結論やまとめ禁止。
        
        ✅ 唯一の出力フォーマット:
        エラーリストのみを以下の形式で出力してください：
        
        ❌ `[Line <行番号>] <元のコード>`
           ↳ **エラー:** <簡潔なエラー内容> (Rule X).
        
        (エラー間は1行空けること)
        
        エラーがない場合のみ: "✅ CLEAN CODE" と出力。
        """

    # GHÉP PROMPT
    prompt = f"""
    {system_instruction}
    
    [HARD RULES]:
    {hard_rules}
    
    [DOCS RULES]:
    {rules_text}

    [SOURCE CODE WITH RULER]:
    {code_with_ruler}
    
    BẮT ĐẦU QUÉT VÀ CHỈ TRẢ VỀ LIST LỖI:
    """
    return prompt
# ==========================================
# HÀM GỌI API (CẬP NHẬT)
# ==========================================
def call_gemini_smart_fallback(rules_text, source_code, lang_prog, selected_lang, active_key):
    if not active_key:
        return "❌ Error: API Key is missing."

    # Xác định ngôn ngữ cho Prompt ('vi' hoặc 'ja')
    lang_code = 'vi' if 'Việt' in selected_lang else 'ja'

    user_prompt = build_prompt(lang_code, rules_text, source_code, lang_prog)

    print(f"🚀 Audit ({lang_code}) using Key: {active_key[:5]}...*****")

    for model_name in MODEL_LIST:
        try:
            # DÙNG KEY ĐƯỢC TRUYỀN VÀO (active_key)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={active_key}"
            headers = {'Content-Type': 'application/json'}
            payload = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "generationConfig": {"temperature": 0.0}
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    return f"🚀 **Model: {model_name}**\n\n{text}"
                except: continue
            elif response.status_code == 429:
                delay(1)
                continue
            else: continue

        except Exception:
            delay(1)
            continue

    return "❌ Service Unavailable (Check Key or Quota)."