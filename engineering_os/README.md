# engineering_os

[Thư mục cha](../README.md) · [Quy tắc cấu trúc](../docs/STRUCTURE_GOVERNANCE.md)

## Mục đích và ranh giới

Mã Python của EngineeringOS: CLI, cấu hình, tạo/kiểm tra cấu trúc, runtime abstraction và tìm kiếm Markdown. eng.py ở gốc chỉ là entrypoint. API runtime đi qua LLMRuntime/create_runtime; không đưa workflow học tập hoặc dữ liệu model vào module code.

## Tài liệu và file hiện có

- [__init__.py](__init__.py).
- [cli.py](cli.py).
- [config.py](config.py).
- [doctor.py](doctor.py).
- [knowledge.py](knowledge.py).
- [llm.py](llm.py).
- [structure.py](structure.py).
- [templates.py](templates.py).

## Khi mở rộng

Thêm file đúng ranh giới trên và liên kết từ mục lục này. Thư mục con mới cần được đăng ký trong manifest, có README.md riêng và liên kết từ README cha. Áp dụng quy trình và kiểm tra trong tài liệu quy tắc cấu trúc.
