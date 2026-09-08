# Quy tắc cấu trúc EngineeringOS

[Mục lục tài liệu](README.md) · [README gốc](../README.md)

## Mục tiêu và hiệu lực

Áp dụng yêu cầu của chủ project ngày 2026-09-05: README là khung hướng dẫn kiến
trúc, mọi file có nơi lưu rõ ràng, mở rộng bằng liên kết và hạn chế thay đổi
README gốc. Dùng thống nhất tên `README.md` theo repository hiện có; không tạo
song song `readme.md` trên Windows.

README gốc đã được chủ project duyệt và áp dụng ngày 2026-09-05. Bản đọc và
patch được giữ tại [hồ sơ đề xuất](proposals/README.md) để truy vết; README gốc
là nguồn có hiệu lực. `rootNavigationPendingApproval` được đặt thành `false`:
kiểm tra manifest, README con, các liên kết ổn định từ root và hash bảo vệ đều
có hiệu lực; root không phải mục lục đầy đủ của mọi folder/file.
Không bật lại ngoại lệ chuyển tiếp để che lỗi hoặc bỏ qua quy trình duyệt.

## Vai trò của từng nguồn

| Nguồn | Trách nhiệm |
| --- | --- |
| README.md ở gốc | Mục đích, tầm nhìn, nguyên tắc, ranh giới cấp cao và điều hướng; chỉ thay đổi khi chủ project duyệt |
| configs/project-structure.json | Inventory máy đọc của thư mục được quản lý, file bắt buộc và cấu hình kiểm tra |
| README.md trong từng thư mục | Mục đích, loại nội dung, ranh giới, mục lục con và quy tắc mở rộng tại chỗ |
| docs/ARCHITECTURE.md | Thiết kế và trạng thái triển khai có thể thay đổi theo phiên bản |
| skills/<id>/SKILL.md | Workflow tái sử dụng, input/output và cách kiểm tra |
| agents/ | Vai trò và điều phối skill; không sở hữu bản sao workflow |
| AGENTS.md | Điểm vào ngắn cho AI đọc các nguồn trên |

Manifest là inventory, không phải bản sao nội dung README. Nếu mục đích trong
README và manifest mâu thuẫn, nêu rõ xung đột và đề xuất chỉnh sửa đồng bộ; không
âm thầm chọn một nguồn để hợp thức hóa thay đổi ngoài phạm vi. Hướng dẫn mới
của chủ project có thể thay đổi thiết kế, nhưng phải được ghi nhận rõ.

## Cây điều hướng và độ ổn định của root

README gốc liên kết tới các vùng trách nhiệm ổn định và tài liệu quản trị; không
phải là mục lục đầy đủ của mọi thư mục/file. Manifest là inventory chính xác để
phát hiện thư mục cấp một mới. README cấp một liên kết xuống các README con;
mỗi README con liên kết ngược về README cha và liệt kê file thuộc phạm vi của
nó.

Mọi tài liệu mới được truy cập từ gốc thông qua cây liên kết này. Không thêm
một dòng vào README gốc cho mỗi lesson, JD hoặc skill; cập nhật mục lục gần
nhất. Cách này đáp ứng điều hướng từ root đồng thời hạn chế sửa hiến chương.

Mỗi README con cần nêu: mục đích, ranh giới nội dung, thư mục con, nguồn chính
hoặc file hiện có, quy tắc thêm nội dung. README chỉ là chỉ dẫn; không chép lại
toàn bộ lesson, JD, profile hoặc workflow.

## Chọn nơi đặt file

| Nội dung | Nơi đặt |
| --- | --- |
| Định hướng, kế hoạch nghề nghiệp | career/ |
| Hồ sơ, CV và bằng chứng nghề nghiệp | career/profile/ |
| JD, benchmark thị trường | career/job-market/<company>/ |
| Workflow AI dùng lại | skills/<skill-id>/SKILL.md; đăng ký một lần trong configs/skills.json |
| Vai trò và điều phối AI | agents/ |
| Lesson/tiến độ Architect hiện có | knowledge/architect/lessions/ |
| Roadmap Architect hiện có | knowledge/architect/Architect_Daily_Program_Roadmap.md |
| Sách của chương trình Architect | knowledge/architect/books/ |
| ASR học tập/nghiên cứu đang có | knowledge/architect/asr/ |
| Kiến thức kiến trúc dùng chung | knowledge/architecture/ theo phân loại con |
| Kiến thức Automotive hoặc standards | knowledge/automotive/ hoặc knowledge/standards/ |
| Kiến thức theo project | knowledge/projects/<project>/ |
| Quyết định kiến trúc của EngineeringOS | ADR/ |
| Thiết kế, vận hành và quy tắc project | docs/ |
| Đề xuất chờ duyệt | docs/proposals/ |
| Code Python của EngineeringOS | engineering_os/ |
| Cấu hình, registry | configs/ |
| Prompt, template dùng chung | prompts/ hoặc templates/ |
| Thử nghiệm | experiments/<experiment>/ |
| Dữ liệu chạy, index, cache | runtime/; không thay nguồn knowledge |

`architect/` phục vụ chương trình học cá nhân; `architecture/` là taxonomy kiến
thức dùng chung đã có trong manifest. Không tự gộp hoặc tạo bản sao giữa hai
vùng. Giữ tên lịch sử `lessions/` cho đến khi có yêu cầu migration riêng.

## Quy trình cho AI và người đóng góp

1. Đọc root, tài liệu này, manifest và chuỗi README dẫn đến đích.
2. Tìm nguồn tương tự trước khi tạo mới. Chọn một nơi lưu chính theo mục đích.
3. Khi thêm file trong phạm vi đã có, cập nhật README gần nhất và liên kết liên
   quan. Không phải xin duyệt root cho thay đổi nội dung thông thường đã được
   người dùng yêu cầu.
4. Khi thêm thư mục được quản lý, đăng ký `folders[]`, tạo README mô tả thật,
   liên kết từ README cha ở cấp cục bộ; nếu là thư mục cấp một thì manifest là
   điểm điều hướng chính và không cần thêm dòng vào root README. Nếu thư mục
   mới tạo ranh giới trách nhiệm cấp cao thì cần đề xuất và được chủ project
   duyệt trước.
5. Khi di chuyển/đổi tên/xóa, kiểm tra file đích, liên kết, registry và nội dung
   đang làm dở. Không ghi đè nguồn khác hoặc xóa hàng loạt để làm cấu trúc đẹp.
6. Chạy `python eng.py validate`, `git diff --check` và test phù hợp với code
   thay đổi. Kiểm tra bằng mắt rằng ý nghĩa file đúng với README nơi chứa nó.
7. Báo rõ thay đổi, kiểm tra đã chạy và phần còn cần duyệt. Không sửa baseline,
   registry hoặc ignore rule chỉ để bỏ qua một lỗi chưa được xử lý.

## Bảo vệ README gốc

Không sửa nội dung, tên, vị trí, xóa hoặc thay README gốc khi chưa có phê duyệt
rõ ràng của chủ project cho bản thay đổi cụ thể. Yêu cầu tổng quát như "dọn
project", "thêm skill" hay "sync" không tự cấp quyền sửa README gốc.

Trước khi xin duyệt, chuẩn bị draft/patch trong docs/proposals/, giải thích lý
do, tác động và xác minh liên kết. Sau khi duyệt: áp dụng đúng diff đã duyệt,
cập nhật `governance.protectedRootReadme.sha256` bằng SHA-256 của bytes mới,
ghi nhận phê duyệt và chạy kiểm tra. Baseline hiện tại tương ứng bản README
đã được chủ project duyệt ngày 2026-09-05.

Baseline hoặc trường bảo vệ không được tự cập nhật khi kiểm tra thất bại.
Validator phát hiện thay đổi so với baseline, không xác thực danh tính hoặc
lịch sử phê duyệt. `init`/`sync` không được ghi đè file đã tồn tại; khi README
bảo vệ bị mất, phải khôi phục bản đã duyệt thay vì dùng một mẫu chung.

## Phạm vi kiểm tra và ngoại lệ

Validator kiểm tra các vi phạm cơ học: đường dẫn manifest, file/thư mục bắt
buộc, README con không rỗng, thư mục ngoài manifest, root file ngoài danh sách,
liên kết README bị hỏng, điều hướng cha đến con và hash README gốc.
File trực tiếp trong mỗi thư mục được quản lý cũng phải có liên kết từ README
tại đó, trừ file khớp các pattern đã khai báo trong
`governance.autoIndexedFiles`; các vùng dữ liệu sinh tự động đã khai báo được
miễn mục lục file.
Skill registry được kiểm tra ID và đường dẫn khi có. Nội dung file có đúng domain,
kinh nghiệm có bằng chứng và thiết kế có hợp lý vẫn cần review theo task.

Ngoại lệ cho `.git`, môi trường Python, cache, dữ liệu runtime và vùng tạm
được khai báo tập trung trong manifest. Không yêu cầu README cho mỗi thư mục
model/cache/test sinh ra. `logs/README.md` được version; dữ liệu log bỏ qua.
Thư mục hoàn toàn rỗng còn sót sau migration không phải nguồn nội dung; không
lưu file mới ở đó để né đăng ký. Template có ví dụ đường dẫn trong code fence
không được xem là liên kết tài liệu thực.

Đây là hướng dẫn và kiểm tra phát hiện sai lệch, không phải khóa quyền ghi của
hệ điều hành. Chưa cài Git hook hay CI gate. AI hoặc công cụ bỏ qua kiểm tra
vẫn có thể ghi sai; một tác nhân có quyền sửa cả policy và validator cũng có
thể vô hiệu hóa chúng. Muốn cưỡng chế trước merge cần quy tắc review/CI hoặc
quyền truy cập độc lập bên ngoài repository, do chủ project cấu hình riêng.
