---
name: refactor-agent-skills-to-hierarchical-routing
description: |
  將扁平化 AI Agent Skills 重構為「階層式 Toolkit Routers + 全域 Root Router」的企業級合約：
  - 全域路由（Root Router）：跨 Domain 的意圖分流、跨 Toolkit pipeline 編排與狀態傳遞
  - 型別校驗（JSON Schema 子集，可機器驗證）
  - DAG 依賴/循環防護（含互動式解循環合約 + 無人值守 fallback）
  - 並行調度（同時治理資料依賴 + 副作用/資源互斥）
  - 安全遮蔽（宣告式 + Host Environment 外部攔截器執行）
  - 覆蓋率守恆（允許 merge/split 但不得遺漏；可驗證）
  - 冪等性/重試/補償（防止重試造成副作用災難）
  - 可觀測性（trace_id/span_id 強制繼承）
  產出 Step0-5 全 YAML 合約與可驗證 Lint。
schema_version: "2.2"
---

# 技能：重構為階層式路由 (Refactor to Hierarchical Router)

## 0) 目標 (MUST)

### 0.1 Toolkit 目標
- **高內聚優先 (Cohesion over Fragmentation)**：如果一組高度相關的技能（例如具有相同前綴或領域目的）總數在 30 個以內，應將其打包為單一 Toolkit。請勿為了硬湊數量而將其強行拆散。
- 只有當整體技能庫跨度過大或總數過多時，才切分為 2–5 個 `<domain>-toolkit`。
- 每 toolkit 子技能 ≤30；`misc-toolkit` ≤20。
- 每個 `<domain>-toolkit` 必須包含一個 `SKILL.md` 檔案，作為該領域的路由進入點 (Routing Entry Point)。這個 YAML 內的 `description` 欄位至關重要，必須精準說明其包含之所有子技能的目的，以確保 Agent 能夠基於對話正確路由至該領域。此外，其 Markdown 本文必須包含 `sub_skills` 子技能註冊表，以便 Agent 確切知道如何路由。

### 0.2 輸出格式與可驗證性
- Step0–5 輸出皆為 **單一可解析 YAML**
- markdown 只能以 YAML block scalar 內嵌（`|` 或 `>`）
- 必須滿足 `yaml.safe_load` 可解析（Step5 必須驗證）

### 0.3 正確性與安全性
- 覆蓋率守恆：不得遺漏任何輸入技能（允許 merge/split 但必須顯式宣告）
- 並行安全：並行需同時滿足「資料無依賴」+「副作用/資源互斥無衝突」
- 安全遮蔽：logs/handoff/final_outputs 必須遮蔽敏感值
- 循環防護：若 cycle，必須輸出 `cycle_resolution` 合約；且提供 **無人值守 fallback**
- 冪等與重試：任何可能產生副作用的技能必須宣告 `idempotent`；非冪等不得重試，除非提供補償

---

## 1) 硬性規則 (MUST)

### 1.1 檔案命名與 Bundle 保留原則 (MUST)
- Toolkit 根目錄 (`<domain>-toolkit/`) 下的 Router 檔案名稱 MUST 固定為 `SKILL.md`，絕對不可命名為 `<domain>-toolkit.md`。
- 不需要額外建立 `sub_skills/` 階層。子技能應直接以子資料夾形式放進 toolkit 目錄內（例如 `<domain>-toolkit/old_folder_name/`）。
- **載入器防護機制（僅限子技能）**：**子技能**資料夾內的主檔案絕對「禁止」命名為 `SKILL.md` 或是其他保留名（如 `ROUTER.md`）。這是為了防止 Host 環境使用遞迴掃描 `glob("**/*.md")` 時，將子技能誤認為是 Router。請以目錄名稱作為主檔案名（例如 `my_skill/SKILL.md` 改名為 `my_skill/my_skill.md`）。
- **Bundle 完整性**：若原始技能是以資料夾形式存在，必須將整個資料夾（含所有設定檔、提示詞、腳本）原封不動搬遷。

### 1.2 檔案編碼與產物清理 (MUST)
- **UTF-8 編碼**：Agent 在讀取與寫入檔案時，MUST 確保保留原有編碼。所有的檔案修改與寫入 MUST 明確使用 UTF-8 (無 BOM) 編碼，以防止非 ASCII 字元（如中文）變成亂碼。
- **清理過渡產物**：在重構與搬遷完成後，Agent MUST 負責刪除過程中的臨時產物（例如：殘留在 toolkit 目錄的 `step0-5-contracts.yaml`，以及殘留在 `skills` 目錄的 `refactor_*.ps1` 等腳本）。

### 1.3 共用資源與相對路徑重寫 (MUST)
- 在 Step 0 (Cleansing) 時，Agent MUST 靜態分析技能內容，找出任何參考外部或共用資料夾的相對路徑（例如 `../shared_utils/`）。
- 若存在共用資料夾，必須將其搬遷至 toolkit 內（若屬單一 toolkit）或保留於全域（若跨 toolkit），**但 MUST 保留其原始的資料夾名稱**（例如：原本叫 `shared_utils` 就必須維持 `shared_utils`，不可隨意改名為 `shared`）。
- Agent 搬遷時 MUST 自動修正 `.md` 或腳本內相對應的路徑參考，確認相對路徑的表示正確，確保引用不會斷裂。

### 1.4 Cleansing（最小可用）
每個 skill 最少要有：
- `name`
- `description`（必含：動作 + 物件 + 產出）
- `required_inputs[]`、`outputs[]`（缺就補，並標 `confidence: low`）
- 若涉及副作用：必須補 `side_effects[]`、`resources_touched[]`、`mutex_group`（可先低信心推測）

### 1.5 YAML 可解析（YAML-safe profile）
- 多行字串：必用 block scalar `|` 或 `>`
- 單行字串：必要時加引號（避免 YAML 歧義）
- **Router markdown 嚴禁 fenced code blocks（```）**  
  - 若需呈現程式碼/合約片段：使用「四空白縮排碼塊」  
  - 原因：LLM 常在 ``` 與縮排互動下產生不可解析 YAML
- **Frontmatter 閉合要求 (MUST)**：若產出帶有 YAML frontmatter 的 Markdown（如 `toolkit_router_skill_md`），該 YAML 區塊必須在頭部與**尾部**都嚴格加上 `---` 進行閉合，之後才可接續 Markdown 本文。
- Step5 必須驗證：所有 step 產物可被 `yaml.safe_load` 解析

### 1.6 DAG + 並行安全（資料依賴 + 副作用互斥）
- DAG 邊來源（任何一種都算依賴）：
  - `depends_on`
  - `input_bindings(from_skill)`
  - 互斥序列化：`mutex_group` 衝突 或 `resources_touched` 有交集
- 並行允許條件：同一並行層內所有技能必須同時滿足：
  - 無 DAG 邊互相指向
  - `mutex_group` 不衝突
  - `resources_touched` 無交集（以 glob/prefix 規則比對）

### 1.7 Security（宣告式 + Host Delegation）
- 遮蔽作用範圍：`logs`, `handoff`, `final_outputs`
- 遮蔽偵測（宣告式規則）：
  - key-name contains（不分大小寫）：token/secret/password/apikey/authorization/cookie/session/key
  - value-pattern（regex）：JWT / PEM 私鑰 / AWS key / 常見 tokens（可擴充）
- 遮蔽輸出：一律 `***MASKED***`
- **允許（且建議）將實際遮蔽委派給 Host Environment 外部攔截器**：
  - Skill/Router 只需宣告 `requires_redaction: true` 與 `sensitive_outputs`
  - 實際 regex 掃描/替換由 Host 執行（效能/準確性/一致性更可靠）
- 任務失敗必須輸出：
  - `failure_report`
  - `manual_cleanup_recommendations`

### 1.8 子技能註冊表還原度 (Sub-skill Registry Fidelity) (MUST)
- **100% 完整複製 (Exact Match)**：在生成 Router (如 `SKILL.md`) 內的 `sub_skills` 註冊表時，必須完全照抄子技能原始 YAML 中的 `description` 內容，不可遺漏任何字元。
- **禁止重新摘要或翻譯 (No Summarization / Translation)**：嚴禁使用 AI 模型重新歸納、縮減字數或自行翻譯。原始語言是中文就保留中文，是英文就保留英文。
- **安全處理多行文字 (Safe YAML Block Scalar)**：若原始 `description` 包含多行文字，必須在 Router 的 YAML 陣列中使用安全的區塊標量符號（如 `|` 或 `>`），以確保換行符號不破壞整份文件的 YAML 結構。

### 1.9 Toolkit Router 描述生成 (語意最佳化, MUST)
在產出 Router 的 `description`（如 Step 3 / Step 5）時，你必須扮演 Master Router Architect 的角色，將 LLM 意圖路由的「語意命中率 (Semantic Hit Rate)」最大化，避免產生「語意覆蓋不足」與「致命的結構空白」。
1. **萃取 (Extract)**: 讀取所有子技能的 descriptions。列出所有獨特的動作動詞（例如：撰寫、分流、審查）以及目標實體（例如：SPEC、CI、PR、Approval）。
2. **分群 (Cluster)**: 將這些詞彙分組為 3 到 5 個具備邏輯關聯的能力領域 (Capability Domains)。
3. **起草 (Draft)**: 依照以下確切的結構撰寫主 `description`：
   - **主要定位 (Primary Identity)**: 用 1~2 句話說明整體的框架與主要目的。
   - **核心領域/階段 (Core Phases/Domains)**: 條列出前一步分群的 3~5 個領域，必須明確包含萃取出的關鍵字。
   - **觸發時機 ("Use When" Triggers)**: 使用無序列單列出 3~4 個明確的使用者意圖，說明「當使用者提出這些需求時，必須路由至此 Toolkit」。
4. **稽核 (Audit)**: 確認 **每一個子技能** 至少有一個語意錨點（相關關鍵字或概念）出現在最終的 Router description 內。例如：若某個子技能負責「舊代碼萃取」，但你的 Router 描述卻只提到「新功能交付」，則必須重寫描述以明確包含該特定處理需求。

---

## 2) 型別系統（可機器驗證）(MUST)

### 2.1 JSON Schema 子集
I/O 使用 `schema`（推薦），或最少 `schema.type`（enum）：
- `string|integer|number|boolean|null|object|array`
- object 可用：`properties|required|additionalProperties`
- array 必用：`items`

### 2.2 Trace Context（可觀測性必備）
所有技能 I/O **必須支援 trace context 繼承**：
- 每個 skill 的 `required_inputs` 應包含（至少 optional）`trace_context`
- 每個 skill 的 `outputs` 應輸出（至少 optional）`trace_context`

建議 schema（可直接引用）：
~~~yaml
TraceContext:
  type: "object"
  additionalProperties: false
  properties:
    trace_id: {type: "string", minLength: 8}
    span_id:  {type: "string", minLength: 8}
    parent_span_id: {type: "string"}
  required: ["trace_id","span_id"]
````

### 2.3 input_bindings（顯式綁定）

若輸入名不符，必須：

```yaml
input_bindings:
  - target_input: "aws_config"
    from_skill: "fetch_profile"
    from_output: "profile_config"
```

---

## 3) 全域狀態與跨 Toolkit（MUST）

### 3.1 Global Context（跨 Domain State Contract）

若 pipeline 跨 toolkit，必須用 `global_context` 明確傳遞：

* `context_writes[]`: skill 將哪些 key 寫入 global_context（型別宣告）
* `context_reads[]`: skill 依賴哪些 key（型別宣告）
* Router 必須治理：缺 key → 問 1 題；或在 batch 模式下 fail-fast

建議 key 命名：

* `infra.machine.ip`
* `deploy.release.id`
* `secrets.vault.ref`（僅允許 ref，不得直接放明文 secret）

### 3.2 Artifact Registry（覆蓋率與可追溯）

編排管線的 Router 應維護 artifact registry（宣告式）：

* 任何重要輸出（報告、變更單、部署摘要）應有 `artifact_id`
* 便於稽核、重跑、對帳（coverage 也更易驗證）

---

## 4) Step 0–5 輸出合約（全部 MUST 是 YAML）

> 禁止用自由文本取代；必要說明只能放 `notes: |`

### Step 0：Cleansing

```yaml
step: "0"
schema_version: "2.2"
warnings: []
auto_fixes: []
input_inventory:
  total_input_skills: 0
  input_skills:
    - old_path: "skills/x.md"
      detected_name: "..."
      detected_description: "..."
      io_inferred: true
      reserved_name_conflict: false
      confidence: "low"  # low|medium|high
```

### Step 1：Domain Grouping

```yaml
step: "1"
schema_version: "2.2"
target_toolkits_range: "2-5"
actual_toolkits_count: 0
toolkits:
  - toolkit: "devops-toolkit"
    verbs: ["deploy","monitor"]
    objects: ["service","infra"]
    skills: [{old_path: "skills/x.md"}]
constraints:
  per_toolkit_skill_limit: 30
  misc_skill_limit: 20
```

### Step 2：Migration Mapping + 覆蓋率守恆

```yaml
step: "2"
schema_version: "2.2"
migration_mapping:
  - old_path: "skills/x.md"
    new_path: "devops-toolkit/rollout_service/rollout_service.md"
    new_skill_id: "rollout_service"
    rename_reason: ""
    coverage:
      supersedes: ["skills/x.md"]  # merge：可多個
      split_into: []               # split：列新 skill_id
coverage_report:
  total_input_skills: 0
  total_mapped_input_skills: 0
  uncovered_inputs: []
  coverage_ratio: 1.0
```

### Step 3：生成 Toolkit Routers（YAML-safe）

**Token 截斷防護（toolkits > 3）**

* toolkit：只完整輸出第 1 個 toolkit（index + router_md），其餘輸出 draft + `pending_generation[]`

````yaml
step: "3"
schema_version: "2.2"

global_routing_spec:
  routing_mode: "deterministic_then_semantic"
  semantic_confidence_threshold: 0.72
  tie_breaker:
    mode: "ask_one_question_then_fallback"
    fallback_strategy:
      on_no_user_response: "fail_fast"   # fail_fast | break_lowest_confidence_edge
      default_max_wait_ms: 30000
  global_context:
    enabled: true
    mode: "explicit_reads_writes"
  security:
    redaction_mode: "external_interceptor_preferred"   # inline_allowed | external_interceptor_preferred | external_only
    mask_value: "***MASKED***"

toolkits_generated:
  - toolkit: "devops-toolkit"
    toolkit_index_yaml: |
      schema_version: "2.2"
      toolkit: "devops-toolkit"
      routing_mode: "deterministic_then_semantic"
      security:
        requires_redaction: true
        redaction_mode: "external_interceptor_preferred"
        mask_value: "***MASKED***"
        redaction_rules_declared:
          key_name_contains: ["token","secret","password","apikey","authorization","cookie","session","key"]
          value_patterns:
            - {name: "jwt", regex: "eyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"}
            - {name: "pem_private_key", regex: "-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"}
            - {name: "aws_access_key_id", regex: "AKIA[0-9A-Z]{16}"}
      execution_defaults: {timeout_ms: 600000, max_retries: 2}
      observability:
        require_trace_context: true
      sub_skills:
        - id: "rollout_service"
          name: "服務滾動部署"
          description: |
            執行滾動部署指定服務，產出部署結果與摘要。
          when: >
            使用者要求部署/上線/滾動更新，且提供服務與環境。
          execution_policy:
            idempotent: false
            max_retries_override: 0
            requires_idempotency_key: true
            compensating_action_path: "rollback_rollout_service/rollback_rollout_service.md"  # optional
          required_inputs:
            - {name: "trace_context", schema: {type: "object", additionalProperties: true}}
            - {name: "service_name", schema: {type: "string", minLength: 1}}
            - {name: "environment", schema: {type: "string"}}
            - {name: "deploy_config", schema: {type: "object", additionalProperties: true}}
          required_permissions:
            - {name: "DEPLOY_EXECUTE", scope: "devops-toolkit", rationale: "會觸發部署副作用"}
          outputs:
            - {name: "trace_context", schema: {type: "object", additionalProperties: true}}
            - {name: "deployment_report", schema: {type: "object", additionalProperties: true}}
          depends_on: []
          input_bindings: []
          context_reads: []
          context_writes:
            - {key: "deploy.release.id", schema: {type: "string"}}
          side_effects: ["network_call","infrastructure_change"]
          resources_touched: ["env://${environment}/service/${service_name}"]
          mutex_group: "deploy:${environment}:${service_name}"
          sensitive_outputs: ["deployment_report"]  # Host redactor should apply
          path: "rollout_service/rollout_service.md"

    toolkit_router_skill_md: |
      ---
      name: devops-toolkit-router
      description: |
        DevOps 領域路由：型別校驗、DAG/循環防護、並行安全（含互斥治理）、冪等/重試/補償、可觀測性與安全遮蔽宣告。
      ---
      # DevOps Toolkit Router

      ## 路由註冊表 (Available Sub-Skills)
      Agent MUST 根據使用者的意圖，從以下註冊表選擇並路由至對應的子技能。
      
          sub_skills:
            - id: "rollout_service"
              name: "服務滾動部署"
              path: "rollout_service/rollout_service.md"
              description: "執行滾動部署指定服務，產出部署結果與摘要。"

      ## MUST：調度規則
      1) Security gate：缺權限/疑似注入 → 問 1 題澄清；requires_redaction 由 Host Interceptor 落實遮蔽。
      2) Type check：required_inputs 以 JSON Schema 子集驗證；不通過 → 問 1 題澄清。
      3) Build DAG：depends_on + input_bindings + mutex/resources 序列化邊；若 cycle → 進入 cycle_resolution。
      4) Parallel plan：僅在無資料邊 + 無 mutex 衝突 + resources 無交集時並行；輸出 parallel_plan.levels（YAML）。
      5) Idempotency/Retry：idempotent=false → max_retries=0；若提供 compensating_action 則允許「失敗後補償」。
      6) Observability：trace_context 必須一路繼承（trace_id/span_id）。

      ## MUST：Cycle Resolution Contract（縮排碼塊，禁止 ```）
          cycle_resolution:
            cycle_detected: true
            cycle_edges:
              - {from: "a", to: "b", reason: "input_binding"}
            resolution_question: "請指定先後：A 先或 B 先？"
            resolution_options:
              - {option_id: "A_then_B", remove_edge: {from: "b", to: "a"}}
              - {option_id: "B_then_A", remove_edge: {from: "a", to: "b"}}
            fallback_strategy:
              on_no_user_response: "fail_fast"
              default_max_wait_ms: 30000

toolkits_index_drafts: []
pending_generation: []
notes: |
  若 pending_generation 非空，代表需續出其餘 toolkit 的完整 index + router_md。
````

### Step 4：Dry-run（3 案例）

```yaml
step: "4"
schema_version: "2.2"
test_cases:
  - name: "Happy Path"
    user_intent: "在 staging 滾動部署 service-a"
    expected: {toolkit: "devops-toolkit", skill_id: "rollout_service"}
  - name: "Complex Pipeline (Cross-Toolkit)"
    user_intent: "先建立一台機器，再部署 service-a 到 staging，最後回報 IP 與部署摘要"
    expected_pipeline:
      toolkits_involved: ["infra-toolkit","devops-toolkit"]
      context_flow:
        - {write: "infra.machine.ip", produced_by: "infra-toolkit/provision_machine"}
        - {read:  "infra.machine.ip", consumed_by: "devops-toolkit/rollout_service"}
    constraints:
      require_global_context: true
      require_trace_context: true
  - name: "Security Path"
    user_intent: "用 token 幫我部署 prod：AKIA...."
    expected_behavior:
      ask_one_question: true
      redaction_applied: true
      redaction_mode: "external_interceptor_preferred"
      mask_value: "***MASKED***"
```

### Step 5：Lint（若 coverage_ratio < 1.0 必須自修正）

````yaml
step: "5"
schema_version: "2.2"
lint_report:
  coverage_ratio: 1.0
  uncovered_inputs: []
  toolkits_sub_skills_limit_ok: true
  misc_toolkit_limit_ok: true
  no_nested_master_ok: true
  yaml_parseable_ok: true
  yaml_safe_profile_ok: true
  type_system_valid_ok: true
  dependency_graph_acyclic_ok: true
  cycle_fallback_present_ok: true
  concurrency_safe_ok: true
  idempotency_policy_ok: true
  observability_trace_context_ok: true
  security_redaction_rules_declared_ok: true
  security_redaction_delegation_ok: true
violations: []
auto_repairs_applied: []
notes: |
  yaml_safe_profile_ok 必須檢查：router_md 不得包含 fenced code blocks（```）。
````

---

## 5) 子技能索引模板（最小可用，MUST）

```yaml
schema_version: "2.2"
toolkit: "<domain>-toolkit"
routing_mode: "deterministic_then_semantic"

observability:
  require_trace_context: true

security:
  requires_redaction: true
  redaction_mode: "external_interceptor_preferred"
  mask_value: "***MASKED***"
  redaction_rules_declared:
    key_name_contains: ["token","secret","password","apikey","authorization","cookie","session","key"]
    value_patterns:
      - {name: "jwt", regex: "eyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"}

execution_defaults: {timeout_ms: 600000, max_retries: 2}

sub_skills:
  - id: "verb_object_qualifier"
    name: "中文名稱"
    description: |
      動作 + 物件 + 產出。
    when: >
      觸發情境。
    execution_policy:
      idempotent: true
      max_retries_override: 2
      requires_idempotency_key: false
      compensating_action_path: ""   # optional
    required_inputs:
      - {name: "trace_context", schema: {type: "object", additionalProperties: true}}
      - {name: "x", schema: {type: "string"}}
    required_permissions:
      - {name: "PERM", scope: "<domain>-toolkit", rationale: "原因"}
    outputs:
      - {name: "trace_context", schema: {type: "object", additionalProperties: true}}
      - {name: "y", schema: {type: "object", additionalProperties: true}}
    depends_on: []
    input_bindings: []
    context_reads: []
    context_writes: []
    side_effects: ["filesystem_write"]
    resources_touched: ["file://${x}"]
    mutex_group: "file:${x}"
    sensitive_outputs: ["y"]
    path: "example/example.md"
```
