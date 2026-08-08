# Lesson 006 — Decomposition & Separation of Concerns

## Status
Completed after extended review.

## 1. English
Decomposition is breaking a complex system into meaningful building blocks with clear responsibilities, interfaces and relationships.
Separation of concerns means separating different responsibilities so they can be understood and changed more independently.

## 2. Giải thích bằng tiếng Việt
Decomposition không đơn giản là chia nhỏ thành nhiều component. Mục tiêu là tìm meaningful boundaries.

Architect hỏi:
- Responsibility nào thuộc về nhau?
- Nếu requirement thay đổi thì phần nào nên thay đổi?
- Workload/quality characteristics có khác nhau không?

## 3. Architect Mindset
Không hỏi “có bao nhiêu service?”, mà hỏi “boundary nên ở đâu và WHY?”.

Một insight quan trọng từ user:
> “Cần phải biết mỗi component có responsibility rõ ràng thì mới chia tách được.”

Nếu problem statement chưa đủ cụ thể thì chưa nên đưa ra architecture decision chắc chắn.

## 4. Real-world Case Study — Bosch OTA
Campaign Management:
- cho biết xe nào cần update/download;
- software nào;
- campaign/rollout context.

Download Management:
- xử lý download;
- retry/resume;
- network interruption;
- progress;
- quyết định HOW/WHEN trong phạm vi responsibility của nó.

User kết luận:
> Campaign và Download nên khác boundary vì một bên thay đổi/scale không nhất thiết ảnh hưởng bên kia.

## 5. iSAQB Mapping
Week 2 Design Principles: decomposition, separation of concerns, building blocks, top-down/bottom-up, cohesion/coupling.

## 6. Mini Exercise
Case OTA:
- Campaign Management
- Vehicle Management
- Package Management
- Download Management
- Installation
- Monitoring

Hãy tìm meaningful boundaries, không mặc định mỗi responsibility = một service.

## 7. Reflection
Một Architect phải biết challenge problem statement. Nếu responsibility, requirements, quality attributes, constraints và dependencies chưa đủ rõ, boundary chỉ là assumption.

## 8. Summary
System → Responsibilities → Boundaries → Cohesion/Coupling → Architecture Decision.

## 9. Flashcards
- Decomposition? → Breaking complexity into meaningful building blocks.
- Có phải càng nhiều component càng tốt? → Không.
- Boundary tốt? → Boundary có responsibility rõ, change impact hợp lý và dependency được kiểm soát.

## 10. Keywords
Decomposition, Separation of Concerns, Building Block, Responsibility, Boundary, Top-down, Bottom-up.
