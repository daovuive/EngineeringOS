# Lesson 008 — Loose Coupling & High Cohesion

## Status
Completed after extended review.

## 1. English
Cohesion describes how strongly responsibilities inside a building block belong together.
Coupling describes how strongly one building block depends on another.

Good architecture generally aims for high cohesion and loose/controlled coupling.

## 2. Giải thích bằng tiếng Việt
Cohesion nhìn vào bên trong:
> Những responsibility trong component có thực sự thuộc về nhau không?

Coupling nhìn qua boundary:
> Component này phụ thuộc component khác đến mức nào?

Dependency không xấu. Zero coupling không phải mục tiêu.

## 3. Architect Mindset
Đánh giá coupling không chỉ bằng số lượng mũi tên. Hãy hỏi:
- Dependency vào interface hay implementation?
- Dependency vào internal knowledge hay stable contract?
- Change của A có lan sang B không?
- Failure của B có làm A fail không?

User đã nhận ra:
> “Cần phải biết mỗi component có responsibility rõ ràng thì mới chia tách được.”
Và:
> “Đề bài chưa cụ thể thì phải?”

Đây là Architect mindset: nếu problem chưa đủ rõ, phải clarify thay vì đoán architecture.

## 4. Real-world Case Study — Bosch OTA / Order-Payment
OTA:
Campaign → Download có dependency nhưng Campaign không cần biết retry/chunk/network/storage.
Order/Payment:
Order cần Payment capability nhưng Payment failure không được làm mất Order.

Một insight quan trọng:
> Business relationship ≠ direct architectural dependency ≠ failure propagation.

## 5. iSAQB Mapping
Loose coupling/high cohesion nằm trong Week 2 Design Principles, cùng với information hiding và dependency inversion.

## 6. Mini Exercise
OrderService → Payment:
- Payment only needs orderId, amount, currency.
- Payment failure must not lose Order.
User chọn contract nhỏ hơn và nhận ra failure isolation.

## 7. Reflection
Dependency không tự động là xấu.
Mục tiêu là necessary, explicit, manageable dependency.
Failure coupling phải được xem xét riêng.

## 8. Summary
High Cohesion + Controlled Coupling.
Dependency → contract → failure propagation → change propagation → blast radius.

## 9. Flashcards
- Cohesion? → Mức độ responsibilities trong block thuộc về nhau.
- Coupling? → Mức độ dependency giữa blocks.
- Zero coupling? → Không phải mục tiêu.
- Failure coupling? → Mức độ failure của một block gây failure/degradation ở block khác.

## 10. Keywords
Cohesion, Coupling, Loose Coupling, Tight Coupling, Dependency, Contract, Failure Isolation, Blast Radius.
