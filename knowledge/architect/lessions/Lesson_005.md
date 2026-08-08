# Lesson 005 — Architecture Decisions

## Status
Completed.

## 1. English
An architecture decision records a significant choice about how the system should be structured or behave.

## 2. Giải thích bằng tiếng Việt
Architect không chỉ liệt kê requirements. Architect phải chuyển requirements, ASRs và constraints thành decisions, cùng với rationale và trade-offs.

## 3. Architect Mindset
WHY trước HOW. Không chọn solution chỉ vì nó quen thuộc.

## 4. Real-world Case Study — Bosch OTA
Các decisions đã thảo luận:
1. Update message distribution cần retry.
2. Vehicle cần cache đủ lớn để chứa software trước khi update.
3. Update phía vehicle thực hiện offline; quá trình này là download-only.

## 5. iSAQB Mapping
Architecture decisions là trung tâm của architecture work và cần được đánh giá dựa trên requirements, quality attributes và constraints.

## 6. Mini Exercise
Với OTA 15 million vehicles, xác định decision, rationale, trade-off.

## 7. Reflection
Một decision tốt phải trả lời WHY và chỉ ra trade-off.

## 8. Summary
Requirement → ASR/Constraint → Architecture Decision → Trade-off.

## 9. Flashcards
- Architecture Decision? → Significant choice shaping the architecture.
- Tại sao cần rationale? → Để giải thích WHY và hỗ trợ evolution/review.

## 10. Keywords
Architecture Decision, Rationale, Trade-off, ASR, Constraint.
