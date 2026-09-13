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
python3 eng.py validate
python3 -m compileall -q engineering_os tests
python3 -m unittest discover -s tests -p 'test_*.py'
git diff --check
```

Đây là đúng bộ gate deterministic của CI. Live Ollama, deployed-service và
browser-visual smoke tests là bước vận hành riêng, phải dùng dữ liệu synthetic;
chúng không chạy trong CI mặc định. Dữ liệu test tạm thuộc `tmp/`.

WebUI production không có chế độ demo. Sau khi khởi động EOS tại
`http://127.0.0.1:8081`, có thể chuẩn bị Playwright và kiểm tra trang thật trên
WSL Ubuntu/Debian bằng lệnh tùy chọn sau:

```bash
bash scripts/setup-wsl-webui-testing.sh http://127.0.0.1:8081
```

Đọc script trước khi chạy: nó dùng `sudo apt-get`, tải NVM/Node/Chromium và ghi
tooling vào `~/.local/share/eos-webui-testing/`. Đây không phải CI gate và không
được chạy tự động khi khởi động EngineeringOS.

## Observed host issue

Read-only diagnostics on 2026-09-12 found `ssh.service` failed, which makes
systemd report `degraded`. `engineeringos-web.service` and
`cloudflared.service` were active and healthy, so the SSH failure is unrelated
to EOS and was not modified by this work.
