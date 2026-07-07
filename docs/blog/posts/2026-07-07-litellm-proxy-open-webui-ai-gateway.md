---
date: 2026-07-07
categories:
  - MLOps
tags:
  - litellm
  - open-webui
  - ai-gateway
  - langfuse
  - enterprise-ai
level: intermediate
status: published
description: "Hướng dẫn xây dựng AI Gateway thống nhất cho toàn tổ chức bằng LiteLLM Proxy + Open WebUI + Langfuse: cấu hình multi-model, rate limiting theo team, cost tracking, SSO và observability."
authors:
  - tranvanhoan
---

# LiteLLM Proxy & Open WebUI: Xây Dựng "Cổng Vào AI" Duy Nhất Cho Toàn Tổ Chức

## Mở Đầu: Khi Mỗi Phòng Ban Tự "Mở Cổng" Riêng

Hãy tưởng tượng: phòng R&D dùng Ollama chạy Llama 3 trên server GPU nội bộ, phòng Marketing kết nối thẳng OpenAI API bằng API key cá nhân, còn phòng Pháp chế thì thuê Azure OpenAI riêng vì lý do compliance. Ba phòng ban — ba "cổng vào AI" khác nhau — **không ai kiểm soát được ai đang dùng gì, tốn bao nhiêu, và dữ liệu nội bộ có bị gửi ra ngoài không**.

Đây là thực trạng phổ biến tại các doanh nghiệp bắt đầu triển khai AI nội bộ. Và nó nhanh chóng dẫn đến:

- 💸 **Chi phí "ma"** — Không ai biết tổng tiền API hàng tháng là bao nhiêu.
- 🔐 **Rủi ro bảo mật** — API key phân tán, dữ liệu nhạy cảm gửi qua cloud không kiểm soát.
- 📊 **Không có data để tối ưu** — Không biết model nào hiệu quả nhất, prompt nào tốn token nhất.

Giải pháp? Một **AI Gateway thống nhất** — nơi mọi request AI trong tổ chức đều đi qua một "cổng vào" duy nhất, được kiểm soát, theo dõi và tối ưu tập trung.

**Nội dung chính:**

- Tại sao cần AI Gateway thống nhất thay vì kết nối trực tiếp đến model.
- Cấu hình LiteLLM Proxy chi tiết: multi-model, fallback, rate limiting, cost tracking.
- Triển khai Open WebUI kết nối LiteLLM: workspace theo phòng ban, RAG nội bộ.
- Thiết lập SSO (OAuth2/OIDC) để nhân viên đăng nhập bằng tài khoản công ty.
- Monitoring toàn diện với Langfuse: trace request, token, latency.

---

## 1. Tại Sao Cần AI Gateway Thống Nhất?

### 1.1 Mô Hình "Kết Nối Trực Tiếp" — Nhanh Nhưng Nguy Hiểm

Khi một developer hoặc team kết nối trực tiếp đến LLM provider (OpenAI, Ollama, vLLM...), họ thường:

| Vấn đề | Hậu quả |
|--------|---------|
| Mỗi team quản lý API key riêng | API key rò rỉ = toàn bộ budget bị tiêu hết trong 1 đêm |
| Không có rate limiting tập trung | Một script chạy vòng lặp "nuốt" hết capacity GPU cho cả tổ chức |
| Không tracking chi phí | Cuối tháng bill Azure/OpenAI gấp 5x dự kiến, không biết ai gây ra |
| Không fallback | Ollama server sập → toàn bộ team dừng việc, không tự chuyển sang backup |
| Không audit log | Nhân viên gửi dữ liệu khách hàng vào ChatGPT, IT không hay biết |

### 1.2 Mô Hình AI Gateway — "Single Pane of Glass"

AI Gateway đóng vai trò **reverse proxy thông minh** đứng giữa người dùng và LLM backends:

```mermaid
graph LR
    subgraph "Người dùng"
        A["👩‍💼 Nhân viên<br/>(Open WebUI)"]
        B["🤖 Ứng dụng nội bộ<br/>(API Client)"]
        C["📱 Chatbot<br/>(Mobile App)"]
    end

    subgraph "AI Gateway"
        D["🚪 LiteLLM Proxy<br/>Authentication · Rate Limiting<br/>Cost Tracking · Routing"]
    end

    subgraph "LLM Backends"
        E["🦙 Ollama<br/>(GPU Server 1)"]
        F["⚡ vLLM<br/>(GPU Server 2)"]
        G["☁️ Azure OpenAI<br/>(Cloud Backup)"]
    end

    A --> D
    B --> D
    C --> D
    D --> E
    D --> F
    D --> G
```

!!! tip "Lợi ích của AI Gateway tập trung"
    - **Một API endpoint duy nhất** cho toàn bộ tổ chức: `https://ai-gateway.company.internal/v1`
    - **Virtual API key** per team — thu hồi ngay khi nhân viên nghỉ việc, không ảnh hưởng key gốc.
    - **Tự động failover**: Ollama sập → chuyển sang vLLM → cuối cùng fallback lên Azure.
    - **Cost tracking real-time**: biết chính xác phòng Marketing tốn bao nhiêu token tháng này.

---

## 2. LiteLLM Proxy: Trái Tim Của AI Gateway

[LiteLLM](https://github.com/BerriAI/litellm) là một open-source proxy viết bằng Python, cung cấp **OpenAI-compatible API** cho hơn 100 LLM providers. Phiên bản Proxy của nó biến một máy chủ thành AI Gateway hoàn chỉnh với authentication, rate limiting, cost tracking và routing.

### 2.1 Cấu Hình config.yaml Chi Tiết

Dưới đây là file `config.yaml` cho một tổ chức sử dụng **3 backend**: Ollama local (primary), vLLM local (secondary), và Azure OpenAI (cloud backup):

```yaml title="litellm/config.yaml" linenums="1"
# ============================================================
# LiteLLM Proxy Configuration — Enterprise AI Gateway
# ============================================================

# --- General Settings ---
general_settings:
  master_key: "sk-litellm-master-key-change-me"    # Admin key (thay đổi ngay!)
  database_url: "postgresql://litellm:litellm_pass@postgres:5432/litellm_db"
  alerting:
    - "slack"                                        # Alert khi budget vượt ngưỡng
  alert_types:
    - "budget_alerts"
    - "failed_tracking"

# --- Model Registry ---
model_list:
  # Primary: Ollama chạy trên GPU Server nội bộ
  - model_name: "llama-3.1-70b"
    litellm_params:
      model: "ollama/llama3.1:70b"
      api_base: "http://ollama-server:11434"
      rpm: 60                                        # Max 60 requests/phút
      tpm: 100000                                    # Max 100K tokens/phút
      timeout: 120                                   # Timeout 2 phút (model lớn)

  - model_name: "llama-3.1-8b"
    litellm_params:
      model: "ollama/llama3.1:8b"
      api_base: "http://ollama-server:11434"
      rpm: 200
      tpm: 500000
      timeout: 30

  # Secondary: vLLM chạy Mistral trên GPU Server 2
  - model_name: "mistral-nemo"
    litellm_params:
      model: "openai/mistralai/Mistral-Nemo-Instruct-2407"
      api_base: "http://vllm-server:8000/v1"
      rpm: 120
      tpm: 300000
      timeout: 60

  # Cloud Backup: Azure OpenAI (dùng khi local servers quá tải/sập)
  - model_name: "gpt-4o-backup"
    litellm_params:
      model: "azure/gpt-4o"
      api_base: "https://company-ai.openai.azure.com/"
      api_key: "os.environ/AZURE_API_KEY"
      api_version: "2024-08-01-preview"
      rpm: 30                                        # Giới hạn thấp (tiết kiệm chi phí)
      tpm: 50000

  # Embedding model cho RAG
  - model_name: "text-embedding"
    litellm_params:
      model: "ollama/nomic-embed-text"
      api_base: "http://ollama-server:11434"
      rpm: 300

# --- LiteLLM Core Settings ---
litellm_settings:
  # Tự động bỏ qua các parameter không được hỗ trợ bởi model local (ví dụ: logit_bias, frequency_penalty)
  drop_params: true

  # Fallback chain: local-first, cloud-last
  fallbacks:
    - "llama-3.1-70b": ["mistral-nemo", "gpt-4o-backup"]
    - "llama-3.1-8b": ["mistral-nemo"]
    - "mistral-nemo": ["gpt-4o-backup"]

  # Budget toàn proxy
  max_budget: 500.00                                 # $500/tháng cho cloud backup
  budget_duration: "30d"

  # Observability — Langfuse callback
  success_callback: ["langfuse"]
  failure_callback: ["langfuse"]

  # Cache (Redis) — giảm tải cho GPU server
  cache: true
  cache_params:
    type: "redis"
    host: "redis"
    port: 6379
    ttl: 3600                                        # Cache response 1 giờ

# --- Router Settings ---
router_settings:
  routing_strategy: "least-busy"                     # Ưu tiên server rảnh nhất
  enable_pre_call_checks: true                       # Kiểm tra health trước khi gửi
  allowed_fails: 3                                   # 3 lần fail → tạm loại khỏi pool
  cooldown_time: 60                                  # Cooldown 60s trước khi thử lại
  num_retries: 2                                     # Số lần retry trước khi fallback
  timeout: 120                                       # Timeout cho mỗi request (giây)

```

!!! warning "Bảo mật master_key"
    **KHÔNG BAO GIỜ** commit `master_key` vào Git. Sử dụng biến môi trường: `master_key: "os.environ/LITELLM_MASTER_KEY"`. Master key bị lộ = toàn bộ AI Gateway bị kiểm soát.

### 2.2 Rate Limiting Theo User/Team

LiteLLM hỗ trợ **rate limiting đa tầng** — từ global đến từng virtual key cá nhân:

```
┌─────────────────────────────────┐
│     Global Proxy Limit          │ ← Tổng capacity toàn hệ thống
│  ┌───────────────────────────┐  │
│  │    Team Limit             │  │ ← Budget & RPM theo phòng ban
│  │  ┌─────────────────────┐  │  │
│  │  │  Virtual Key Limit  │  │  │ ← Giới hạn từng cá nhân/app
│  │  └─────────────────────┘  │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### 2.3 Virtual API Key — "Chìa Khóa Ảo" Cho Mỗi Team

Sau khi proxy chạy, tạo team và virtual key thông qua API:

```bash
# Tạo team "Engineering" với budget $200/tháng, giới hạn 100 RPM
curl -X POST "http://localhost:4000/team/new" \
  -H "Authorization: Bearer sk-litellm-master-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "team_alias": "engineering",
    "max_budget": 200.00,
    "budget_duration": "30d",
    "rpm_limit": 100,
    "tpm_limit": 200000,
    "models": ["llama-3.1-70b", "llama-3.1-8b", "mistral-nemo"],
    "metadata": {"department": "Engineering", "cost_center": "ENG-001"}
  }'

# Tạo virtual key cho team Engineering
curl -X POST "http://localhost:4000/key/generate" \
  -H "Authorization: Bearer sk-litellm-master-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "<team_id_từ_response_trên>",
    "key_alias": "engineering-main-key",
    "max_budget": 50.00,
    "budget_duration": "30d",
    "metadata": {"owner": "tech-lead@company.com"}
  }'
```

!!! note "Thiết Lập Quota Theo Phòng Ban"
    **Chiến lược phân bổ quota khuyến nghị cho tổ chức 100–500 nhân viên:**

    | Phòng ban | Budget/tháng | RPM | TPM | Models được phép |
    |-----------|-------------|-----|-----|-----------------|
    | Engineering | $200 | 100 | 200K | Tất cả (bao gồm 70B) |
    | Data Science | $150 | 80 | 150K | Tất cả (bao gồm 70B) |
    | Marketing | $80 | 50 | 100K | 8B, Mistral |
    | HR | $30 | 20 | 50K | 8B only |
    | Legal/Compliance | $50 | 30 | 80K | Azure GPT-4o (data residency) |

    **Nguyên tắc:**

    - Phòng ban **tạo nội dung nhiều** (Marketing) → giới hạn TPM cao, RPM thấp (ít request nhưng dài).
    - Phòng ban **dùng cho coding** (Engineering) → RPM cao, TPM vừa (nhiều request ngắn).
    - Phòng ban **xử lý dữ liệu nhạy cảm** (Legal) → chỉ cho phép model trên Azure với data residency rõ ràng.
    - **Dự phòng 20%** budget proxy cho cloud backup — tránh bất ngờ khi local server bảo trì.

---

## 3. Open WebUI: Giao Diện Chat Cho Toàn Tổ Chức

[Open WebUI](https://github.com/open-webui/open-webui) là giao diện web mã nguồn mở, giao diện giống ChatGPT, hỗ trợ đa model, upload tài liệu RAG, và quản lý workspace — lý tưởng làm "mặt tiền" cho AI Gateway.

### 3.1 Kết Nối Open WebUI Với LiteLLM

Quy trình kết nối:

1. **Tạo Virtual Key** trên LiteLLM Admin UI (`http://litellm:4000/ui`) — key này sẽ được dùng bởi Open WebUI.
2. **Cấu hình trong Open WebUI**: vào **Admin Panel → Settings → Connections**, thêm connection:
    - **URL**: `http://litellm:4000` (dùng tên container Docker)
    - **API Key**: Virtual key vừa tạo
3. **Bật forward user info**: set `ENABLE_FORWARD_USER_INFO_HEADERS=true` trong biến môi trường của Open WebUI — cho phép LiteLLM biết ai đang gửi request để tracking per-user.

### 3.2 Workspace Theo Phòng Ban & RAG Nội Bộ

Open WebUI hỗ trợ tạo **Knowledge Bases** cho từng nhóm:

1. Vào **Workspace → Knowledge** → tạo Knowledge Base mới (ví dụ: "Nội quy công ty", "Product Specs Q3/2026").
2. Upload tài liệu: PDF, DOCX, Markdown, TXT — Open WebUI tự động chunk và embedding.
3. Trong chat, nhân viên dùng ký tự `#` để gọi Knowledge Base:

```
# product-specs Tính năng X hoạt động thế nào trong version 2.5?
```

!!! example "Ví dụ: Workspace cho phòng HR"
    - **Knowledge Base "Nội quy"**: Upload file nội quy, quy chế lương thưởng, handbook nhân viên.
    - **Knowledge Base "Tuyển dụng"**: Upload JD mẫu, quy trình phỏng vấn, rubric đánh giá.
    - Kết quả: nhân viên HR hỏi _"Chính sách nghỉ phép cho nhân viên thử việc?"_ → AI trả lời chính xác từ nội quy, kèm trích dẫn nguồn.

---

## 4. Docker Compose: Triển Khai Toàn Bộ Stack

Dưới đây là file Docker Compose triển khai **toàn bộ AI Gateway stack**: LiteLLM Proxy + Open WebUI + Langfuse + PostgreSQL + Redis.

```yaml title="docker-compose.yml" linenums="1"
version: "3.9"

services:
  # ============================================================
  # 1. PostgreSQL — Database chung cho LiteLLM + Langfuse
  # ============================================================
  postgres:
    image: postgres:16-alpine
    container_name: ai-gateway-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: "${POSTGRES_PASSWORD:-change_me_in_production}"
      POSTGRES_DB: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sh:/docker-entrypoint-initdb.d/init-db.sh
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ai-gateway

  # ============================================================
  # 2. Redis — Cache & Rate Limiting cho LiteLLM
  # ============================================================
  redis:
    image: redis:7-alpine
    container_name: ai-gateway-redis
    restart: unless-stopped
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ai-gateway

  # ============================================================
  # 3. LiteLLM Proxy — AI Gateway core
  # ============================================================
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: ai-gateway-litellm
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      # Database
      DATABASE_URL: "postgresql://litellm:litellm_pass@postgres:5432/litellm_db"
      # Master key
      LITELLM_MASTER_KEY: "${LITELLM_MASTER_KEY:-sk-litellm-master-change-me}"
      # Azure backup (nếu dùng)
      AZURE_API_KEY: "${AZURE_API_KEY:-}"
      # Langfuse callback
      LANGFUSE_PUBLIC_KEY: "${LANGFUSE_PUBLIC_KEY}"
      LANGFUSE_SECRET_KEY: "${LANGFUSE_SECRET_KEY}"
      LANGFUSE_HOST: "http://langfuse:3000"
      # Redis
      REDIS_HOST: "redis"
      REDIS_PORT: "6379"
    volumes:
      - ./litellm/config.yaml:/app/config.yaml
    ports:
      - "4000:4000"
    command: >
      --config /app/config.yaml
      --port 4000
      --detailed_debug
    networks:
      - ai-gateway

  # ============================================================
  # 4. Langfuse — Observability & Tracing
  # ============================================================
  langfuse:
    image: langfuse/langfuse:2
    container_name: ai-gateway-langfuse
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: "postgresql://langfuse:langfuse_pass@postgres:5432/langfuse_db"
      NEXTAUTH_URL: "http://localhost:3000"
      NEXTAUTH_SECRET: "${LANGFUSE_NEXTAUTH_SECRET:-change-me-nextauth-secret-32chars}"
      SALT: "${LANGFUSE_SALT:-change-me-salt-value-random}"
      ENCRYPTION_KEY: "${LANGFUSE_ENCRYPTION_KEY:-0000000000000000000000000000000000000000000000000000000000000000}"
      TELEMETRY_ENABLED: "false"
    ports:
      - "3000:3000"
    networks:
      - ai-gateway

  # ============================================================
  # 5. Open WebUI — Giao diện chat cho nhân viên
  # ============================================================
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: ai-gateway-webui
    restart: unless-stopped
    depends_on:
      - litellm
    environment:
      # Kết nối đến LiteLLM (không dùng Ollama trực tiếp)
      OPENAI_API_BASE_URL: "http://litellm:4000/v1"
      OPENAI_API_KEY: "${WEBUI_LITELLM_KEY:-sk-webui-virtual-key}"
      OLLAMA_BASE_URL: ""

      # Forward user info → LiteLLM (tracking per-user)
      ENABLE_FORWARD_USER_INFO_HEADERS: "true"

      # OAuth2/OIDC SSO
      ENABLE_OAUTH_SIGNUP: "true"
      OAUTH_CLIENT_ID: "${OAUTH_CLIENT_ID}"
      OAUTH_CLIENT_SECRET: "${OAUTH_CLIENT_SECRET}"
      OPENID_PROVIDER_URL: "${OPENID_PROVIDER_URL}"
      OAUTH_PROVIDER_NAME: "Company SSO"
      OAUTH_SCOPES: "openid email profile"
      OAUTH_MERGE_ACCOUNTS_BY_EMAIL: "true"
      ENABLE_OAUTH_ROLE_MANAGEMENT: "true"
      OAUTH_ADMIN_ROLES: "admin"
      OAUTH_ALLOWED_ROLES: "user,admin"
      # Không cho phép DB ghi đè các cấu hình OAuth từ environment (đặc biệt quan trọng từ v0.5+)
      ENABLE_OAUTH_PERSISTENT_CONFIG: "false"
      # URL của WebUI để sinh chính xác redirect URI trong OIDC flow
      WEBUI_URL: "${WEBUI_URL:-http://localhost:8080}"

      # WebUI settings
      WEBUI_AUTH: "true"
      WEBUI_NAME: "Company AI Assistant"
      DEFAULT_MODELS: "llama-3.1-8b"
      RAG_EMBEDDING_MODEL: "text-embedding"
    volumes:
      - webui_data:/app/backend/data
    ports:
      - "8080:8080"
    networks:
      - ai-gateway

# ============================================================
# Volumes & Networks
# ============================================================
volumes:
  postgres_data:
  redis_data:
  webui_data:

networks:
  ai-gateway:
    driver: bridge
```

Script khởi tạo database cho cả LiteLLM và Langfuse:

```bash title="init-db.sh"
#!/bin/bash
set -e

# Tạo database và user cho LiteLLM
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER litellm WITH PASSWORD 'litellm_pass';
    CREATE DATABASE litellm_db OWNER litellm;
    GRANT ALL PRIVILEGES ON DATABASE litellm_db TO litellm;

    CREATE USER langfuse WITH PASSWORD 'langfuse_pass';
    CREATE DATABASE langfuse_db OWNER langfuse;
    GRANT ALL PRIVILEGES ON DATABASE langfuse_db TO langfuse;
EOSQL

echo "✅ Databases created: litellm_db, langfuse_db"
```

File `.env` mẫu:

```bash title=".env"
# === LiteLLM ===
LITELLM_MASTER_KEY=sk-litellm-prod-CHANGE-THIS-TO-RANDOM-STRING
AZURE_API_KEY=your-azure-api-key-here

# === Langfuse ===
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
LANGFUSE_NEXTAUTH_SECRET=your-random-32-char-secret-here
LANGFUSE_SALT=your-random-salt-value-here
LANGFUSE_ENCRYPTION_KEY=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef

# === Open WebUI ===
WEBUI_LITELLM_KEY=sk-webui-key-generated-from-litellm

# === OAuth2/OIDC (ví dụ: Keycloak) ===
OAUTH_CLIENT_ID=open-webui
OAUTH_CLIENT_SECRET=your-oauth-client-secret
OPENID_PROVIDER_URL=https://auth.company.com/realms/company/.well-known/openid-configuration

# === PostgreSQL ===
POSTGRES_PASSWORD=super-secure-postgres-password
```

---

## 5. Luồng Request: Từ Nhân Viên Đến Model Và Ngược Lại

### 5.1 Sequence Diagram Chi Tiết

```mermaid
sequenceDiagram
    actor NV as 👩‍💼 Nhân viên
    participant WebUI as Open WebUI
    participant LLM as LiteLLM Proxy
    participant Auth as Auth Check
    participant Router as Smart Router
    participant Ollama as 🦙 Ollama Server
    participant LF as 📊 Langfuse

    NV->>WebUI: Gửi câu hỏi qua chat UI
    WebUI->>WebUI: Kiểm tra session (OAuth2 token)
    WebUI->>LLM: POST /v1/chat/completions<br/>+ Virtual API Key<br/>+ User Info Headers

    LLM->>Auth: Validate Virtual Key
    Auth-->>LLM: ✅ Key hợp lệ, Team: Engineering<br/>Budget còn: $180/200

    LLM->>Auth: Check Rate Limit
    Auth-->>LLM: ✅ RPM: 45/100, TPM: 80K/200K

    LLM->>Router: Route request đến model phù hợp
    Router->>Router: Chiến lược: least-busy<br/>Ollama: 3 pending, vLLM: 7 pending
    Router-->>LLM: Chọn: Ollama (ít tải nhất)

    LLM->>Ollama: Forward request → llama3.1:70b
    Ollama-->>LLM: Stream response tokens

    LLM->>LF: Async log: user, model, tokens,<br/>latency, cost
    LLM-->>WebUI: Stream response về
    WebUI-->>NV: Hiển thị câu trả lời real-time

    Note over LF: Langfuse ghi nhận:<br/>- User: alice@company.com<br/>- Team: Engineering<br/>- Model: llama-3.1-70b<br/>- Tokens: 1,247 (in: 156, out: 1,091)<br/>- Latency: 3.2s<br/>- Cost: $0.00 (local model)
```

### 5.2 Xử Lý Khi Ollama Gặp Sự Cố

```mermaid
sequenceDiagram
    actor NV as 👩‍💼 Nhân viên
    participant LLM as LiteLLM Proxy
    participant Ollama as 🦙 Ollama (Primary)
    participant vLLM as ⚡ vLLM (Secondary)
    participant Azure as ☁️ Azure OpenAI (Backup)

    NV->>LLM: "Tóm tắt báo cáo Q3 này"

    LLM->>Ollama: Request → llama3.1:70b
    Ollama--xLLM: ❌ Connection refused (GPU OOM)

    LLM->>LLM: Retry 1/2...
    LLM->>Ollama: Retry request
    Ollama--xLLM: ❌ Vẫn lỗi

    Note over LLM: Fallback trigger!<br/>llama-3.1-70b → mistral-nemo

    LLM->>vLLM: Request → Mistral-Nemo
    vLLM-->>LLM: ✅ Response thành công

    LLM-->>NV: Trả response (nhân viên không biết có failover)
    Note over LLM: Log: model_used=mistral-nemo<br/>fallback_from=llama-3.1-70b
```

!!! info "Failover trong suốt"
    Nhân viên **không cần biết** hệ thống đã failover. LiteLLM tự động xử lý và ghi log để admin theo dõi. Response headers chứa `x-litellm-model-id` cho phép debug khi cần.

---

## 6. Cấu Hình SSO (OAuth2/OIDC) Cơ Bản

### 6.1 Kiến Trúc SSO

Để nhân viên đăng nhập bằng tài khoản công ty, chúng ta cần một **Identity Provider (IdP)** hỗ trợ OAuth2/OIDC. Các lựa chọn phổ biến:

| IdP | Open-source? | Phù hợp cho |
|-----|-------------|-------------|
| **Keycloak** | ✅ Có | Doanh nghiệp tự host, full control |
| **Authentik** | ✅ Có | Startup, dễ setup hơn Keycloak |
| **Azure AD / Entra ID** | ❌ Không | Tổ chức đã dùng Microsoft 365 |
| **Google Workspace** | ❌ Không | Tổ chức đã dùng Google Suite |

### 6.2 Thiết Lập Với Keycloak (Ví Dụ)

**Bước 1: Tạo Client trên Keycloak**

1. Đăng nhập Keycloak Admin Console → chọn Realm **company**.
2. Clients → Create Client:
    - **Client ID**: `open-webui`
    - **Client Protocol**: `openid-connect`
    - **Root URL**: `https://ai.company.com`
3. Settings:
    - **Valid Redirect URIs**: `https://ai.company.com/oauth/oidc/callback`
    - **Access Type**: `confidential`
    - **Client Authentication**: ON
4. Copy **Client Secret** từ tab Credentials.

**Bước 2: Cập nhật biến môi trường Open WebUI**

Các biến đã được khai báo trong Docker Compose ở mục 4. Giá trị cần cấu hình thêm trong `.env` để SSO hoạt động chính xác:

```bash
OAUTH_CLIENT_ID=open-webui
OAUTH_CLIENT_SECRET=<client-secret-từ-keycloak>
OPENID_PROVIDER_URL=https://auth.company.com/realms/company/.well-known/openid-configuration
# Cần thiết để đảm bảo redirect URI khớp với cấu hình Keycloak
WEBUI_URL=https://ai.company.com
# Tránh trường hợp WebUI ghi đè config trong database ở Runtime
ENABLE_OAUTH_PERSISTENT_CONFIG=false
```


**Bước 3: Phân quyền qua role**

Trong Keycloak, tạo **Client Role** `admin` cho Open WebUI client, và gán role này cho các user thuộc nhóm IT Admin. Nhân viên thường sẽ tự động nhận role `user`.

!!! warning "Bảo mật OIDC"
    - **Luôn dùng HTTPS** cho cả Open WebUI và Keycloak — OAuth2 yêu cầu TLS cho redirect URI.
    - **Tắt form login** sau khi SSO hoạt động ổn định: `ENABLE_LOGIN_FORM=false` — tránh bypass SSO.
    - Đảm bảo **Redirect URI khớp chính xác** — sai 1 ký tự sẽ gây lỗi silent failure.

---

## 7. Monitoring Với Langfuse: Trace Mọi Request

### 7.1 Tại Sao Cần Observability Cho AI?

Khác với API truyền thống, LLM request có đặc thù riêng cần monitoring chuyên biệt:

- **Chi phí biến động**: mỗi request tốn lượng token khác nhau → cần tracking token-level.
- **Latency không đều**: model 70B mất 5–10s, model 8B mất 0.5–1s → cần phân tích theo model.
- **Chất lượng output**: cùng prompt, khác model → khác kết quả → cần so sánh.

### 7.2 Langfuse Integration Qua LiteLLM

Langfuse được kích hoạt qua callback trong `config.yaml`:

```yaml
litellm_settings:
  success_callback: ["langfuse"]
  failure_callback: ["langfuse"]
```

Kết hợp với biến môi trường trong Docker Compose:

```yaml
environment:
  LANGFUSE_PUBLIC_KEY: "${LANGFUSE_PUBLIC_KEY}"
  LANGFUSE_SECRET_KEY: "${LANGFUSE_SECRET_KEY}"
  LANGFUSE_HOST: "http://langfuse:3000"
```

### 7.3 Dashboard Langfuse — Những Gì Bạn Theo Dõi Được

Sau khi thiết lập, Langfuse Dashboard tại `http://localhost:3000` cung cấp:

| Metric | Mô tả | Ví dụ |
|--------|--------|-------|
| **Traces** | Mỗi request = 1 trace với đầy đủ input/output | `alice@company.com` hỏi "Tóm tắt báo cáo..." |
| **Token Usage** | Input tokens + Output tokens per request | In: 156 tokens, Out: 1,091 tokens |
| **Latency** | Thời gian phản hồi end-to-end | P50: 2.1s, P95: 8.3s, P99: 15.2s |
| **Cost** | Chi phí ước tính theo bảng giá model | $0.00 (local) / $0.03 (Azure) |
| **Model Distribution** | % request theo từng model | Ollama: 72%, vLLM: 23%, Azure: 5% |
| **User Analytics** | Ai dùng nhiều nhất, team nào tốn nhất | Engineering: 45K tokens/ngày |
| **Error Rate** | Tỷ lệ request lỗi theo model/team | Ollama timeout: 2.3% |

!!! tip "Tạo Custom Dashboard"
    Langfuse cho phép tạo dashboard tùy chỉnh. Gợi ý dashboard cho CTO:

    1. **Cost Overview**: Tổng chi phí theo ngày/tuần/tháng, breakdown theo team.
    2. **Model Performance**: Latency P50/P95 theo model — để quyết định nâng cấp GPU hay chuyển model.
    3. **Usage Heatmap**: Giờ cao điểm sử dụng AI — để lên lịch bảo trì server.
    4. **Error Trends**: Xu hướng lỗi — phát hiện sớm GPU degradation.

---

## 8. Prompt Mẫu: Test Kết Nối & Đo Latency

Sau khi triển khai xong toàn bộ stack, sử dụng các lệnh sau để kiểm tra:

### 8.1 Test Kết Nối Cơ Bản

```bash
# Test LiteLLM Proxy health
curl -s http://localhost:4000/health | python3 -m json.tool

# List tất cả models đã đăng ký
curl -s http://localhost:4000/v1/models \
  -H "Authorization: Bearer sk-litellm-master-key-change-me" | python3 -m json.tool

# Test chat completion đơn giản
curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-litellm-master-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b",
    "messages": [{"role": "user", "content": "Xin chào! Bạn là AI model nào?"}],
    "max_tokens": 100
  }' | python3 -m json.tool
```

### 8.2 Đo Latency & Throughput

```bash
# Script đo latency cho từng model
for MODEL in "llama-3.1-8b" "llama-3.1-70b" "mistral-nemo"; do
  echo "=== Testing: $MODEL ==="
  START=$(python3 -c "import time; print(time.time())")

  RESPONSE=$(curl -s -w "\n%{time_total}" \
    http://localhost:4000/v1/chat/completions \
    -H "Authorization: Bearer sk-litellm-master-key-change-me" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"$MODEL\",
      \"messages\": [{\"role\": \"user\", \"content\": \"Giải thích ngắn gọn Docker là gì trong 3 câu.\"}],
      \"max_tokens\": 200
    }")

  LATENCY=$(echo "$RESPONSE" | tail -1)
  echo "Latency: ${LATENCY}s"
  echo "---"
done
```

### 8.3 Test Fallback Chain

```bash
# Giả lập Ollama sập — xem LiteLLM có tự chuyển sang backup không
# (Dừng Ollama container trước khi test)
# docker stop ollama-server

curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-litellm-master-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-70b",
    "messages": [{"role": "user", "content": "Nếu bạn nhận được message này, fallback đang hoạt động!"}],
    "max_tokens": 50
  }' | python3 -m json.tool

# Kiểm tra response header để xác nhận model thực sự được dùng
curl -s -D - http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-litellm-master-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-70b",
    "messages": [{"role": "user", "content": "Test fallback"}],
    "max_tokens": 10
  }' 2>&1 | grep -i "x-litellm"
```

!!! example "Kết quả mong đợi khi Ollama đã dừng"
    ```
    x-litellm-model-id: mistral-nemo
    x-litellm-model-fallback: true
    ```
    Response vẫn trả về bình thường — nhân viên không bị gián đoạn.

---

## Kết Luận

Xây dựng AI Gateway thống nhất bằng **LiteLLM Proxy + Open WebUI + Langfuse** không chỉ là vấn đề kỹ thuật — nó là **chiến lược quản trị AI** cho toàn tổ chức. Ba điều cốt lõi cần nhớ:

1. **Một cổng vào duy nhất** — Mọi request AI đều đi qua LiteLLM Proxy. Không ngoại lệ. Điều này cho phép kiểm soát chi phí, bảo mật và chất lượng từ một điểm duy nhất.
2. **Phân quyền theo phòng ban** — Virtual key + team budget + rate limiting đảm bảo mỗi team dùng đúng quota, không ảnh hưởng lẫn nhau, và dữ liệu nhạy cảm chỉ đi qua model được phê duyệt.
3. **Observability là bắt buộc** — Không có Langfuse (hoặc công cụ tương đương), bạn đang "bay mù". Trace từng request, đo latency, tracking cost — đó là cơ sở để tối ưu và báo cáo ROI cho ban lãnh đạo.

Bước tiếp theo trong series: triển khai **RAG Pipeline** chuyên sâu — xây dựng hệ thống tìm kiếm tài liệu nội bộ thông minh, kết hợp vector database và reranking model.

---

## Tham Khảo

- [LiteLLM Documentation — Proxy Server](https://docs.litellm.ai/) — Tài liệu chính thức về cấu hình LiteLLM Proxy, virtual keys, và routing.
- [Open WebUI Documentation](https://docs.openwebui.com/) — Hướng dẫn triển khai, cấu hình SSO/OIDC và RAG cho Open WebUI.
- [Langfuse — Self-Hosting Guide](https://langfuse.com/docs/deployment/self-host) — Tài liệu triển khai Langfuse bằng Docker Compose và tích hợp với LiteLLM.
- [Langfuse — LiteLLM Integration](https://langfuse.com/docs/integrations/litellm) — Hướng dẫn chi tiết callback Langfuse trong LiteLLM Proxy.
- [Keycloak — OpenID Connect](https://www.keycloak.org/docs/latest/securing_apps/) — Tài liệu cấu hình OIDC client cho ứng dụng web.
