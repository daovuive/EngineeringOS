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

## Local service diagnostics

`scripts/eos-status` is the repository-owned operational diagnostic for a
locally running EngineeringOS web service and its configured Ollama runtime.
It does not expose an HTTP diagnostic endpoint, does not read or send
Cloudflare Access credentials, and does not change service state.

From the repository root:

```bash
scripts/eos-status
scripts/eos-status --deep
```

FAST mode checks system/service state, local `/health`, configured Ollama
metadata, relevant listening ports, the unauthenticated result of the public
health URL, and warning-event counts. It does **not** call `/api/v1/query` and
does not load an Ollama model. `--deep` is explicit: it performs one local RAG
request, then reports request status, answer status, source count, latency, a
redacted answer preview, and models loaded afterward.

To invoke the repository-owned script globally, create a symlink only when the
destination does not already exist:

```bash
mkdir -p "$HOME/.local/bin"
ln -s "$(pwd)/scripts/eos-status" "$HOME/.local/bin/eos-status"
```

The command uses these optional deployment overrides; defaults preserve the
current local service setup and derive the Ollama endpoint from the existing AI
runtime configuration when no override is supplied:

| Variable | Purpose |
| --- | --- |
| `EOS_STATUS_PROJECT_ROOT` | Repository root used to load EngineeringOS defaults. |
| `EOS_STATUS_LOCAL_URL` | Local web adapter URL (default: configured `127.0.0.1:8081`). |
| `EOS_STATUS_OLLAMA_URL` | Ollama URL (default: existing runtime configuration). |
| `EOS_STATUS_PUBLIC_URL` | Protected public endpoint URL. |
| `EOS_STATUS_WEB_SERVICE` | systemd service name for EngineeringOS. |
| `EOS_STATUS_CLOUDFLARED_SERVICE` | systemd service name for cloudflared. |
| `EOS_STATUS_LISTEN_PORTS` | Comma-separated ports shown in the listener check. |

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
