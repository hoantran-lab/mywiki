---
date: 2026-05-08
categories:
  - Agent
tags:
  - multi-agent-system
  - markdown-agents
  - claude-code
  - github-copilot
  - no-code
level: intermediate
status: published
description: "Hướng dẫn xây dựng hệ thống Multi-Agent hoàn toàn bằng file Markdown — không cần viết code framework. Chạy trực tiếp trên Claude Code, GitHub Copilot, Cursor."
authors:
  - tranvanhoan
---

# Multi-Agent System Bằng Markdown — Không Cần Viết Một Dòng Code Framework

## Mở đầu

Ở [bài trước](./2026-05-08-thuc-chien-multi-agent-system-waterfall-ipa.md), chúng ta đã thiết kế hệ thống MAS bằng code Python với LangGraph — một cách tiếp cận mạnh mẽ nhưng đòi hỏi phải viết code infrastructure. Câu hỏi đặt ra: **Nếu tôi chỉ muốn dùng Claude Code, GitHub Copilot hoặc Cursor — những công cụ đã có sẵn — thì sao?**

Câu trả lời: **Hoàn toàn được.** Bạn có thể xây dựng một hệ thống Multi-Agent hoàn chỉnh chỉ bằng **file Markdown**, không cần cài thêm framework, không cần viết code orchestration. Các AI coding agent hiện đại đều hỗ trợ cơ chế đọc file hướng dẫn (instruction files) để thay đổi hành vi — và đó chính là nền tảng để xây dựng "agent" và "skill" dưới dạng text.

**Nội dung chính:**

- Tại sao Markdown-based Agent hoạt động được
- Cấu trúc thư mục chuẩn cho Multi-Agent project
- Xây dựng từng Agent bằng file Markdown
- Thiết kế Orchestrator Workflow bằng text
- Cơ chế Review & Self-Healing hoàn toàn bằng prompt
- Tương thích đa nền tảng: Claude Code, GitHub Copilot, Cursor

---

## 1. Tại Sao Markdown-Based Agent Hoạt Động?

### Nguyên lý cốt lõi

Các AI coding agent (Claude Code, Copilot, Cursor) đều có cơ chế **đọc file hướng dẫn** khi khởi động hoặc khi thực hiện task:

| Công cụ | File hướng dẫn chính | Cơ chế load |
| :--- | :--- | :--- |
| **Claude Code** | `CLAUDE.md`, `AGENTS.md`, `.gemini/skills/*.md` | Load tự động khi bắt đầu session |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Load tự động trong mọi chat/agent interaction |
| **Cursor** | `.cursorrules`, `.cursor/rules/*.mdc` | Load tự động |
| **Gemini CLI** | `GEMINI.md`, `.gemini/skills/*.md` | Load tự động |

Khi bạn viết một file Markdown với nội dung: *"Bạn là System Architect. Nhiệm vụ của bạn là thiết kế kiến trúc hệ thống..."*, AI sẽ **đóng vai trò đó** trong suốt quá trình thực thi. Đây chính là "Agent" — không cần code Python, không cần import framework.

!!! info "Agent = Prompt + Context + Rules"
    Trong thế giới Markdown-based, một "Agent" đơn giản là một file `.md` chứa: **(1)** Vai trò (Role), **(2)** Kiến thức chuyên môn (Expertise), **(3)** Quy tắc hành vi (Rules), và **(4)** Format output mong muốn.

---

## 2. Cấu Trúc Thư Mục Chuẩn

Dưới đây là cấu trúc thư mục được thiết kế để **tương thích đa nền tảng** (Claude Code, Copilot, Cursor, Gemini):

```
my-project/
├── AGENTS.md                          # Hướng dẫn tổng thể (cross-tool standard)
├── CLAUDE.md -> AGENTS.md             # Symlink cho Claude Code
├── .github/
│   └── copilot-instructions.md        # Copy hoặc symlink cho Copilot
├── .cursor/
│   └── rules/
│       └── project.mdc                # Copy hoặc symlink cho Cursor
├── .gemini/
│   └── skills/                        # Skills cho Gemini/Claude
│       ├── 01-requirements.md
│       ├── 02-basic-design.md
│       ├── 03-detailed-design.md
│       ├── 04-implementation.md
│       ├── 05-testing.md
│       └── 06-review.md
├── docs/
│   └── specs/                         # Output của các Agent
│       ├── requirements.md
│       ├── basic-design.md
│       ├── detailed-design.md
│       └── test-report.md
└── logs/
    ├── temp_error.log                 # Log lỗi tạm (AI tự sửa)
    └── final_error.log                # Log lỗi cuối (cần người can thiệp)
```

!!! tip "Symlink để dùng chung 1 nguồn"
    Thay vì copy nội dung sang nhiều file, dùng symlink:
    ```bash
    ln -s AGENTS.md CLAUDE.md
    ln -s AGENTS.md .github/copilot-instructions.md
    ```
    Khi sửa `AGENTS.md`, tất cả công cụ đều nhận được cập nhật.

---

## 3. Xây Dựng Từng Agent Bằng Markdown

### Agent 1: Requirements Agent (PM)

Tạo file `.gemini/skills/01-requirements.md`:

```markdown
# Skill: Requirements Definition (要件定義)

## Khi nào kích hoạt
- Khi user yêu cầu "phân tích yêu cầu", "viết SRS", "requirements", hoặc 
  khi Orchestrator chỉ định Phase 1.

## Vai trò
Bạn là Business Analyst chuẩn IPA Nhật Bản. Nhiệm vụ: 
biến yêu cầu thô của khách hàng thành tài liệu Yêu cầu có cấu trúc.

## Quy trình
1. Đọc yêu cầu từ user hoặc từ file được chỉ định
2. Phân tích và liệt kê:
   - Functional Requirements (FR-001, FR-002...)
   - Non-Functional Requirements (NFR-001...)
   - Use Cases cho chức năng chính
   - Assumptions & Constraints
3. Lưu kết quả vào `docs/specs/requirements.md`

## Format output
Tài liệu phải theo format sau:
- Mỗi FR có ID, mô tả, priority (High/Medium/Low)
- Mỗi NFR có ID, metric đo lường cụ thể
- Mỗi Use Case có: Actor, Precondition, Main Flow, Alternative Flow

## Quy tắc
- KHÔNG được bịa thêm chức năng user không yêu cầu
- KHÔNG được bỏ qua yêu cầu phi chức năng
- Nếu yêu cầu mơ hồ, hãy HỎI user trước khi giả định
```

### Agent 2: Basic Design Agent (Architect)

Tạo file `.gemini/skills/02-basic-design.md`:

```markdown
# Skill: Basic Design (基本設計)

## Khi nào kích hoạt
- Khi user yêu cầu "thiết kế kiến trúc", "basic design",
  hoặc khi Orchestrator chỉ định Phase 2.

## Điều kiện tiên quyết
- File `docs/specs/requirements.md` phải tồn tại và đã được review PASS.

## Vai trò
Bạn là System Architect. Nhiệm vụ: thiết kế kiến trúc tổng thể
dựa trên tài liệu Yêu cầu.

## Quy trình
1. Đọc `docs/specs/requirements.md`
2. Thiết kế và viết ra:
   - Tech stack (với lý do chọn)
   - System architecture (layers, modules, components)
   - API endpoints (method, path, request/response schema)
   - Database schema (ERD dạng Mermaid hoặc text)
   - Sequence diagrams cho các flow chính
3. Lưu kết quả vào `docs/specs/basic-design.md`

## Quy tắc
- Mọi API endpoint phải map với ít nhất 1 FR trong requirements
- Database schema phải cover tất cả entities trong requirements
- PHẢI sử dụng Mermaid syntax cho diagrams
```

### Agent 3: Detailed Design Agent (SE)

Tạo file `.gemini/skills/03-detailed-design.md`:

```markdown
# Skill: Detailed Design (詳細設計)

## Khi nào kích hoạt
- Khi user yêu cầu "thiết kế chi tiết", "detailed design",
  hoặc khi Orchestrator chỉ định Phase 3.

## Điều kiện tiên quyết
- File `docs/specs/basic-design.md` phải tồn tại và đã được review PASS.

## Vai trò
Bạn là System Engineer. Nhiệm vụ: chi tiết hóa thiết kế cơ bản
đến mức class, function, và pseudocode.

## Quy trình
1. Đọc `docs/specs/basic-design.md`
2. Cho MỖI module/component, viết:
   - Class diagram (attributes, methods, visibility)
   - Function signatures: tên hàm, input types, output types
   - Pseudocode cho mỗi hàm có logic phức tạp
   - Error handling strategy cho mỗi hàm
3. Lưu kết quả vào `docs/specs/detailed-design.md`

## Quy tắc
- Mỗi class phải có docstring mô tả mục đích
- Mỗi hàm phải có: input types, output types, exceptions
- KHÔNG được viết "implement later" hoặc "TODO" — phải viết pseudocode cụ thể
```

### Agent 4: Programmer Agent

Tạo file `.gemini/skills/04-implementation.md`:

```markdown
# Skill: Implementation (製造)

## Khi nào kích hoạt
- Khi user yêu cầu "viết code", "implement", "coding",
  hoặc khi Orchestrator chỉ định Phase 4.

## Điều kiện tiên quyết
- File `docs/specs/detailed-design.md` phải tồn tại và đã được review PASS.

## Vai trò
Bạn là Senior Programmer. Nhiệm vụ: dịch thiết kế chi tiết thành 
source code hoàn chỉnh, chạy được.

## Quy trình
1. Đọc `docs/specs/detailed-design.md`
2. Tạo cấu trúc thư mục source code theo kiến trúc đã thiết kế
3. Implement từng class/function theo đúng signatures trong thiết kế
4. Viết docstrings cho mỗi class và function
5. Implement error handling theo strategy đã định nghĩa

## Quy tắc
- Code PHẢI tuân thủ 100% function signatures trong detailed design
- KHÔNG được thêm function hoặc class không có trong thiết kế
- KHÔNG được dùng placeholder ("pass", "# TODO", "...")
- Mỗi file phải có header comment với tên module và mục đích
```

### Agent 5: Tester Agent (QA)

Tạo file `.gemini/skills/05-testing.md`:

```markdown
# Skill: Testing (テスト)

## Khi nào kích hoạt
- Khi user yêu cầu "viết test", "testing", "QA",
  hoặc khi Orchestrator chỉ định Phase 5.

## Điều kiện tiên quyết
- Source code đã được implement và review PASS.
- File `docs/specs/requirements.md` tồn tại (để map test cases với FR).

## Vai trò
Bạn là QA Engineer. Nhiệm vụ: viết và chạy test cases để đảm bảo 
source code đáp ứng đúng yêu cầu.

## Quy trình
1. Đọc `docs/specs/requirements.md` (để biết test cái gì)
2. Đọc source code (để biết test ở đâu)
3. Viết test cases:
   - Mỗi FR phải có ít nhất 1 test case
   - Thêm edge cases: input rỗng, giá trị biên, duplicate
   - Thêm negative cases: input sai type, unauthorized access
4. Chạy tests và ghi kết quả
5. Lưu báo cáo vào `docs/specs/test-report.md`

## Format test report
| Test ID | Mô tả | FR liên quan | Kết quả | Ghi chú |
|---------|--------|-------------|---------|---------|
| TC-001  | ...    | FR-001      | PASS ✅ |         |
| TC-002  | ...    | FR-003      | FAIL ❌ | Expected: ... Actual: ... |
```

---

## 4. Xây Dựng Orchestrator & Workflow Bằng Text

### File AGENTS.md — Bộ não điều phối

Đây là file quan trọng nhất. Nó định nghĩa **toàn bộ quy trình** và là thứ đầu tiên AI đọc khi bắt đầu session:

```markdown
# AGENTS.md — Orchestrator Workflow

## Tổng quan
Dự án này sử dụng quy trình Waterfall chuẩn IPA Nhật Bản.
AI PHẢI tuân theo 5 giai đoạn theo đúng thứ tự. 
KHÔNG được nhảy cóc giai đoạn.

## Pipeline bắt buộc

### Phase 1: Requirements Definition (要件定義)
- Skill: `.gemini/skills/01-requirements.md`
- Input: Yêu cầu từ user
- Output: `docs/specs/requirements.md`
- **Sau khi hoàn thành → Chạy Review (xem mục Review bên dưới)**

### Phase 2: Basic Design (基本設計)
- Skill: `.gemini/skills/02-basic-design.md`
- Input: `docs/specs/requirements.md`
- Output: `docs/specs/basic-design.md`
- **Sau khi hoàn thành → Chạy Review**

### Phase 3: Detailed Design (詳細設計)
- Skill: `.gemini/skills/03-detailed-design.md`
- Input: `docs/specs/basic-design.md`
- Output: `docs/specs/detailed-design.md`
- **Sau khi hoàn thành → Chạy Review**

### Phase 4: Implementation (製造)
- Skill: `.gemini/skills/04-implementation.md`
- Input: `docs/specs/detailed-design.md`
- Output: Source code trong `src/`
- **Sau khi hoàn thành → Chạy Review**

### Phase 5: Testing (テスト)
- Skill: `.gemini/skills/05-testing.md`
- Input: Source code + `docs/specs/requirements.md`
- Output: `docs/specs/test-report.md`
- **Sau khi hoàn thành → Chạy Review**

## Quy trình Review & Self-Healing (BẮT BUỘC)

Sau MỖI phase, PHẢI chạy review theo skill `.gemini/skills/06-review.md`.

### Logic xử lý:
1. Nếu Review = PASS → Chuyển sang Phase tiếp theo
2. Nếu Review = FAIL:
   a. Ghi lỗi vào `logs/temp_error.log` (append)
   b. Đếm retry_count cho phase hiện tại
   c. Nếu retry_count < 3: Tự đọc lại lỗi và sửa output
   d. Nếu retry_count >= 3: Ghi vào `logs/final_error.log` 
      và DỪNG LẠI, thông báo user

## Quy tắc tổng thể
- KHÔNG BAO GIỜ bắt đầu Phase N+1 nếu Phase N chưa PASS review
- Mọi output phải được lưu vào file, không chỉ hiển thị trên chat
- Khi bắt đầu mỗi Phase, thông báo cho user: "Bắt đầu Phase X: ..."
- Khi kết thúc mỗi Phase, thông báo: "Phase X hoàn thành. Đang review..."
```

### File Review Agent — Người gác cổng

Tạo file `.gemini/skills/06-review.md`:

```markdown
# Skill: Review Agent (品質レビュー)

## Khi nào kích hoạt
- Tự động sau mỗi Phase trong pipeline.

## Vai trò
Bạn là Senior Reviewer chuẩn IPA. Nhiệm vụ: kiểm tra sản phẩm 
của Phase vừa hoàn thành, so sánh với tài liệu giai đoạn trước.

## Quy trình Review

### Bước 1: Xác định Phase đang review
- Phase 1 (Requirements): So sánh output với yêu cầu gốc của user
- Phase 2 (Basic Design): So sánh với `docs/specs/requirements.md`
- Phase 3 (Detailed Design): So sánh với `docs/specs/basic-design.md`
- Phase 4 (Implementation): So sánh với `docs/specs/detailed-design.md`
- Phase 5 (Testing): So sánh test results với `docs/specs/requirements.md`

### Bước 2: Checklist kiểm tra
- [ ] Output có đầy đủ tất cả items từ input không?
- [ ] Có mâu thuẫn logic nào không?
- [ ] Có placeholder/TODO chưa hoàn thành không?
- [ ] Format có đúng chuẩn không?
- [ ] Có item nào bị "bịa" thêm (không có trong input) không?

### Bước 3: Đưa ra kết quả
Trả về kết quả theo format:
```
REVIEW RESULT: [PASS/FAIL]
Phase: [Tên phase]
Retry: [Lần thứ mấy] / 3

Nếu FAIL:
- Lỗi 1: [Mô tả chi tiết]
- Lỗi 2: [Mô tả chi tiết]

Hành động tiếp theo: [Tự sửa / Báo user]
```

### Bước 4: Xử lý kết quả
- Nếu PASS: Thông báo "✅ Phase X PASSED. Chuyển sang Phase X+1"
- Nếu FAIL và retry < 3:
  1. Ghi lỗi vào `logs/temp_error.log`
  2. Thông báo "❌ Phase X FAILED (lần Y/3). Đang tự sửa..."
  3. Đọc lại lỗi và sửa output
  4. Chạy review lại
- Nếu FAIL và retry >= 3:
  1. Ghi toàn bộ lỗi vào `logs/final_error.log`
  2. Thông báo "🚨 Phase X FAILED sau 3 lần. Cần can thiệp."
  3. DỪNG pipeline
```

---

## 5. Cách Sử Dụng Trên Từng Nền Tảng

### Claude Code

```bash
# Bắt đầu dự án
claude

# Prompt khởi động pipeline
> Hãy đọc AGENTS.md và bắt đầu Phase 1: Requirements Definition.
> Yêu cầu dự án: "Xây REST API quản lý sách cho thư viện"
```

Claude sẽ tự động:

1. Đọc `AGENTS.md` → hiểu pipeline
2. Load skill `01-requirements.md` → đóng vai BA
3. Sinh `docs/specs/requirements.md`
4. Tự chạy review theo `06-review.md`
5. Nếu PASS → tự chuyển sang Phase 2 và load `02-basic-design.md`

### GitHub Copilot (Agent Mode)

1. Copy nội dung `AGENTS.md` vào `.github/copilot-instructions.md`
2. Mở VS Code, chọn **Agent Mode** trong Copilot Chat
3. Prompt tương tự:

```
Hãy bắt đầu Phase 1 theo quy trình trong copilot-instructions.md.
Yêu cầu dự án: "Xây REST API quản lý sách cho thư viện"
```

### Cursor

1. Tạo `.cursorrules` với nội dung tương tự `AGENTS.md`
2. Hoặc tạo từng file rule trong `.cursor/rules/`
3. Sử dụng Composer mode để chạy từng phase

---

## 6. So Sánh: Markdown-Based vs Code-Based MAS

| Tiêu chí | Markdown-Based (Bài này) | Code-Based (LangGraph/AutoGen) |
| :--- | :--- | :--- |
| **Setup** | 0 dependencies, chỉ cần tạo file `.md` | Cần Python, pip install, viết code |
| **Nền tảng** | Claude Code, Copilot, Cursor, Gemini | Chỉ chạy trên Python runtime |
| **Learning curve** | Thấp — ai biết viết Markdown đều dùng được | Cao — cần hiểu StateGraph, edges, nodes |
| **Deterministic** | Thấp — AI tự quyết định có tuân thủ không | Cao — code enforce luồng chạy |
| **Retry control** | Dựa vào prompt instruction | Dựa vào code logic (biến đếm, conditions) |
| **Customization** | Rất dễ — sửa file text | Cần sửa code, test lại |
| **Phù hợp cho** | Dự án cá nhân, team nhỏ, prototyping | Dự án enterprise, production pipeline |
| **Traceability** | Trung bình — phụ thuộc AI có ghi log không | Cao — state persistence, checkpointing |

!!! warning "Hạn chế quan trọng"
    Markdown-based agent **không đảm bảo 100%** AI sẽ tuân thủ. AI có thể "quên" đọc skill, bỏ qua review, hoặc nhảy cóc phase. Để giảm rủi ro:

    - Viết instruction **rõ ràng, ngắn gọn** — AI tuân thủ tốt hơn khi prompt dưới 500 từ
    - Dùng **từ khóa mạnh**: "BẮT BUỘC", "KHÔNG BAO GIỜ", "PHẢI"
    - Kiểm tra output sau mỗi phase — đừng tin tưởng 100%

---

## Kết luận

Bạn không cần là Python developer để xây dựng Multi-Agent System. Với những file Markdown được thiết kế cẩn thận, bạn có thể biến bất kỳ AI coding agent nào thành một **đội dự án ảo** có kỷ luật:

1. **`AGENTS.md`** — Orchestrator: định nghĩa pipeline và quy tắc tổng thể
2. **Skill files** — Specialized Agents: mỗi file một vai trò (PM, Architect, SE, Dev, QA)
3. **Review skill** — Quality Gate: cơ chế tự kiểm tra và self-healing
4. **Log files** — Audit trail: lưu vết lỗi và quá trình sửa chữa

Cách tiếp cận này đặc biệt phù hợp nếu bạn đang làm việc với Claude Code, GitHub Copilot, hoặc Cursor và muốn có **quy trình phát triển phần mềm có cấu trúc** mà không cần đầu tư vào code infrastructure phức tạp.

## Tham khảo

- [AGENTS.md Standard](https://github.com/anthropics/agents-md) — Chuẩn cross-tool cho AI agent instructions
- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code) — Hướng dẫn Skills và CLAUDE.md
- [GitHub Copilot Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) — Hướng dẫn copilot-instructions.md
- [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) — Framework prompt-based multi-agent cho phát triển phần mềm
- Bài viết liên quan: [Thực chiến MAS: Waterfall chuẩn IPA bằng Code](./2026-05-08-thuc-chien-multi-agent-system-waterfall-ipa.md)
