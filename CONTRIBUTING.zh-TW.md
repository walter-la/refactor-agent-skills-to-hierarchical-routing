# 貢獻指南

感謝您的貢獻！

## 本地環境與驗證
1. 確認已安裝 Python 3。
2. 安裝依賴：`pip install -r requirements.txt`
3. 提交 (Commit) 之前，請在本地端執行驗證工具：`python tools/validate_repo.py`

## PR 檢查清單
- [ ] 確保 `SKILL.md` 與 `SKILL.zh-TW.md` 中的 `name` 與 `schema_version` 保持一致。
- [ ] 若修改範例，請確保其能被 `yaml.safe_load` 成功解析。
- [ ] **嚴禁** 在 YAML 範例的 Router markdown 區塊中使用 fenced code blocks (```)。

請確保您的 PR 能夠順利通過所有的 CI 驗證。
