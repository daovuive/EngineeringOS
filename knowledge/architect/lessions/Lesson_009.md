# Lesson 009 — Dependency Inversion

## Status
In progress / key understanding captured.

## 1. English
Dependency Inversion means high-level modules should not depend directly on low-level concrete modules. Both should depend on an abstraction.

## 2. Giải thích bằng tiếng Việt
Thay vì:
OrderService → StripePayment

có thể:
OrderService → IPayment ← StripePayment/PayPalPayment

High-level business logic phụ thuộc vào capability/abstraction, không phụ thuộc provider cụ thể.

## 3. Architect Mindset
User đã phát hiện trong exercise:
> “tôi nghĩ mình đang thiếu paymentservice.”

Đây là phản biện architecture hợp lý: abstraction cần có ownership/implementation rõ ràng.

User kết luận:
> “dựa trên nhu cầu của ordersrv, payment support nhiều provider điều đó ko có nghĩa là order phải nắm tất cả các provider này, thông tin này vốn dĩ thuộc về payment.”

Đây là core insight của DIP:
> Business should not adapt to technology/provider; technology should fit the business abstraction.

## 4. Real-world Case Study — Payment
Requirement:
- nhiều payment provider;
- provider có thể thay đổi;
- OrderService không cần biết provider.

Possible structure:
OrderService → IPayment ← Payment implementation(s) → Stripe/PayPal.

`IPayment` nên được thiết kế từ nhu cầu của OrderService, không copy Stripe API.

## 5. iSAQB Mapping
Dependency Inversion via interfaces và Dependency Injection là design principles trong roadmap. Mục tiêu là giảm direct dependency và tăng khả năng thay thế building blocks.

## 6. Mini Exercise
OrderService → StripePayment vs OrderService → IPayment ← Stripe/PayPal.
User chọn B.

User đề xuất:
IPayment chỉ chứa những gì OrderService cần expose/contract, không expose provider internals.

## 7. Reflection
Không phải cứ tạo interface là DIP. Cần có architectural reason để invert dependency.
Không over-design.

## 8. Summary
High-level policy → abstraction ← low-level implementation.
Business contract phải được thiết kế theo nhu cầu của business/high-level module.

## 9. Flashcards
- Dependency Inversion? → High-level và low-level cùng depend on abstraction.
- IPayment nên dựa trên gì? → Nhu cầu/capability mà OrderService cần.
- Provider details thuộc về ai? → Payment side, không phải Order.
- Có phải mọi dependency đều cần interface? → Không.

## 10. Keywords
Dependency Inversion, Abstraction, Interface, High-Level Module, Low-Level Module, Provider, Decoupling, Dependency Injection.
