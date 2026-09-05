# runtime

[Thư mục cha](../README.md) · [Quy tắc cấu trúc](../docs/STRUCTURE_GOVERNANCE.md)

## Mục đích và ranh giới

Dữ liệu sinh ra khi chạy: model, cache, index và dữ liệu runtime cục bộ. Code adapter nằm ở engineering_os/llm.py; cấu hình nằm ở configs/ai-runtime.json. Không lưu tài liệu nguồn duy nhất trong dữ liệu có thể tái tạo.

Các thư mục sinh tự động `models/`, `cache/`, `index/`, `vector-db/` được khai báo ngoại lệ trong manifest. Việc có tên một vùng dữ liệu không có nghĩa capability tương ứng đã triển khai.

## Khi mở rộng

Thêm file đúng ranh giới trên và liên kết từ mục lục này. Thư mục con mới cần được đăng ký trong manifest, có README.md riêng và liên kết từ README cha. Áp dụng quy trình và kiểm tra trong tài liệu quy tắc cấu trúc.
