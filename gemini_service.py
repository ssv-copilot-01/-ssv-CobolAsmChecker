import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()

MODEL_LIST = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash-lite-001",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.5-pro",
]

def add_line_numbers_and_ruler(source_code):
    ruler = "        ....+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8"
    lines = source_code.splitlines()
    numbered_lines = [f"{i+1:04d}: {line}" for i, line in enumerate(lines)]
    return f"RULER:\n{ruler}\n" + "\n".join(numbered_lines)

def build_prompt(lang_code, rules_text, source_code, lang_prog):
    code_prepared = add_line_numbers_and_ruler(source_code)

    if lang_code == 'vi':
        target_lang_instruction = "PHẢI TRẢ LỜI BẰNG TIẾNG VIỆT HOÀN TOÀN. Dịch các quy chuẩn từ tiếng Nhật sang tiếng Việt để giải thích."
        clean_msg = "✅ **CLEAN CODE** — Không phát hiện lỗi nào."
        role_msg = "Bạn là một Robot kiểm tra mã nguồn (Linter) chuyên nghiệp."
        example_block = """\
### Ví dụ định dạng đầu ra:

---

#### ❌ Dòng 10 — `001900 IDENTIFICATION DIVISION.`
- **Lỗi:** IDENTIFICATION DIVISION phải bắt đầu từ cột 8, hiện tại ở cột 1.
- **Cột:** 1 | **Rule:** 1.1 桁位置 / インデント

---

#### ❌ Dòng 22 — `003100 77   W-LEN  PIC  S9(11).`
- **Lỗi:** Cấp độ 77 phải bắt đầu từ cột 8, hiện tại ở cột 1.
- **Cột:** 1 | **Rule:** 1.1 桁位置 / インデント

---"""
        format_instruction = """\
Xuất kết quả theo định dạng Markdown sau cho MỖI lỗi tìm thấy.
Mỗi lỗi là một block riêng biệt, cách nhau bằng dòng `---`.
TUYỆT ĐỐI không thêm lời chào, giải thích hay bình luận ngoài danh sách lỗi."""

    else:
        target_lang_instruction = "必ず日本語で回答してください。すべての説明を日本語で行ってください。"
        clean_msg = "✅ **クリーンコード** — エラーは検出されませんでした。"
        role_msg = "あなたは厳格なコード検査ロボットです。"
        example_block = """\
### 出力フォーマットの例:

---

#### ❌ 行 10 — `001900 IDENTIFICATION DIVISION.`
- **エラー:** IDENTIFICATION DIVISIONは8桁目から始まる必要があります（現在: 1桁目）。
- **カラム:** 1 | **Rule:** 1.1 桁位置 / インデント

---

#### ❌ 行 22 — `003100 77   W-LEN  PIC  S9(11).`
- **エラー:** レベル77は8桁目から始まる必要があります（現在: 1桁目）。
- **カラム:** 1 | **Rule:** 1.1 桁位置 / インデント

---"""
        format_instruction = """\
以下のMarkdown形式で、検出されたすべてのエラーを出力してください。
各エラーは `---` で区切られた独立したブロックとして記述してください。
挨拶・説明・コメントは一切不要です。エラーリストのみを出力してください。"""

    prompt = f"""
{role_msg}
出力言語 / NGÔN NGỮ ĐẦU RA: {target_lang_instruction}

{format_instruction}

{example_block}

**Nếu không có lỗi / エラーがない場合:**
{clean_msg}

---

[QUY CHUẨN / 規約]:
{rules_text}

[MÃ NGUỒN / ソースコード (có số dòng / 行番号付き)]:
{code_prepared}

---
LƯU Ý / 注意:
1. Quy chuẩn có thể bằng tiếng Nhật — hãy dịch và giải thích bằng {'Tiếng Việt' if lang_code=='vi' else '日本語'}.
2. Dùng RULER ở trên để xác định chính xác vị trí cột của lỗi.
3. Chỉ báo lỗi thực sự vi phạm quy chuẩn, không báo lỗi giả.
"""
    return prompt


def call_gemini_smart_fallback(rules_text, source_code, lang_prog, selected_lang_code, active_key):
    if not active_key:
        return "❌ Error: API Key is missing."

    lang_code = 'vi' if (selected_lang_code == 'vi' or 'vi' in str(selected_lang_code).lower()) else 'ja'
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
                continue

            if response.status_code in [400, 401, 403]:
                return f"❌ Lỗi API Key: {res_data.get('error', {}).get('message', 'Key không hợp lệ')}"

            last_error_msg = res_data.get('error', {}).get('message', response.text)

        except Exception as e:
            last_error_msg = str(e)
            continue

    return f"❌ Lỗi: {last_error_msg}. Vui lòng thử lại sau 1 phút."