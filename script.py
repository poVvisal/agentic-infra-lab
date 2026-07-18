import os
os.makedirs('output', exist_ok=True)

content = """# PROJECT_CONTEXT.md

## Project Name
agentic-infra-lab (working title)

## Purpose
A progressive learning project to practice production-grade AI agent infrastructure:
agent orchestration, observability (tracing), and platform primitives (IAM/secrets),
built on top of existing AWS + Spring Boot + Terraform + Docker skills.

## Architecture Decision (as of Phase 0)
**Chosen path:** Hybrid, staged rollout (Option B from planning discussion)
- Start 100% local (Ollama + Spring Boot + self-hosted Langfuse via Docker Compose)
- No cloud spend until Phase 4
- Swap Ollama -> Amazon Bedrock only after tracing pipeline is proven locally
- Kubernetes (kind, local only) is an optional capstone (Phase 5) -- no EKS billing
  unless explicitly decided later

## Why this order
- Isolates variables: learn Spring Boot AI integration first, then OTel tracing,
  then AWS IAM/secrets, then K8s -- never more than one new hard concept at a time
- Avoids AWS bills during the "still figuring out Spring Boot" phase
- Ollama -> Bedrock swap is designed to be a config change, not a rewrite
  (Spring AI abstracts the model client)

## Environment
- Local dev machine: i7 13th gen, 32GB RAM -- sufficient for full Langfuse stack
  (Postgres, ClickHouse, Redis, MinIO, langfuse-web) + Ollama + Spring Boot concurrently
- Docker Compose is the orchestration layer for Phases 0-3
- Terraform is introduced starting Phase 4 (AWS resources only, not for local Docker)

## Naming Conventions
- Services in docker-compose.yml: lowercase-hyphenated (e.g. `agent-service`, `ollama`, `langfuse-web`)
- Java packages: `com.<yourname>.agentlab.<layer>` (e.g. `controller`, `service`, `config`)
- Terraform resources: `<project>-<resource>-<env>` e.g. `agentlab-bedrock-role-dev`
- Env vars: SCREAMING_SNAKE_CASE, all secrets referenced via `.env` (gitignored) or
  Secrets Manager from Phase 4 onward -- never inline in application.yml
- Git branches: `phase-0-setup`, `phase-1-echo-agent`, etc. -- one branch per phase,
  merge to main only when phase checklist is fully ticked

## Ports / Local Service Map
| Service | Port | Notes |
|---|---|---|
| ollama | 11434 | Model inference API |
| agent-service (Spring Boot) | 8080 | Main REST API |
| langfuse-web | 3000 | Tracing UI |
| postgres (langfuse) | 5432 | Internal only, not exposed beyond compose network |
| clickhouse (langfuse) | 8123 | Internal only |

## Never Do X (hard rules)
1. Never hardcode AWS credentials or Bedrock keys in application.yml or Java code --
   .env locally, Secrets Manager once on AWS.
2. Never leave an EKS cluster or any billable AWS resource running unattended --
   always `terraform destroy` after a session unless actively demoing.
3. Never skip the tracing step before adding new agent logic -- if you can't see it
   in Langfuse, you can't debug it later. Instrument before you extend.
4. Never grant broad IAM policies (no `bedrock:*` or `*` resource ARNs) --
   scope to specific actions and model ARNs only.
5. Never mix phases in one branch/commit -- each phase should be independently
   revertable and demoable.
6. Never move to Bedrock (Phase 4) until Ollama + Langfuse tracing works completely
   locally first.

## Progress Log
- [ ] Phase 0 -- Environment & repo skeleton
- [ ] Phase 1 -- Echo agent (Spring Boot + Ollama)
- [ ] Phase 2 -- Add Langfuse, get first trace
- [ ] Phase 3 -- Custom spans + retry/tool-call logic
- [ ] Phase 4 -- Swap Ollama for Bedrock + AWS platform primitives
- [ ] Phase 5 (optional capstone) -- Deploy to local Kubernetes (kind)

## Open Decisions (revisit later)
- Which Ollama model to standardize on for consistency across phases (e.g. llama3.1:8b)
- Whether Phase 5 targets kind only, or eventually real EKS (cost decision, revisit
  after Phase 4)
- Whether to keep Langfuse self-hosted long-term or switch to Langfuse Cloud free
  tier for convenience in Phase 5

---
*This file is updated after every phase. Do not let it drift from actual implementation.*
"""

with open('output/PROJECT_CONTEXT.md', 'w') as f:
    f.write(content)

print("done")
