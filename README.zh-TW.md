繁體中文 | [English](README.md)

# 將 AI Agent 技能重構為階層式路由 (Refactor Agent Skills to Hierarchical Routing)

這是一個用來**「將散落一地的散裝 AI 技能，重構成企業級大腦系統」**的 meta-skill（給 AI 執行的技能）。

如果你的專案裡有幾十個扁平的 `.md` 技能檔，這個工具能幫你把它們自動分門別類成「多個領域 Toolkit」，並為每個 Toolkit 自動生成具備**安全防護、型別校驗、並行控制**的路由大腦（Router）。

---

## 💡 這到底是在做什麼？ (Before & After)

你可以把這當作**「AI 的公司組織重整」**：

*   **⚠️ Before (目前的痛點)**：
    你有一堆像便利貼一樣的技能說明（如 `部署腳本.md`、`重啟伺服器.md`）。AI 把這些當作萬事通，但沒有定義嚴格的輸入格式、防撞車機制，或是遇到斷線能不能自動重試。這在複雜的真實場景下非常容易出錯或洩漏密碼。
*   **✨ After (經過本技能重構後)**：
    AI 幫你把技能按領域打包（例如 `devops-toolkit/`）。在該資料夾內，會自動生成一個企業級的**總機路由器 (`SKILL.md`)**。這個路由器會在執行你的子技能前，嚴格把關：
    > 「等等！你想執行佈署，但你給的輸入不符合 JSON Schema！」
    > 「等等！你想同時執行 A 和 B？不行，你們會動到同一個資料庫，必須排隊 (Mutex)！」
    > 「等等！你要輸出 Log？我得先把 Token 和密碼打上星號 (`***MASKED***`)！」

👉 **你可以直接查看 [examples/03-outputs/skills/dummy-toolkit/](examples/03-outputs/skills/dummy-toolkit/)，體驗「重整後」的企業級目錄結構與安全合約到底長得多嚴謹。**

---

## 🛠 它實際的工作流程

若你將本專案的 `SKILL.zh-TW.md` 作為 Prompt 餵給你的 AI Agent，並給它你現有的技能清單，它會依序吐出 6 份 YAML 格式的報告（Step 0 \~ Step 5）：

1.  **盤點與清理 (Step 0)**：讀取你現有 skills 的名稱、描述與路徑，補齊缺漏的 metadata。
2.  **領域分組 (Step 1)**：把 skills 依照動詞與物件，聚類成幾個「領域 toolkit」(例如 aws-toolkit, db-toolkit)，並建立全域 Root Router。
3.  **搬移與守恆檢查 (Step 2)**：產出 `old_path -> new_path` 的搬檔清單，並強制檢查「覆蓋率」，確保重構過程沒有不小心遺漏任何一個舊技能。
4.  **產出企業級 Router (Step 3)**：為每個 toolkit 撰寫一份包含嚴格 JSON Schema、DAG 依賴與機密遮蔽宣告的 Master `SKILL.md` 目錄草稿。
5.  **測試與 Lint (Step 4 & 5)**：進行假想任務的沙盤推演，並執行格式和防呆驗證。

> **📝 為什麼輸出是一堆 YAML 而不是直接給 .md 檔？**
> 這是為了讓你的自動化腳本 (如 Python / CI) 可以使用 `yaml.safe_load()` 100% 安全地解析這些規劃，自動幫你建立資料夾又搬移檔案。LLM 如果直接輸出大量 Markdown 程式碼區塊通常會導致格式壞掉。

---

## 🚀 如何使用

1.  挑選適合你團隊的語系文件：
    *   **英文團隊**：請餵給 Agent `SKILL.md`。
    *   **中文團隊**：請餵給 Agent `SKILL.zh-TW.md`。
2.  提供你的技能清單給 Agent (可參考 `examples/01-inputs/skills/`)。
3.  擷取 Agent 輸出的 Step 0 到 Step 5 YAML，並撰寫一隻小腳本將其解開為真實目錄。

---

## 📦 關鍵企業級保證 (Key Guarantees)

## 專案結構
```
.
├── SKILL.md                 # 規範版英文技能描述
├── SKILL.zh-TW.md           # 繁體中文版本技能描述
├── examples/                # 範例目錄包含輸入、代理推論過程與最終產出
│   ├── 01-inputs/           # 模擬人類原始散裝技能目錄
│   ├── 02-intermediate/     # 存放步驟 0 到步驟 5 的產出 YAML 過程
│   └── 03-outputs/          # 最終轉換出的完整 Toolkit 結構與 Routing 合約
├── tools/                   # 驗證工具
│   └── validate_repo.py
└── ...
```

## CI / 自動化驗證 (Validation)
本專案在 GitHub Actions (`.github/workflows/ci.yml`) 會執行嚴格的自動化驗證機制：
- 確保 `SKILL.md` 與 `SKILL.zh-TW.md` 的 `name` 和 `schema_version` 一致。
- 使用 `PyYAML` 確認所有範例皆可成功解析。
- 確保 YAML-safe profile (如：YAML 格式的 Router markdown 中不得出現 fenced code blocks)。

## 參與貢獻
我們歡迎您的參與！送交 PR 前請務必至 [CONTRIBUTING.zh-TW.md](CONTRIBUTING.zh-TW.md) 了解如何於本地端驗證，並確認完成 PR 檢查清單。

## 作者 (Author)
本技能由 Walter Chien 設計。
