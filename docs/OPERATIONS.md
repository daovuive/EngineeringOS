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
python eng.py knowledge ask "What is EngineeringOS?"
python eng.py knowledge organize --file incoming/my-note.md --dry-run
python eng.py knowledge organize --file incoming/my-note.md
python eng.py add-knowledge "my-document.md"
python eng.py add-knowledge --file "my-document.md" --auto-index
python eng.py add-knowledge --text "New knowledge content" --title "My note"
python eng.py add-knowledge --stdin --title "My note" < notes.txt
python eng.py add-knowledge "my-document.md" --no-index
```

`add-knowledge` accepts exactly one file, direct text, or stdin source and saves
it under `knowledge/inbox/`. It accepts UTF-8 `.md`, `.markdown`, and `.txt`,
copies external input, never overwrites, deduplicates unchanged content, and
indexes automatically. If indexing fails, the saved document remains and the
command prints an exact retry command while returning nonzero. `--no-index`
intentionally skips indexing and does not claim RAG readiness.

The canonical [Knowledge Ingestion Guide](KNOWLEDGE_INGESTION.md) documents
web equivalents, exact states, duplicate/collision behavior, the full path to
RAG, and partial-failure recovery.

`knowledge organize` sends only the explicit UTF-8 Markdown file to the local
reasoning model and selects one configured, existing `knowledge/` destination.
It preserves the filename, never creates a directory or overwrites a file, and
copies by default. Add `--move` only when the source should be removed after a
successful placement. Rebuild the index afterwards with `knowledge index`.

## Engineering and architecture workflows

All workflow inputs are explicit UTF-8 text. They are analyzed as untrusted
data, never executed, and never modified. Use one or more `--file`/`--text`
arguments; relative file paths resolve from `--root`.

```powershell
python eng.py workflow code-review --file change.diff
python eng.py workflow requirement-review --file requirements.md
python eng.py workflow adr-assistant --file decision-brief.md --with-knowledge
python eng.py workflow solution-architect --file architecture-brief.md --with-knowledge
```

`--knowledge-query "..."` can focus optional retrieval. Without
`--with-knowledge`, the workflow uses only the supplied input and returns no
repository citations. Results are review artifacts: they do not change source
files, save ADRs, or approve decisions.

Solution Architect makes one schema-constrained reasoning call, validates the
typed relationships, and deterministically renders its diagram, stages, draft
ADR, and evidence appendix. Output is currently buffered; allow roughly three
minutes for a local run on the configured host before treating it as stalled.

The browser provides the same four modes. API clients can send:

```json
{
  "input": "Problem, stakeholders, requirements, constraints and context",
  "source_name": "architecture-brief",
  "with_knowledge": true,
  "knowledge_query": "relevant architecture trade-offs"
}
```

to `/api/v1/workflows/solution-architect`. The other IDs are `code-review`,
`requirement-review`, and `adr-assistant`.

The browser provides five workspaces: Knowledge, Ask EOS, Engineering, Models,
and Project, plus one shared Activity surface. See the
[WebUI Guide](WEBUI_GUIDE.md) for navigation, preview/confirmation, recovery,
responsive behavior, and real-data runtime behavior. See
[Command and Web Coverage](COMMAND_COVERAGE.md) for the complete CLI mapping and
host-diagnostic exception.

An already-running Python web process must be restarted by the operator after
this version is deployed before the new API routes become active. Updating the
working tree alone does not reload Python modules. Repository implementation
does not authorize or perform that deployment/restart.

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
