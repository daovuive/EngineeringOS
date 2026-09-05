# scripts

[Thư mục cha](../README.md) · [Quy tắc cấu trúc](../docs/STRUCTURE_GOVERNANCE.md)

## Mục đích và ranh giới

Script vận hành hỗ trợ EngineeringOS khi thật sự cần. Logic CLI có thể tái sử dụng thuộc engineering_os/. Chỉ thêm script khi có đầu vào, đầu ra, cách chạy và cách kiểm tra rõ ràng; không tạo implementation thứ hai của cùng chức năng.

## Khi mở rộng

Thêm file đúng ranh giới trên và liên kết từ mục lục này. Thư mục con mới cần được đăng ký trong manifest, có README.md riêng và liên kết từ README cha. Áp dụng quy trình và kiểm tra trong tài liệu quy tắc cấu trúc.
