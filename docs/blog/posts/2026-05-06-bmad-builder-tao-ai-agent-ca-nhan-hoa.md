---
date: 2026-05-06
categories:
  - Agent
tags:
  - bmad-method
  - bmad-builder
  - ai-agent
  - ai-memory
  - autonomous-agent
level: advanced
status: published
description: "Khám phá BMad Builder — công cụ mạnh mẽ trong hệ sinh thái BMad giúp bạn tự tạo ra các AI Agent có trí nhớ dài hạn (Memory Agents), tự động hóa (Autonomous) và đóng gói thành module để chia sẻ."
authors:
  - tranvanhoan
---

# BMad Builder — Công cụ "Đúc" AI Agent Có Trí Nhớ Và Cá Tính Riêng

## Mở đầu: Lời nguyền "mất trí nhớ" của AI

Hãy nhớ lại lần gần nhất bạn dùng Claude, ChatGPT hay Cursor để làm việc. Bạn mất 30 phút để giải thích cho AI hiểu văn phong viết blog của bạn, dự án bạn đang làm, và các quy tắc coding bạn muốn tuân thủ. AI làm rất tốt. Nhưng ngày hôm sau, bạn mở một đoạn chat mới, và... AI lại trở thành một "tờ giấy trắng". Bạn lại phải copy/paste đống context đó một lần nữa.

Làm việc với AI hiện nay giống như làm việc với một người cực kỳ thông minh nhưng lại mắc chứng **mất trí nhớ ngắn hạn (amnesia)**. 

Đó chính là lý do **BMad Builder** ra đời. Nếu BMad Method cung cấp cho bạn một quy trình có sẵn, thì **BMad Builder** cung cấp cho bạn "xưởng đúc" để tự tạo ra các AI Agent **có trí nhớ dài hạn, có cá tính riêng, và thậm chí biết tự động làm việc khi bạn đang ngủ**.

**Nội dung bài viết:**

- BMad Builder là gì và sự khác biệt cốt lõi
- Phân biệt Workflow và Agent
- 3 Cấp độ Agent: Stateless, Memory, Autonomous
- Cơ chế trí nhớ (Memory) hoạt động ra sao?
- Đóng gói và phân phối với Modules
- Quy trình 4 bước build một Agent
- Ví dụ thực tế: Tạo "Writing Partner" có trí nhớ

---

## 1. BMad Builder là gì?

BMad Builder là một module cốt lõi trong hệ sinh thái BMad Method. Khẩu hiệu của nó là: *"Build More, Architect Dreams"* (Xây dựng nhiều hơn, Kiến tạo giấc mơ).

Nó là một bộ công cụ (builder wizards) giúp bạn chuyển hóa các ý tưởng thành các "kỹ năng" (skills) hoặc "tác nhân" (agents) cài đặt trực tiếp vào hệ thống Claude Code hoặc các AI IDE khác. BMad Builder cho phép bạn tạo ra:

1. **Personal AI Companions**: Những trợ lý AI có khả năng đồng hành, nhớ các sở thích và thói quen của bạn theo thời gian.
2. **Domain Experts**: Chuyên gia trong một lĩnh vực cực hẹp (luật sư, bác sĩ nội trú, chuyên gia sáng tạo).
3. **Workflow Automations**: Những quy trình tự động hóa thay vì phải gõ lệnh thủ công.
4. **Custom Modules**: Gói tất cả những thứ trên lại thành một "Plugin" để chia sẻ cho team hoặc bán trên marketplace.

---

## 2. Điểm khác biệt: Workflow vs. Agent

Trước khi đi sâu, chúng ta cần phân biệt rõ hai khái niệm mà BMad Builder hỗ trợ tạo ra:

- **Workflow (Luồng công việc)**: Là một quy trình cứng. Nó giống như một kịch bản từng bước (Step 1 làm gì, Step 2 làm gì). Nó không có tính cách, chỉ là công cụ thực thi. *Ví dụ: Workflow tự động tạo file `README.md` từ source code.*
- **Agent (Tác nhân AI)**: Là một "nhân sự" thực thụ. Nó là sự kết hợp của **Persona** (Tính cách/Vai trò) + **Capabilities** (Năng lực/Tools) + **Memory** (Trí nhớ, tùy chọn). Agent có thể trò chuyện với bạn, tự quyết định dùng tool nào, và rút kinh nghiệm cho lần sau.

Nếu bạn không chắc nên tạo cái gì, lời khuyên từ BMad là: *Hãy bắt đầu với Workflow. Khi nào thấy cần nó tự chủ và cá nhân hóa hơn, hãy nâng cấp nó thành Agent.*

---

## 3. Ba cấp độ Agent trong BMad Builder

Điều làm nên sức mạnh của BMad Builder là nó chia Agent thành 3 cấp độ tiến hóa rõ rệt:

### Cấp độ 1: Stateless Agents (Chuyên gia vô hình)

- **Đặc điểm**: Không có trí nhớ. Mỗi lần khởi động lại là một phiên hoàn toàn độc lập. Mọi hướng dẫn đều nằm chung trong một file `SKILL.md`.
- **Khi nào dùng**: Khi context của phiên làm việc cũ không ảnh hưởng gì đến phiên hiện tại.
- **Ví dụ**: Agent chuyên dịch thuật tài liệu JSON, Agent review lỗi bảo mật của hàm hiện tại. Bạn không cần Agent nhớ hôm qua nó đã dịch file nào, bạn chỉ cần nó dịch chuẩn file hôm nay.

### Cấp độ 2: Memory Agents (Người đồng hành có trí nhớ)

- **Đặc điểm**: Đây là nơi phép màu xuất hiện. Agent có một **"Sanctum" (Thánh địa trí nhớ)** — một thư mục riêng biệt trên máy của bạn (thường ở `_bmad/memory/<agent-name>/`).
- **Cách hoạt động**: 
    - Lần đầu kích hoạt, Agent sẽ trải qua quá trình **"First Breath" (Hơi thở đầu tiên)**. Nó sẽ phỏng vấn bạn để biết bạn là ai, mục tiêu của bạn là gì, và nó cần thích nghi thế nào.
    - Trong các lần sau, dù bạn mở chat mới, Agent vẫn sẽ đọc các file trong Sanctum để "nhập hồn" trở lại đúng con người cũ. Nếu nó không nhớ điều gì, nó sẽ thú nhận và lục lại trí nhớ.
- **Khả năng tiến hóa**: Memory agents có thể "Học" (Learned capabilities). BMad hỗ trợ người dùng dạy Agent những prompt mới, và nó sẽ tự lưu vào repertoire (danh sách kỹ năng) của nó.
- **Ví dụ**: Một Agent *Writing Coach*. Lần đầu nó hỏi bạn thích văn phong nào (nghiêm túc, hài hước, dùng nhiều icon). Sau đó, nó tự lưu vào memory. Các bài viết sau, bạn không cần nhắc lại, nó tự động review theo đúng gu của bạn.

### Cấp độ 3: Autonomous Agents (Nhân viên mẫn cán)

- **Đặc điểm**: Có tất cả mọi thứ của Memory Agent, nhưng được trang bị thêm file **PULSE**. 
- **Cách hoạt động**: PULSE định nghĩa những việc Agent làm *khi không có ai giám sát*. Autonomous Agent có thể được đánh thức bằng cronjob hoặc background task. Khi có người, nó chat; khi không có người (headless), nó tự làm việc rồi thoát.
- **Ví dụ**: Agent *Project Maintainer*. Mỗi sáng lúc 2h, nó tự động thức dậy, đọc qua git commit, dọn dẹp các memory rác, summarize tiến độ dự án, và để lại một file báo cáo tóm tắt cho bạn đọc lúc 8h sáng.

!!! info "Sự riêng tư của Memory (Trí nhớ)"
    Một thiết kế cực hay của BMad: Trí nhớ của Agent được lưu ở cấp độ **Project** (ví dụ `_bmad/memory/`), không lưu trong thư mục lõi của Agent. Nhờ vậy, cùng một Agent "Code Reviewer" nhưng ở Project A nó sẽ học theo chuẩn code của Project A, sang Project B nó lại học theo chuẩn của Project B. Dữ liệu hoàn toàn local và thuộc về dự án.

---

## 4. Modules: Đóng gói và Phân phối

Agent hay Workflow dù hay đến mấy cũng vô nghĩa nếu không thể cài đặt hoặc chia sẻ. BMad giải quyết vấn đề này qua **Modules**.

Module thực chất là một Plugin (giống `.claude-plugin/`). Một Module có thể chứa:
- Một Agent duy nhất (Standalone module).
- Nhiều Agent kết hợp làm việc cùng nhau (Multi-skill modules).

Điểm ăn tiền của BMad Module là **khả năng tích hợp hệ thống Help (`bmad-help`)**. Khi bạn cài một module, nó sẽ đăng ký các tính năng của nó vào file `config.yaml` và `module-help.csv`. Từ đó, user chỉ cần gõ `bmad-help` là AI IDE (như Claude Code) sẽ hướng dẫn họ nên dùng Agent nào của bạn trong hoàn cảnh nào.

---

## 5. Quy trình 4 bước tạo Agent bằng BMad Builder

Việc tạo ra các Agent này không yêu cầu bạn phải code Python phức tạp. Bạn dùng chính AI để đẻ ra AI thông qua các wizard của BMad Builder. Quy trình chuẩn như sau:

1. **Step 1: Ideate (Lên ý tưởng - Tùy chọn)**
   - Chạy lệnh: `bmad-module-builder` -> chọn *Ideate Module (IM)*.
   - Builder sẽ đóng vai facilitator, hỏi bạn các câu hỏi để chốt persona, chức năng, và loại agent cần thiết. Kết quả là một bản Plan.

2. **Step 2: Build Skills (Xây dựng kỹ năng)**
   - Gọi *Agent Builder* hoặc *Workflow Builder*. Bạn cung cấp bản Plan ở bước 1.
   - Builder sẽ tự động tạo cấu trúc thư mục, file `SKILL.md`, các file script cần thiết. Nếu là Memory Agent, nó sẽ setup sẵn thư mục Sanctum và kịch bản First Breath.

3. **Step 3: Scaffold the Module (Đóng gói)**
   - Chạy lệnh *Create Module (CM)*.
   - Builder tự động sinh file `marketplace.json`, file setup để cài đặt, và các file đăng ký vào `bmad-help`.

4. **Step 4: Validate (Kiểm định)**
   - Chạy lệnh *Validate Module (VM)*. Builder sẽ kiểm tra xem agent có bị lỗi cấu trúc, thiếu context, hay xung đột với các module khác không.

---

## 6. Case Study: Xây dựng "Blog Writing Partner" (Memory Agent)

Hãy thử hình dung cách chúng ta dùng BMad Builder tạo ra một người bạn đồng hành viết Blog (Memory Agent):

1. **Thiết kế Persona**: Tên là "Leo", một biên tập viên nghiêm khắc nhưng tận tâm.
2. **Khởi tạo (First Breath)**: 
   - Khi tôi gọi Leo lần đầu, Leo tự động tạo thư mục `_bmad/memory/leo/`.
   - Leo hỏi: *"Chào Hoàn, tôi cần biết blog của bạn viết về chủ đề gì, đối tượng người đọc là ai, và bạn ghét những từ sáo rỗng nào của AI (như 'hòa mình vào', 'thế giới kỹ thuật số')?"*
   - Tôi trả lời. Leo lưu tất cả vào `_bmad/memory/leo/owner-understanding.md`.
3. **Quá trình sử dụng**:
   - Tuần sau, tôi viết một đoạn draft lủng củng và gọi: *"Leo, review giúp."*
   - Dù là phiên làm việc mới, Leo tự động đọc file `owner-understanding.md`. Nó trả lời: *"Bài này ổn, nhưng bạn lại lỡ dùng từ 'bức tranh toàn cảnh' rồi — hôm trước bạn bảo rất ghét từ này. Tôi đã sửa lại giúp bạn theo phong cách ngắn gọn quen thuộc."*
4. **Tiến hóa**:
   - Tôi gõ lệnh: *"Leo, hãy học rule mới: luôn chèn một bảng so sánh vào giữa bài."*
   - Leo ghi nhận điều này vào file `learned-capabilities.md` trong Sanctum của nó. Lần sau, nó tự động áp dụng.

## Kết luận

**BMad Builder** đã đẩy ranh giới của AI coding assistant đi xa hơn rất nhiều. Nó biến các cuộc trò chuyện rời rạc, "não cá vàng" thành những sự cộng tác có tính liên tục, tích lũy kiến thức (Memory) và thậm chí là tự chủ (Autonomous).

Với cấu trúc Module dễ chia sẻ, BMad Builder không chỉ là công cụ cho cá nhân mà còn mở ra cơ hội xây dựng các **AI Marketplace** chuyên biệt trong tương lai, nơi bạn có thể tải về một Agent "Chuyên gia MLOps", một Agent "Kế toán thuế",... và chúng sẽ tự học để phù hợp riêng với dự án của bạn.

---

## Tham khảo

- [BMad Builder Documentation](https://bmad-builder-docs.bmad-method.org/) — Tài liệu chính thức.
- [What Are BMad Agents?](https://bmad-builder-docs.bmad-method.org/explanation/what-are-bmad-agents/) — Phân loại Stateless, Memory, Autonomous.
- [Understanding Modules](https://bmad-builder-docs.bmad-method.org/explanation/what-are-modules/) — Cách đóng gói và chia sẻ agent.
- [Build Your First Module Tutorial](https://bmad-builder-docs.bmad-method.org/tutorials/build-your-first-module/) — Hướng dẫn step-by-step.
