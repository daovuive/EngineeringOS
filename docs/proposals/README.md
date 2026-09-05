# docs/proposals

[Thư mục cha](../README.md) · [Quy tắc cấu trúc](../../docs/STRUCTURE_GOVERNANCE.md)

## Mục đích và ranh giới

Bản đề xuất đang chờ chủ project duyệt, kèm tác động và patch nếu cần. Nội dung trong vùng này không thay thế quy tắc đang có hiệu lực. Sau khi duyệt, áp dụng vào nguồn chính và ghi lại quyết định duyệt.

## Tài liệu và file hiện có

- [Bản đọc để duyệt](ROOT_README.proposed.md): nội dung README gốc đề xuất; liên kết trong preview được chỉnh tương đối từ thư mục này để có thể bấm xem.
- [Diff chính xác cho README gốc](root-readme.patch): thay phần giới thiệu dài và bài thực hành bằng hiến chương, sơ đồ trách nhiệm và cây liên kết. Đường dẫn trong patch được tính từ root.

## Quyết định duyệt và trạng thái áp dụng

Chủ project đã duyệt ngày 2026-09-05 bằng yêu cầu: “tốt, thực hiện thay đổi.”
Trạng thái: **Approved / Applied**. Patch đã được áp dụng vào README.md gốc,
hash bảo vệ đã cập nhật và `rootNavigationPendingApproval` đã đặt thành `false`.
Bản đọc và patch được lưu lại làm lịch sử, không áp dụng lại patch này.

Bản được duyệt giữ mục tiêu Local AI và phát triển
Solution Architect, đưa chi tiết biến động sang docs/, chỉ rõ skills/agents và
quy trình mở rộng. Bài thực hành cũ đã được lưu ở
[Architecture Context](../ARCHITECTURE_CONTEXT.md) và ghi rõ là bối cảnh lịch sử.

README gốc là nguồn có hiệu lực; bản preview không phải bản chính để cập nhật
cho các thay đổi sau này. Không tự áp dụng proposal chỉ vì nó có mặt trong
repository. Không thay đổi skill workflow hoặc roadmap học
trong đợt tổ chức README này; các nội dung đó vẫn thuộc đề xuất riêng trước đó.

## Khi mở rộng

Thêm file đúng ranh giới trên và liên kết từ mục lục này. Thư mục con mới cần được đăng ký trong manifest, có README.md riêng và liên kết từ README cha. Áp dụng quy trình và kiểm tra trong tài liệu quy tắc cấu trúc.
