python -m streamlit run app.py
python -m pip install google-generativeai
 python.exe -m pip install --upgrade pip
 python -m pip install python-docx

 https://ai.google.dev/gemini-api/docs/libraries?hl=vi
📘 MÔ TẢ CHI TIẾT CÔNG VIỆC
XÂY DỰNG HỆ THỐNG SSV CODE CHECKER

1. MỤC TIÊU CÔNG VIỆC
Xây dựng một web tool nội bộ cho phép kiểm tra mã nguồn (hiện tại là COBOL / Assembly) dựa trên quy chuẩn lập trình do khách hàng cung cấp dưới dạng tài liệu Word (.docx).
Hệ thống sử dụng AI Gemini để:
Đọc và hiểu nội dung quy chuẩn (ngôn ngữ tự nhiên).


Đối chiếu trực tiếp quy chuẩn với mã nguồn.


Phát hiện và báo cáo các vi phạm quy định lập trình.


KHÔNG sử dụng rule cứng (if/else) để check, vì nội dung quy chuẩn thay đổi theo từng khách hàng và thường được mô tả bằng văn bản tự do.

2. PHẠM VI CHỨC NĂNG
2.1 Input – Quy chuẩn (Rules)
Người dùng upload file Word định dạng .docx.


File có thể chứa:


Tiếng Việt / tiếng Anh / pha trộn.


Bullet point, đoạn văn, bảng hoặc text thường.


Hệ thống chỉ cần trích xuất toàn bộ text, không cần parse cấu trúc.


Nội dung sau khi đọc sẽ được gửi nguyên văn cho AI xử lý.


📌 Không yêu cầu chuẩn hóa format Rules.

2.2 Input – Mã nguồn (Source Code)
Hệ thống hỗ trợ 2 cách nhập code:
Cách 1: Upload file code
Định dạng hỗ trợ:


.CBL


.COB


Đọc toàn bộ nội dung file (UTF-8, ignore error).


Dùng cho việc check toàn bộ chương trình.


Cách 2: Copy & Paste code
Text area để dán từng đoạn code.


Dùng cho việc check logic nhỏ hoặc đoạn code đang chỉnh sửa.


📌 Nếu người dùng upload file → ưu tiên nội dung file
 📌 Nếu không upload file → dùng nội dung text area

2.3 Xử lý chính – AI Review Engine
Sử dụng Google Gemini API.


Chỉ sử dụng model: gemini



AI đóng vai:


 Senior Code Auditor chuyên COBOL / Assembly



AI nhận 3 input:
Nội dung Rules (text từ Word)


Mã nguồn


Ngôn ngữ (COBOL hoặc ASSEMBLY)



2.4 Prompt & Logic đánh giá
AI được yêu cầu:
Chỉ kiểm tra dựa trên Rules được cung cấp.


Không tự suy diễn thêm quy tắc bên ngoài.


Chỉ trả về:


Các lỗi vi phạm quy chuẩn.


Dòng code liên quan.


Giải thích ngắn gọn.


Nếu không có lỗi:


Trả về đúng 1 dòng:
 ✅ CLEAN CODE


📌 Không yêu cầu fix code, chỉ phát hiện vi phạm.

2.5 Output – Kết quả kiểm tra
Kết quả hiển thị trực tiếp trên giao diện web.


Có thể bao gồm:


Danh sách lỗi.


Mô tả lỗi.


Trích dẫn code.


Không lưu trữ kết quả sau khi reload trang.



3. GIAO DIỆN NGƯỜI DÙNG (UI)
Xây dựng bằng Streamlit.


Bố cục:


Sidebar: Upload Rules.


Main:


Chọn ngôn ngữ.


Chọn cách nhập code (Upload file / Copy).


Button “Kiểm tra”.


Vùng hiển thị kết quả.


UI đơn giản, dễ dùng, hướng đến nội bộ.



4. YÊU CẦU KỸ THUẬT
4.1 Backend / Logic
Python 3.x


Thư viện:


streamlit


python-docx


google-generativeai


Không cần database.


Không cần authentication.



4.2 API Key
API Key của Gemini được set cứng trong code.


Không cho người dùng nhập trên UI.


Dùng cho môi trường nội bộ.



4.3 Xử lý lỗi
Nếu lỗi quota (429):


Hiển thị thông báo chờ và retry.


Nếu lỗi model (404):


Thông báo cấu hình sai hoặc key không hợp lệ.


Không crash app.



5. GIỚI HẠN & LƯU Ý
Tool chỉ hỗ trợ kiểm tra, không thay thế review cuối cùng của con người.


Kết quả phụ thuộc vào:


Chất lượng Rules.


Nội dung code.


Không dùng cho mục đích đánh giá bảo mật hoặc performance.



6. KẾT QUẢ MONG MUỐN
Sau khi hoàn thành, hệ thống cho phép:
Review nhanh code theo từng khách hàng.


Áp dụng cho dự án legacy (COBOL).


Giảm thời gian review thủ công cho senior/leader.


Dùng làm công cụ training và checklist chất lượng code.



7. MỨC ĐỘ HOÀN THÀNH
✔️ Chạy được end-to-end
 ✔️ Không lỗi quota free tier
 ✔️ Dev khác có thể maintain
 ✔️ Phù hợp triển khai nội bộ

