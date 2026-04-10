import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Danh sách model (Ưu tiên bản 1.5 Flash vì Quota bản Free lớn nhất)
MODEL_LIST = [
    "gemini-flash-latest",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-pro-latest"
]

def add_line_numbers_and_ruler(source_code):
    ruler = "        ....+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8"
    lines = source_code.splitlines()
    numbered_lines = [f"{i+1:04d}: {line}" for i, line in enumerate(lines)]
    return f"RULER:\n{ruler}\n" + "\n".join(numbered_lines)

def build_prompt(lang_code, rules_text, source_code, lang_prog):
    """
    Sửa lỗi: Ép AI dịch từ Quy chuẩn tiếng Nhật sang Tiếng Việt nếu chọn UI Tiếng Việt.
    """
    code_prepared = add_line_numbers_and_ruler(source_code)
    
    # Thiết lập chỉ thị ngôn ngữ cực kỳ nghiêm ngặt
    if lang_code == 'vi':
        target_lang_instruction = "PHẢI TRẢ LỜI BẰNG TIẾNG VIỆT HOÀN TOÀN. Dịch các quy chuẩn từ tiếng Nhật sang tiếng Việt để giải thích."
        error_label = "Lỗi"
        line_label = "Dòng"
        col_label = "Cột"
        clean_msg = "✅ CLEAN CODE (KHÔNG CÓ LỖI)"
        role_msg = "Bạn là một Robot kiểm tra mã nguồn (Linter) chuyên nghiệp."
        format_msg = "Chỉ trả về danh sách lỗi theo mẫu dưới đây, tuyệt đối không chào hỏi:"
    else:
        target_lang_instruction = "必ず日本語で回答してください。すべての説明を日本語で行ってください。"
        error_label = "エラー"
        line_label = "行"
        col_label = "カラム"
        clean_msg = "✅ クリーンコード (エラーなし)"
        role_msg = "あなたは厳格なコード検査ロボットです。"
        format_msg = "挨拶は不要です。以下の形式でエラーリストのみを出力してください："

    prompt = f"""
{role_msg}
NGÔN NGỮ ĐẦU RA BẮT BUỘC: {target_lang_instruction}

{format_msg}

❌ `[{line_label} <Số dòng>] <Code gốc>`
   ↳ **{error_label}:** <Giải thích bằng {'Tiếng Việt' if lang_code=='vi' else '日本語'}> ({col_label}: <Vị trí cột>, Rule: <Tên quy chuẩn>)

(Nếu không có lỗi: "{clean_msg}")

[QUY CHUẨN ĐẦU VÀO (DÙNG ĐỂ ĐỐI CHIẾU)]:
{rules_text}

[MÃ NGUỒN CẦN KIỂM TRA (ĐÃ ĐÁNH SỐ DÒNG)]:
{code_prepared}

LƯU Ý QUAN TRỌNG:
1. Tài liệu Quy chuẩn có thể là tiếng Nhật, nhưng bạn PHẢI giải thích lỗi bằng {'Tiếng Việt' if lang_code=='vi' else 'Tiếng Nhật'}.
2. Đối chiếu số dòng và thước đo RULER ở trên để báo chính xác vị trí lỗi cột.
"""
    return prompt

def call_gemini_smart_fallback(rules_text, source_code, lang_prog, selected_lang_code, active_key):
    if not active_key:
        return "❌ Error: API Key is missing."

    # Xác định ngôn ngữ dựa trên UI (vi hoặc ja)
    lang_code = 'vi' if 'Tiếng Việt' in selected_lang_code else 'ja'
    user_prompt = build_prompt(lang_code, rules_text, source_code, lang_prog)

    last_error_msg = ""

    for model_name in MODEL_LIST:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={active_key}"
            payload = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "generationConfig": {"temperature": 0.0}
            }
            response = requests.post(url, json=payload, timeout=60)
            res_data = response.json()
            
            if response.status_code == 200:
                if 'candidates' in res_data:
                    return res_data['candidates'][0]['content']['parts'][0]['text']
            
            if response.status_code == 429:
                continue # Thử model tiếp theo nếu hết quota
            
            if response.status_code in [400, 401, 403]:
                return f"❌ Lỗi API Key: {res_data.get('error', {}).get('message', 'Key không hợp lệ')}"
            
            last_error_msg = res_data.get('error', {}).get('message', response.text)
        except Exception as e:
            last_error_msg = str(e)
            continue

    return f"❌ Lỗi: {last_error_msg}. Vui lòng thử lại sau 1 phút."