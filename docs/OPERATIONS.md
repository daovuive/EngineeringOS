# Vận hành EngineeringOS

[Mục lục](README.md)

Chạy lệnh từ root repository với Python >= 3.10:

```powershell
python eng.py validate
python eng.py config structure
python eng.py config skills
python eng.py doctor
```

`validate` là kiểm tra chỉ đọc, trả mã khác 0 khi phát hiện sai lệch.
`doctor` còn kiểm tra môi trường và có thể gọi endpoint runtime đã cấu hình.

`init` và `sync` tạo thư mục/file thiếu theo manifest và template registry;
chúng không thay thế việc viết README có nội dung phù hợp hoặc duyệt root.
Không dùng chúng để dựng lại tài liệu nguồn/README bảo vệ bị mất từ file rỗng.
Kiểm tra diff sau khi chạy; file đã tồn tại phải được giữ nguyên.

Các lệnh AI/knowledge phụ thuộc runtime local đang chạy:

```powershell
python eng.py llm status
python eng.py llm pull-plan
python eng.py llm chat "Explain an architecture trade-off"
python eng.py knowledge index
python eng.py knowledge search "architecture decisions"
```

Chi tiết implementation và phần chưa triển khai nằm trong
[Architecture](ARCHITECTURE.md). Bộ kiểm tra cấu trúc không cần Ollama.

Kiểm tra trước khi bàn giao thay đổi:

```powershell
python eng.py validate
git diff --check
python -m unittest discover -s tests -p test_structure_governance.py
```

Test hiện hữu viết theo pytest có thể chạy bằng `python -m pytest` khi môi
trường đã cài dependency dev của pyproject.toml. Dữ liệu test tạm thuộc tmp/.
