Dưới đây là phần **Setup Environment hoàn chỉnh** anh viết chuẩn README cho project của em.
Em có thể copy nguyên khối này vào `README.md`.
Savoy Blue rgb(65, 88, 208) 100%);
---

# 🚀 Environment Setup Guide

## 1️⃣ Clone Repository

```bash
git clone https://github.com/ssv-copilot-01/-ssv-CobolAsmChecker.git
cd -ssv-CobolAsmChecker
```

---

## 2️⃣ Tạo Virtual Environment

### 🔹 Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 🔹 macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Sau khi activate thành công, terminal sẽ hiển thị:

```bash
(.venv)
```

---

## 3️⃣ Cập nhật pip (khuyến nghị)

```bash
python -m pip install --upgrade pip
```

---

## 4️⃣ Cài đặt Dependencies

Đảm bảo project có file:

```
requirements.txt
```

Nội dung mẫu:

```
streamlit
python-dotenv
requests
python-docx
```

Cài đặt:

```bash
pip install -r requirements.txt
```

---

## 5️⃣ Cấu hình API Key (.env)

Tạo file `.env` trong thư mục gốc project:

```
GEMINI_API_KEY=your_api_key_here
```

⚠️ Không commit file `.env` lên GitHub.
Đảm bảo `.gitignore` có dòng:

```
.env
```

---

## 6️⃣ (Tuỳ chọn) Kiểm tra Model khả dụng

```bash
python check_model.py
```

Script sẽ hiển thị danh sách model mà API Key của bạn có thể sử dụng.

---

## 7️⃣ Chạy Ứng Dụng

```bash
python -m streamlit run app.py
```

Sau khi chạy thành công:

```
Local URL: http://localhost:8501
```

Mở trình duyệt và truy cập link trên.

---

# 🛠 Kiểm Tra Python Đang Sử Dụng

Để đảm bảo đang dùng đúng virtual environment:

### Windows

```bash
where python
```

Phải hiển thị đường dẫn dạng:

```
...\CobolAsmChecker\.venv\Scripts\python.exe
```

---

# 📦 Re-Setup From Scratch (Khi Clone Mới)

```bash
python -m venv .venv
.\.venv\Scripts\activate   # hoặc source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

# ✅ Yêu Cầu Hệ Thống

* Python 3.10+
* Internet connection (để gọi Gemini API)

---

Nếu em muốn, anh có thể viết thêm:

* 🔹 phần **Project Structure**
* 🔹 phần **Deployment Guide**
* 🔹 hoặc bản README chuẩn “Professional Open Source” level GitHub ⭐
