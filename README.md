# EngineeringOS

> Personal Engineering Knowledge Platform powered by Local AI.

## Vai trò của README gốc

Đây là kim chỉ nam ổn định của project: mục đích, tầm nhìn, nguyên tắc và khung
trách nhiệm. Chỉ sửa, thay thế, đổi tên hoặc xóa file này sau khi chủ project
duyệt rõ ràng bản thay đổi cụ thể. Việc thêm tài liệu hoặc skill trong phạm vi
đã có được thực hiện qua README con; không cần sửa hiến chương mỗi lần.

Quy trình chi tiết nằm trong [quy tắc cấu trúc](docs/STRUCTURE_GOVERNANCE.md).
AI bắt đầu từ file này, đọc manifest rồi đi theo cây README đến thư mục đích.

## Mục đích và tầm nhìn

EngineeringOS lưu giữ và tổ chức kiến thức kỹ thuật, kinh nghiệm thiết kế,
architecture decisions, lessons learned và tài sản tái sử dụng xuyên suốt sự
nghiệp. Giá trị của project tăng khi kiến thức có thể tìm lại, kiểm chứng và
áp dụng vào công việc mới.

Project hỗ trợ phát triển từ nền tảng engineering và Feature Owner hướng tới
Solution Architect; kết hợp học tập, tư duy hệ thống, ra quyết định và Local AI.
Định hướng nghề nghiệp chi tiết nằm trong [career](career/README.md).

## Phạm vi

- Quản lý kiến thức, tiêu chuẩn kỹ thuật, requirements, kiến trúc và ADR.
- Học Architect liên tục; lưu bài học, bài tập, tiến độ và kinh nghiệm.
- Phân tích công việc và nghề nghiệp từ nguồn bằng chứng thực tế.
- Tái sử dụng skills, prompts, templates, tools và vai trò agent.
- Dùng Local AI để tìm kiếm, phân tích và hỗ trợ tác vụ kỹ thuật.

EngineeringOS không thay thế Git, Jira, Confluence hay CI/CD, và không phải kho
chứa mã nguồn của mọi project. Code vận hành chính EngineeringOS thuộc module
riêng. Tích hợp ngoài chỉ được bổ sung khi có nhu cầu và ranh giới rõ ràng.

## Nguyên tắc kiến trúc

1. Knowledge First: giữ nguồn, ngữ cảnh, quyết định và khả năng truy xuất lâu dài.
2. Architecture First: bắt đầu từ vấn đề, stakeholders, requirements, chất lượng
   và constraints; dùng bằng chứng và trade-offs để quyết định.
3. Local AI First: ưu tiên riêng tư, kiểm soát dữ liệu và khả năng chạy cục bộ;
   ranh giới runtime cho phép thay provider mà không thiết kế lại kho kiến thức.
4. Human in Control: AI hỗ trợ; người dùng quyết định thay đổi định hướng và
   kiến trúc quan trọng. Không biến giả định hoặc mục tiêu thành kinh nghiệm.
5. Configuration as Data: cấu trúc và registry được khai báo, tránh hard-code
   đường dẫn hoặc tạo cơ chế cấu hình thứ hai.
6. Một nguồn chính cho mỗi nội dung: liên kết và tái sử dụng thay vì sao chép.
7. Ưu tiên maintainability, extensibility, reliability, findability và giới hạn
   độ phức tạp để project phát triển lâu dài.

## Khung trách nhiệm

```text
Người dùng / AI
    -> đọc README + manifest + README vùng liên quan
    -> agent điều phối vai trò khi cần
    -> skill thực hiện workflow
    -> career / knowledge / memory cung cấp ngữ cảnh và bằng chứng
    -> prompts / tools / templates hỗ trợ
    -> engineering_os + configs cung cấp CLI và runtime abstraction
    -> runtime / logs chứa dữ liệu sinh ra
    -> kiểm tra kết quả và trả lại người dùng
```

Đây là phân chia trách nhiệm, không phải tuyên bố mọi thành phần đều đã được
tự động hóa. Trạng thái triển khai nằm trong [kiến trúc hiện tại](docs/ARCHITECTURE.md);
kế hoạch phát triển nằm trong [roadmap](docs/ROADMAP.md).

## Cấu trúc project và nơi đặt nội dung

[Manifest](configs/project-structure.json) là inventory máy đọc; bảng sau mô tả
trách nhiệm cấp cao. Mỗi README con giải thích chi tiết loại file, nguồn chính
và cách mở rộng. Tài liệu mới được nối vào cây này qua README gần nhất.

| Thư mục | Trách nhiệm |
| --- | --- |
| [ADR/](ADR/README.md) | Quyết định kiến trúc của chính EngineeringOS. |
| [docs/](docs/README.md) | Tài liệu vận hành, kiến trúc và quản trị của chính EngineeringOS. |
| [career/](career/README.md) | Định hướng nghề nghiệp, kế hoạch năng lực, hồ sơ thực tế và nguồn tham khảo thị trường. |
| [templates/](templates/README.md) | Mẫu tạo artifact dùng chung cho project. |
| [scripts/](scripts/README.md) | Script vận hành hỗ trợ EngineeringOS khi thật sự cần. |
| [configs/](configs/README.md) | Cấu hình dạng dữ liệu: manifest cấu trúc, schema, runtime, settings, template registry và skill registry. |
| [agents/](agents/README.md) | Định nghĩa vai trò và cách điều phối công việc của AI. |
| [runtime/](runtime/README.md) | Dữ liệu sinh ra khi chạy: model, cache, index và dữ liệu runtime cục bộ. |
| [memory/](memory/README.md) | Ngữ cảnh dài hạn của project dưới dạng ghi chú có nguồn và ngày cập nhật. |
| [logs/](logs/README.md) | Log do công cụ sinh ra. |
| [tests/](tests/README.md) | Kiểm tra hành vi của CLI và các module EngineeringOS. |
| [experiments/](experiments/README.md) | Thử nghiệm có phạm vi, giả thuyết, cách chạy và kết quả. |
| [prompts/](prompts/README.md) | Prompt hoặc đoạn prompt dùng lại. |
| [tools/](tools/README.md) | Tích hợp hoặc công cụ ngoài phục vụ EngineeringOS. |
| [engineering_os/](engineering_os/README.md) | Mã Python của EngineeringOS: CLI, cấu hình, tạo/kiểm tra cấu trúc, runtime abstraction và tìm kiếm Markdown. |
| [skills/](skills/README.md) | Nguồn chính cho workflow AI tái sử dụng. |
| [knowledge/](knowledge/README.md) | Kho kiến thức kỹ thuật tích lũy. |

Root chỉ giữ README.md, AGENTS.md, eng.py, pyproject.toml, LICENSE và .gitignore
theo allowlist trong manifest. Nội dung mới cần thuộc một vùng đã có; thay đổi
ranh giới hoặc thêm thư mục cấp một cần đề xuất và duyệt lại hiến chương.

## Skills và agents

[Skills](skills/README.md) chứa một workflow chính tại
`skills/<skill-id>/SKILL.md`, đăng ký trong [skill registry](configs/skills.json).
Skill đọc nguồn career/knowledge, không chứa bản sao dữ liệu đó.
[Agents](agents/README.md) quy định vai trò và cách điều phối; agent tham chiếu
skill thay vì chép workflow. Helper riêng của một skill ở trong package đó.

Khi hỏi học Architect, đi qua [chương trình Architect](knowledge/architect/README.md)
để đọc roadmap và tiến độ trước khi chọn bài. Khi hỏi job hoặc career, đi qua
[career](career/README.md) và skill tương ứng.

## Quy trình mở rộng

1. Đọc README gốc, manifest, quy tắc cấu trúc và README từ cha đến thư mục đích.
2. Tìm nguồn chính đã có; chọn nơi lưu theo trách nhiệm, không theo tiện tay.
3. Thêm nội dung và liên kết trong README gần nhất. Thư mục mới phải có README,
   entry manifest và liên kết từ cha; skill mới phải có entry registry.
4. Giữ đồng bộ liên kết khi di chuyển/đổi tên. Không tự sửa README gốc hoặc
   baseline bảo vệ khi chưa được duyệt.
5. Chạy `python eng.py validate` và kiểm tra phù hợp; báo rõ kết quả và giới hạn.

Hướng dẫn này cùng bộ kiểm tra giúp phát hiện sai lệch; nó không thay thế quyền
truy cập hoặc review độc lập để ngăn mọi công cụ ghi sai.

## Tài liệu mở rộng

- [Quy tắc cấu trúc và duyệt thay đổi](docs/STRUCTURE_GOVERNANCE.md).
- [Kiến trúc hiện tại](docs/ARCHITECTURE.md).
- [Vận hành và kiểm tra](docs/OPERATIONS.md).
- [Bối cảnh và bài thực hành kiến trúc ban đầu](docs/ARCHITECTURE_CONTEXT.md).
- [Roadmap, backlog và tài liệu project](docs/README.md).
- [Quyết định kiến trúc](ADR/README.md).
