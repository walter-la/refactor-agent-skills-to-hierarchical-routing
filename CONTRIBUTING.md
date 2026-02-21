# Contributing

Thank you for contributing! 

## Local Setup & Validation
1. Have Python 3 installed.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the validation tool locally before committing: `python tools/validate_repo.py`

## PR Checklist
- [ ] Ensure `name` and `schema_version` remain consistent across `SKILL.md` and `SKILL.zh-TW.md`.
- [ ] If you modify examples, ensure they are parseable via `yaml.safe_load`.
- [ ] **NO** fenced code blocks (```) are allowed inside router markdown block scalars within the YAML examples.

Please make sure your PR passes the CI checks.
