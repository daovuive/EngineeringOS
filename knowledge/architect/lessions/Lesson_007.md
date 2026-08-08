# Lesson 007 — Information Hiding

## Status
Completed.

## 1. English
Information hiding means controlling what knowledge crosses an architectural boundary. A building block exposes necessary interfaces while hiding internal details and mechanisms.

## 2. Giải thích bằng tiếng Việt
Campaign chỉ cần biết:
- vehicle nào;
- software/package nào;
- và những domain/policy information thực sự cần thiết.

Download Manager tự quyết định:
- retry;
- chunking;
- timeout;
- network;
- storage;
- scheduling;
- implementation/protocol.

User's key conclusion:
> Campaign chỉ cần biết vehicle nào và ứng sw nào cần phải download... Download manager tự quyết định nó sẽ tải SW đến Vehicle và nên tải lúc nào, ntn nó tự quyết định. nếu download manager thay đổi mọi cách thức download thì ko ảnh hưởng campaign.

## 3. Architect Mindset
Không phải “hide everything”. Hãy hỏi:
> Who owns the decision?
Nếu consumer cần quyết định một domain/policy → có thể expose.
Nếu provider sở hữu implementation → hide.

## 4. Real-world Case Study — Bosch OTA
Ví dụ:
startDownload(vehicleId, packageId)
có thể đủ cho Campaign.
Download Manager tự xử lý retry, chunk, timeout, network, storage.

Nếu business requirement thật sự yêu cầu campaign chọn storage hoặc priority, những thông tin đó có thể trở thành một phần contract.

## 5. iSAQB Mapping
Black-box view chỉ expose provided/required interfaces và hide internal details. Information hiding giúp encapsulate complexity và hỗ trợ flexibility/changeability.

## 6. Mini Exercise
Interface ban đầu:
startDownload(vehicleId, packageId, retryCount, chunkSize, storagePath, timeout)
User đã nhận ra retryCount/chunkSize/timeout nên hide và đề xuất interface nhỏ hơn.

## 7. Reflection
Một abstraction tốt phải giữ lại domain meaning mà client cần, đồng thời hide representation và mechanism.

Ví dụ user nhận ra:
> “meaningful mới hiểu được. 8 thì không biết có 1000 không.”

## 8. Summary
Meaningful Requirement → Meaningful Abstraction → Stable Interface → Hide Implementation → Reduce Coupling.

## 9. Flashcards
- Information Hiding? → Kiểm soát knowledge đi qua boundary.
- Black box? → Client thấy interface, không thấy internal details.
- Ai sở hữu decision? → Đây là câu hỏi quan trọng để quyết định expose/hide.
- Policy vs mechanism? → Policy là WHAT/decision; mechanism là HOW/implementation.

## 10. Keywords
Information Hiding, Black Box, White Box, Interface, Encapsulation, Abstraction, Policy, Mechanism.
