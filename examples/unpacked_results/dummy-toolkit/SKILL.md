---
name: dummy-toolkit-router
description: Dummy Router that handles basic tasks.
---

# Dummy Router

## Routing Rules
1) **Security gate**: check missing permissions or injection. Deny or ask clarifying questions.
2) **Type check**: validate `required_inputs` with JSON schema subset.
3) **Build DAG**: construct execution graph based on `depends_on`, `input_bindings`, and mutex/resources.
4) **Parallel plan**: parallelize when safe.
5) **Idempotency/Retry**: block retries if `idempotent=false`.
6) **Observability**: inherit `trace_id` and `span_id`.

## Toolkit Index (Auto-Generated)
The following is the YAML index containing all sub-skills governed by this router.

```yaml
schema_version: "2.2"
toolkit: "dummy-toolkit"
routing_mode: "deterministic_then_semantic"
security:
  requires_redaction: true
  redaction_mode: "external_interceptor_preferred"
  mask_value: "***MASKED***"
  redaction_rules_declared:
    key_name_contains: ["secret"]
    value_patterns: []
execution_defaults: {timeout_ms: 600000, max_retries: 2}
observability:
  require_trace_context: true
sub_skills:
  - id: "dummy1"
    name: "Dummy 1"
    description: "Dummy 1 description"
    when: "triggered"
    execution_policy:
      idempotent: true
      max_retries_override: 2
      requires_idempotency_key: false
      compensating_action_path: ""
    required_inputs:
      - {name: "trace_context", schema: {type: "object", additionalProperties: true}}
    required_permissions: []
    outputs: []
    depends_on: []
    input_bindings: []
    context_reads: []
    context_writes: []
    side_effects: []
    resources_touched: []
    mutex_group: "dummy1"
    sensitive_outputs: []
    path: "sub_skills/dummy1.md"
  - id: "dummy2"
    name: "Dummy 2"
    description: "Another simple dummy"
    when: "triggered"
    execution_policy:
      idempotent: true
      max_retries_override: 2
      requires_idempotency_key: false
      compensating_action_path: ""
    required_inputs:
      - {name: "trace_context", schema: {type: "object", additionalProperties: true}}
    required_permissions: []
    outputs: []
    depends_on: []
    input_bindings: []
    context_reads: []
    context_writes: []
    side_effects: []
    resources_touched: []
    mutex_group: "dummy2"
    sensitive_outputs: []
    path: "sub_skills/dummy2.md"
  - id: "dummy3"
    name: "Dummy 3"
    description: "Third dummy"
    when: "triggered"
    execution_policy:
      idempotent: true
      max_retries_override: 2
      requires_idempotency_key: false
      compensating_action_path: ""
    required_inputs:
      - {name: "trace_context", schema: {type: "object", additionalProperties: true}}
    required_permissions: []
    outputs: []
    depends_on: []
    input_bindings: []
    context_reads: []
    context_writes: []
    side_effects: []
    resources_touched: []
    mutex_group: "dummy3"
    sensitive_outputs: []
    path: "sub_skills/dummy3.md"
```
