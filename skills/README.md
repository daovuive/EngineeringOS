# skills

[Thư mục cha](../README.md) · [Quy tắc cấu trúc](../docs/STRUCTURE_GOVERNANCE.md)

## Mục đích và ranh giới

Nguồn chính cho workflow AI tái sử dụng. Mỗi skills/<skill-id>/SKILL.md có một ID kebab-case ổn định và một entry trong configs/skills.json. Agent điều phối, skill mô tả cách làm, knowledge/career cung cấp dữ liệu. Chỉ tạo references/templates/scripts khi cần.

## Thư mục con

- [analyze-job-description](analyze-job-description/README.md): Package phân tích JD.
- [career-direction-review](career-direction-review/README.md): Package đánh giá định hướng nghề nghiệp.

## Khi mở rộng

Mỗi SKILL.md cần nêu input, output, workflow, nguồn phụ thuộc và quality checks.
ID phải ổn định, dùng kebab-case. Supporting references, templates hoặc scripts
chỉ thuộc package khi cần cho workflow đó; không sao chép nguồn career/knowledge.

Thêm file đúng ranh giới trên và liên kết từ mục lục này. Thư mục con mới cần được đăng ký trong manifest, có README.md riêng và liên kết từ README cha. Áp dụng quy trình và kiểm tra trong tài liệu quy tắc cấu trúc.
