# tests

[Thư mục cha](../README.md) · [Quy tắc cấu trúc](../docs/STRUCTURE_GOVERNANCE.md)

## Mục đích và ranh giới

Kiểm tra hành vi của CLI và các module EngineeringOS. Test theo module hoặc khả năng quan sát được; dữ liệu tạm thuộc tmp/. Không gọi model hoặc dịch vụ thật khi kiểm tra cấu trúc tài liệu.

## Tài liệu và file hiện có

- [test_cli.py](test_cli.py).
- [test_structure.py](test_structure.py).
- [test_structure_governance.py](test_structure_governance.py).

## Khi mở rộng

Thêm file đúng ranh giới trên và liên kết từ mục lục này. Thư mục con mới cần được đăng ký trong manifest, có README.md riêng và liên kết từ README cha. Áp dụng quy trình và kiểm tra trong tài liệu quy tắc cấu trúc.
