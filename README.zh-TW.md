繁體中文 | [English](README.md)

# 將 AI Agent 技能重構為階層式路由

本技能旨在將扁平化的 AI Agent 技能庫重構為「階層式 Toolkit 路由 + 全域 Root 路由」的企業級合約結構。它會解析簡易的技能檔案，並將其整理為高內聚的領域 toolkit，以確保擴展性、型別安全，並在所有技能中保持完整的可觀測性。

## 關鍵保證 (Key Guarantees)
- **Step0–5 全 YAML 輸出**：確保產出可被程式系統輕鬆解析。
- **覆蓋率守恆**：確保沒有任何輸入技能被遺漏。允許整併與拆分，但結果必須是可驗證的。
- **DAG / 循環防護（含無人值守 fallback）**：在生成 pipeline 階段可偵測迴圈，並能提出解救問題，同時提供自動化備案（fallback）。
- **並行安全**：透過資料依賴與副作用/資源互斥治理，達成並行的排程安全。
- **安全遮蔽宣告**：採用外部攔截模式（host interceptor），有系統地遮蔽敏感資訊。
- **Trace Context 繼承**：透過 `trace_id` 和 `span_id` 保留可觀測性。

## 如何使用
- **英文團隊**：請將 `SKILL.md` 餵給您的 Agent。
- **中文團隊**：請將 `SKILL.zh-TW.md` 餵給您的 Agent。
- 產出將包含 Step0 到 Step5，每步驟的產出 **必須** 是單一的 YAML 格式，且能被 `yaml.safe_load` 成功解析。

## 專案結構
```
.
├── SKILL.md                 # 規範版英文技能描述
├── SKILL.zh-TW.md           # 繁體中文版本技能描述
├── examples/                # 輸入範例與步驟 0 到步驟 5 的產出 YAML
│   ├── inputs/
│   └── outputs/
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
