ETL_web_PowerBI
Mô tả dự án
Dự án ETL_web_PowerBI là một hệ thống tích hợp ETL và báo cáo trực quan hóa dữ liệu tài chính doanh nghiệp từ báo cáo tài chính (BCTC). Hệ thống giúp tự động thu thập, xử lý, phân tích và trình bày dữ liệu tài chính theo cách trực quan, dễ hiểu, đồng thời cung cấp API để tích hợp vào hệ thống web quản trị.

Chức năng chính
ETL Pipeline:

Extract: Thu thập dữ liệu báo cáo tài chính từ các nguồn công khai bằng Golang (crawler).

Transform: Xử lý và chuẩn hóa dữ liệu bằng Python, chuyển đổi thành định dạng CSV.

Load: Nạp dữ liệu CSV vào hệ thống Power BI để phục vụ phân tích.

Phân tích và trực quan hóa dữ liệu:

Xây dựng báo cáo phân tích tài chính doanh nghiệp bằng Power BI.

Tập trung vào các chỉ số tài chính chính như: lợi nhuận, doanh thu, chi phí, tỷ lệ nợ/vốn, ROE, ROA,...

Triển khai Web Dashboard:

Sử dụng Flask để phát triển web backend.

Tích hợp báo cáo từ Power BI thông qua API để hiển thị trên giao diện quản trị web.

Cho phép người dùng theo dõi dữ liệu tài chính theo thời gian thực.

Công nghệ sử dụng
Ngôn ngữ lập trình:

Golang: Thu thập dữ liệu (crawler).

Python: Tiền xử lý và chuyển đổi dữ liệu.

JavaScript/HTML (Flask Template): Giao diện web.

Công cụ và nền tảng:

Power BI: Trực quan hóa dữ liệu và tạo báo cáo.

Flask: Xây dựng web dashboard và phục vụ API.

CSV: Định dạng trung gian trong quá trình ETL.

Cấu trúc thư mục (gợi ý)
css
Sao chép
Chỉnh sửa
ETL_web_PowerBI/
├── csv/   
├── extract/  
├── load/  
├── transform/           # Python scripts để xử lý dữ liệu và xuất CSV
├── powerbi/             # File .pbix báo cáo Power BI
├── webflask/                 # Ứng dụng Flask
│   ├── templates/
│   ├── static/css,js
│   └── app.py
└── requirements.txt     # Các gói Python cần thiết

Chạy web Flask:

bash
Sao chép
Chỉnh sửa
cd web
python app.py
