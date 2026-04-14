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
    """Giả lập Sakura Editor Ruler để AI soi cột cực chuẩn"""
    # Thước đo được thiết kế để cột 1 của code khớp với vị trí số 1 trên thước
    ruler_1 = "         1         2         3         4         5         6         7         8"
    ruler_2 = "12345678901234567890123456789012345678901234567890123456789012345678901234567890"
    ruler_3 = "--------+--+-------+---------+---------+---------+---------+---------+---------+-"
    #           ^  ^  ^
    #           7  8  12
    
    lines = source_code.splitlines()
    # Format: [Số dòng 4 chữ số] | [Nội dung]
    # Dùng ký tự '|' làm mốc để AI biết mốc đó là cột 0
    numbered_lines = [f"{i+1:04d} |{line}" for i, line in enumerate(lines)]
    
    header = f"SAKURA EDITOR RULER MODE:\n{ruler_1}\n{ruler_2}\n{ruler_3}"
    return f"{header}\n" + "\n".join(numbered_lines)

def build_prompt(lang_code, rules_text, source_code, lang_prog):
    code_prepared = add_line_numbers_and_ruler(source_code)

    # Cập nhật Hard Rules để AI hiểu cấu trúc Sakura Editor vừa tạo
    if lang_code == 'vi':
        hard_rules = """
📏 **HƯỚNG DẪN SOI CỘT TRÊN GIẢ LẬP SAKURA EDITOR:**
- Ký tự ngay sau dấu '|' là cột 1.
- Cột 7: Indicator Area (Dấu * để comment).
- Cột 8-11: Area A (DIVISION, SECTION, Level 01, 77).
- Cột 12-72: Area B (Câu lệnh, PIC).
"""

        target_lang_instruction = "PHẢI TRẢ LỜI BẰNG TIẾNG VIỆT HOÀN TOÀN. Dịch các quy chuẩn từ tiếng Nhật sang tiếng Việt để giải thích."
        clean_msg = "✅ **CLEAN CODE** — Không phát hiện lỗi nào."
        role_msg = "Bạn là một Robot kiểm tra mã nguồn (Linter) chuyên nghiệp."
        
        example_block = """\
### Ví dụ định dạng đầu ra:

---

#### ❌ Dòng 10 — `001900 IDENTIFICATION DIVISION.`
- **Lỗi:** IDENTIFICATION DIVISION phải bắt đầu từ cột 8 (Area A), hiện tại ở cột 13.
- **Cột:** 13 | **Rule:** 1.1 カラム位置

---

#### ❌ Dòng 22 — `003100 77   W-LEN  PIC  S9(11).`
- **Lỗi:** Cấp độ 77 phải bắt đầu từ cột 8 (Area A), hiện tại ở cột 1.
- **Cột:** 1 | **Rule:** 1.1 カラム位置

---"""

        format_instruction = """\
Xuất kết quả theo định dạng Markdown sau cho MỖI lỗi tìm thấy.
Mỗi lỗi là một block riêng biệt, cách nhau bằng dòng `---`.
TUYỆT ĐỐI không thêm lời chào, giải thích hay bình luận ngoài danh sách lỗi."""

    else:  # Japanese
        hard_rules = """
📏 **COBOLカラム位置の固定ルール (国際標準):**

| エリア | カラム | 内容 |
|--------|--------|------|
| **シーケンス番号** | 1-6 | 行番号（省略可） |
| **インジケータエリア** | 7 | `*` = コメント, `-` = 継続行, `D` = デバッグ, space = 通常 |
| **エリアA** | 8-11 | DIVISION, SECTION, 段落名, レベル01/77 |
| **エリアB** | 12-72 | ステートメント, PIC句 |
| **識別エリア** | 73-80 | 無視（処理しない） |

⚠️ **重要:**
- DIVISION/SECTION ヘッダー: **8-11列目** (エリアA) - 41列目ではない
- レベル番号 (01-49, 77): **8-11列目** (エリアA)
- 段落名: **8-11列目** (エリアA)
- PIC/PICTURE 句: **12-72列目** (エリアB)
- ステートメント: **12-72列目** (エリアB)
- コメント (*): **7列目**
- 行の長さ: **最大72文字** (12-72列目)
"""

        target_lang_instruction = "必ず日本語で回答してください。すべての説明を日本語で行ってください。"
        clean_msg = "✅ **クリーンコード** — エラーは検出されませんでした。"
        role_msg = "あなたは厳格なコード検査ロボットです。"
        
        example_block = """\
### 出力フォーマットの例:

---

#### ❌ 行 10 — `001900 IDENTIFICATION DIVISION.`
- **エラー:** IDENTIFICATION DIVISIONは8列目から開始する必要があります（エリアA）、現在は13列目。
- **カラム:** 13 | **Rule:** 1.1 カラム位置

---

#### ❌ 行 22 — `003100 77   W-LEN  PIC  S9(11).`
- **エラー:** レベル77は8列目から開始する必要があります（エリアA）、現在は1列目。
- **カラム:** 1 | **Rule:** 1.1 カラム位置

---"""

        format_instruction = """\
以下のMarkdown形式で、検出されたすべてのエラーを出力してください。
各エラーは `---` で区切られた独立したブロックとして記述してください。
挨拶・説明・コメントは一切不要です。エラーリストのみを出力してください。"""

    # GHÉP PROMPT HOÀN CHỈNH
    prompt = f"""
{role_msg}
出力言語 / NGÔN NGỮ ĐẦU RA: {target_lang_instruction}

{format_instruction}

{example_block}

**Nếu không có lỗi / エラーがない場合:**
{clean_msg}

---

[HARD RULES - QUY TẮC CỘT BẮT BUỘC]:
{hard_rules}

[QUY CHUẨN / 規約]:
{rules_text}

[MÃ NGUỒN / ソースコード (có số dòng / 行番号付き)]:
{code_prepared}

---
LƯU Ý / 注意:
1. Quy chuẩn có thể bằng tiếng Nhật — hãy dịch và giải thích bằng {'Tiếng Việt' if lang_code=='vi' else '日本語'}.
2. Dùng RULER ở trên để xác định chính xác vị trí cột của lỗi.
3. Chỉ báo lỗi thực sự vi phạm quy chuẩn, không báo lỗi giả.
4. DIVISION/SECTION đúng ở cột 8-11 (Area A), KHÔNG phải cột 41.
"""
    return prompt


def call_gemini_smart_fallback(rules_text, source_code, lang_prog, selected_lang_code, active_key):
    if not active_key:
        return "❌ Error: API Key is missing."

    # Xử lý lấy lang_code vi/ja từ chuỗi input
    if isinstance(selected_lang_code, str):
        if 'vi' in selected_lang_code.lower() or 'tiếng việt' in selected_lang_code.lower():
            lang_code = 'vi'
        else:
            lang_code = 'ja'
    else:
        lang_code = 'vi'  # default

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
                if 'candidates' in res_data and len(res_data['candidates']) > 0:
                    content = res_data['candidates'][0].get('content', {})
                    parts = content.get('parts', [])
                    
                    # GHÉP TẤT CẢ PHẦN TEXT LẠI THÀNH CHUỖI
                    full_text = "".join([p.get('text', '') for p in parts if 'text' in p])
                    
                    if full_text.strip():
                        return str(full_text)

            if response.status_code == 429:
                continue
            if response.status_code in [400, 401, 403]:
                return f"❌ Lỗi API Key: {res_data.get('error', {}).get('message', 'Key không hợp lệ')}"

            last_error_msg = res_data.get('error', {}).get('message', response.text)
        except Exception as e:
            last_error_msg = str(e)
            continue

    return f"❌ Lỗi: {last_error_msg}"