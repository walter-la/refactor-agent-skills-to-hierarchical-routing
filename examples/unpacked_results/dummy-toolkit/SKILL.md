---
name: dummy-toolkit
description: Domain toolkit for Intake and Extract
---
# Dummy Toolkit
Domain specific routing.

```yaml
schema_version: "2.2"
toolkit: "dummy-toolkit"
routing_mode: "deterministic_then_semantic"
sub_skills:
  - id: "dummy-01-intake"
    name: "Intake"
    description: "Intake phase."
    path: "dummy-01-intake/dummy-01-intake.md"
  - id: "dummy-02-extract"
    name: "Extract"
    description: "Extract phase."
    path: "dummy-02-extract/dummy-02-extract.md"
```
