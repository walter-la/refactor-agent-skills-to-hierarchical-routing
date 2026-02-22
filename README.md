English | [繁體中文](README.zh-TW.md)

# Refactor Agent Skills to Hierarchical Routing

This repository provides a **meta-skill** (a skill executed by an AI Agent) designed to transform a chaotic, flattened directory of AI skills into an **enterprise-grade, hierarchical brain**. 

If you have dozens of flat `.md` files acting as your agent's skills, this tool will automatically categorize them into "Domain Toolkits" and generate a highly secure, concurrency-safe, and type-checked **Router** for each toolkit.

---

## 💡 What exactly does this do? (Before & After)

Think of this as a **corporate restructuring for your AI Agent**:

*   **⚠️ Before (The Pain Point)**:
    You have a pile of post-it note-like skill instructions (e.g., `deploy_script.md`, `restart_server.md`). Your AI treats them like a grab bag. There are no strict input definitions, no collision-prevention mechanisms (mutex), and no retry rules. In complex, real-world scenarios, this easily leads to failures or secret leaks.
*   **✨ After (Refactored by this Skill)**:
    The AI organizes your skills into cohesive domains (e.g., `devops-toolkit/`). Within that folder, it generates an enterprise **Router (`SKILL.md`)**. This router acts as a strict gatekeeper before executing any sub-skill:
    > "Wait! You want to deploy, but your input doesn't match the JSON Schema!"
    > "Wait! You want to run A and B simultaneously? No, they touch the same database; they must be queued (Mutex)!"
    > "Wait! You're outputting a Log? I need to mask the Tokens and Passwords (`***MASKED***`) first!"

👉 **You can directly browse [examples/03-outputs/skills/dummy-toolkit/](examples/03-outputs/skills/dummy-toolkit/) to experience how rigorous and structured the "After" state is.**

---

## 🛠 How it Works (The Workflow)

If you feed the `SKILL.md` prompt from this repository to your AI Agent along with your current list of skills, it will sequentially output 6 YAML reports (Step 0 ~ Step 5):

1.  **Cleansing (Step 0)**: Reads your existing skills' names, descriptions, and paths, and infers missing metadata.
2.  **Domain Grouping (Step 1)**: Clusters skills by verbs and objects into "Domain Toolkits" (like `aws-toolkit`, `db-toolkit`) and establishes a Global Root Router.
3.  **Migration & Coverage Check (Step 2)**: Outputs an `old_path -> new_path` migration plan. It enforces a "Coverage Check" to ensure no old skill is accidentally left behind.
4.  **Router Generation (Step 3)**: Drafts the Master `SKILL.md` index for each toolkit, injecting strict JSON Schemas, DAG dependencies, and Security Redaction rules.
5.  **Dry-run & Lint (Step 4 & 5)**: Simulates hypothetical tasks and performs syntax/logic validations.

> **📝 Why output a bunch of YAMLs instead of ready-to-use .md files?**
> This is specifically designed so your automation scripts (like Python or CI tools) can safely parse the layout using `yaml.safe_load()`. If an LLM directly outputs massive Markdown code blocks, it frequently breaks formatting. YAML ensures 100% programmatic reliability for auto-generating folders and moving files.

---

## 🚀 How to Use

1.  Pick the instruction file for your team:
    *   **English Teams**: Feed `SKILL.md` to your Agent.
    *   **Chinese Teams**: Feed `SKILL.zh-TW.md` to your Agent.
2.  Provide the Agent with your existing skills inventory (refer to `examples/01-inputs/skills/`).
3.  Extract the Step 0 to Step 5 YAML outputs from the Agent, and write a small script to "unpack" them into actual directories.

---

## 📦 Key Enterprise Guarantees

## Repository Structure
```
.
├── SKILL.md                 # Canonical English skill descriptor
├── SKILL.zh-TW.md           # Traditional Chinese skill descriptor
├── examples/                # Examples containing original inputs, process, and outputs
│   ├── 01-inputs/           # Mock original flattened skills directory
│   ├── 02-intermediate/     # Intermediate YAML outputs from Step 0 to Step 5
│   └── 03-outputs/          # The final unpacked hierarchical routing toolkit structures
├── tools/                   # Validation tools
│   └── validate_repo.py
└── ...
```

## CI / Validation
This repository runs rigorous validation checks in GitHub Actions (`.github/workflows/ci.yml`). Checks include:
- `name` and `schema_version` consistency between `SKILL.md` and `SKILL.zh-TW.md`
- Parseability of all step examples using `PyYAML`
- Assertion that the YAML safe profile is maintained (e.g. no fenced code blocks within router markdown strings inside YAML)

## Contributing
We welcome contributions! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for local setup and PR checklist requirements before you submit.

## Author
Designed by Walter Chien.