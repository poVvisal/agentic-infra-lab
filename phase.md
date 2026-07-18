# PROJECT PHASES — agentic-infra-lab

A progressive learning project to practice production-grade AI agent infrastructure
(orchestration, observability, platform primitives) on top of existing AWS + Spring
Boot + Terraform + Docker skills. Architecture: Hybrid, staged rollout — local-first
with Ollama, self-hosted Langfuse for tracing, swapping to Bedrock only once the
pipeline is proven, with an optional local-Kubernetes capstone. No AWS spend until
Phase 4; no billable resource left running unattended (see PROJECT_CONTEXT.md rules).

---

## Phase 0 — Environment & Repo Skeleton

**Objective**
Stand up the project repository and a minimal Docker Compose network containing
only Ollama, and confirm a model runs and responds locally before any Spring Boot
code exists. This isolates "does my local AI runtime work" from every later
variable, so if something breaks in Phase 1 you know it's not Ollama.

**Files / resources touched**
- `docker-compose.yml` (single `ollama` service + named volume)
- `.gitignore`
- `README.md`
- `PROJECT_CONTEXT.md` (created)

**What "done" looks like**
Running `docker compose up -d` starts Ollama, `docker exec` pulling a model succeeds,
and `curl http://localhost:11434/api/generate -d '{"model":"llama3.1:8b","prompt":"hi"}'`
returns a real generated response.

**Checklist**
- [ ] Repo initialized, README with one-paragraph project description
- [ ] docker-compose.yml with ollama service, named volume for model persistence, exposed on 11434
- [ ] Model pulled (e.g. llama3.1:8b) and persists across container restart
- [ ] curl test against /api/generate returns a valid completion
- [ ] PROJECT_CONTEXT.md committed with initial architecture decision

---

## Phase 1 — Echo Agent (Spring Boot + Ollama)

**Objective**
Build the smallest possible Spring Boot service that accepts a prompt over REST,
forwards it to Ollama via Spring AI, and returns the raw response — no tracing,
no retries, no cleverness yet. This is the "hello world" for the agent brain and
your first real Spring Boot + AI integration, since Spring Boot itself is new to you.

**Files / resources touched**
- `agent-service/pom.xml` (new Maven module, spring-ai-ollama-starter dependency)
- `agent-service/src/main/java/.../AgentController.java`
- `agent-service/src/main/java/.../AgentService.java`
- `agent-service/src/main/resources/application.yml`
- `agent-service/Dockerfile`
- `docker-compose.yml` (add `agent-service`, wired to `ollama` via Docker network name, not localhost)

**What "done" looks like**
`docker compose up` brings up both containers; `POST /api/chat` with body
`{"prompt": "hi"}` returns a real LLM-generated JSON response from the agent-service,
proxied through to Ollama.

**Checklist**
- [ ] Spring Boot app scaffolded with spring-ai-ollama-starter dependency
- [ ] application.yml points to `ollama` (Docker service name), not 127.0.0.1
- [ ] AgentController exposes POST /api/chat, delegates to AgentService
- [ ] Dockerfile builds a runnable jar image, added to compose
- [ ] Manual test via curl/Postman returns a coherent response
- [ ] PROJECT_CONTEXT.md updated: port map, package naming confirmed in practice

---

## Phase 2 — Add Langfuse, Get First Trace

**Objective**
Stand up the full self-hosted Langfuse stack (Postgres, ClickHouse, Redis, MinIO,
langfuse-web) in Docker Compose, then attach the OpenTelemetry Java agent to the
Spring Boot service so every /api/chat call automatically produces a visible trace.
This is where observability stops being an abstract concept from Dimitri's post and
becomes something you can literally click through.

**Files / resources touched**
- `docker-compose.yml` (add langfuse-web, postgres, clickhouse, redis, minio services)
- `.env` (Langfuse public/secret API keys, gitignored)
- `agent-service/Dockerfile` (bundle OTel Java agent jar)
- `docker-compose.yml` (JAVA_TOOL_OPTIONS env var pointing at OTel agent + OTLP endpoint)

**What "done" looks like**
Langfuse UI is reachable at localhost:3000, a project + API keypair exists, and
after calling /api/chat you can open Langfuse and see a trace with latency, input
prompt, and output response attached to it — zero code changes required for this
first trace (zero-code / auto-instrumentation).

**Checklist**
- [ ] Full Langfuse stack running via docker compose, UI reachable on :3000
- [ ] Langfuse project created, API keys generated and stored in .env
- [ ] OTel Java agent attached to agent-service via JAVA_TOOL_OPTIONS
- [ ] OTLP exporter endpoint correctly pointed at Langfuse's ingestion endpoint
- [ ] Test /api/chat call appears as a trace in Langfuse UI within seconds
- [ ] RAM/CPU usage while all 6 containers run noted in PROJECT_CONTEXT.md

---

## Phase 3 — Custom Spans + Retry / Multi-Step Logic

**Objective**
Move past pure auto-instrumentation: add a small multi-step behavior to the agent
(e.g. retry-on-failure, or a "plan then answer" two-call flow), and manually
instrument it with custom OpenTelemetry spans and attributes. This directly targets
the "tracing decisions, failures, and loops" skill called out as the differentiator
in the original post — auto-instrumentation only gets you HTTP-level traces, not
agent-logic-level ones.

**Files / resources touched**
- `agent-service/.../AgentService.java` (retry logic, or plan-then-answer flow)
- `agent-service/.../TracingConfig.java` (new — manual OTel Tracer bean/config)
- `application.yml` (tunable retry count / timeout config)

**What "done" looks like**
Forcing a failure (bad prompt, simulated timeout, or a kill-switch flag) produces a
visible parent-child span tree in Langfuse showing the retry sequence, with custom
attributes like `agent.step`, `agent.retry_count`, and `agent.outcome` attached to
each span — not just one flat HTTP span.

**Checklist**
- [ ] Retry or multi-step agent logic implemented in AgentService
- [ ] Custom OTel spans created manually around each logical step (not just auto-instrumented HTTP calls)
- [ ] Custom span attributes added (step name, retry count, outcome)
- [ ] Forced-failure scenario tested and confirmed visible as a trace tree in Langfuse
- [ ] PROJECT_CONTEXT.md updated with span-naming and attribute conventions

---

## Phase 4 — Swap Ollama for Bedrock + AWS Platform Primitives

**Objective**
Introduce real AWS infrastructure: use Terraform to provision a least-privilege IAM
role/policy scoped only to `bedrock:InvokeModel` on a specific model ARN, ensure no
credentials are ever hardcoded (Secrets Manager or instance-profile injection only),
and swap the Spring AI backend from Ollama to Amazon Bedrock. This is the "platform
primitives" phase from the original thesis — proving you can give an agent workload
narrow, auditable access rather than broad IAM permissions.

**Files / resources touched**
- `terraform/provider.tf`, `terraform/iam.tf`, `terraform/secrets.tf`
- `agent-service/.../application.yml` (new `bedrock` Spring profile)
- `agent-service/.../BedrockAgentService.java` (or config swap if Spring AI abstracts this cleanly)
- `.env` / Secrets Manager reference (never plaintext keys in code)

**What "done" looks like**
The exact same `/api/chat` endpoint now calls Amazon Bedrock instead of Ollama, using
Terraform-provisioned least-privilege credentials, and the call is traced in Langfuse
exactly as it was for Ollama — proving the observability layer is model-agnostic.

**Checklist**
- [ ] Terraform applies IAM role + policy scoped to InvokeModel on a specific model ARN only (no wildcard actions/resources)
- [ ] Credentials delivered via Secrets Manager or instance profile — zero plaintext keys committed
- [ ] Spring Boot bedrock profile successfully calls Bedrock and returns a response
- [ ] Bedrock calls appear in Langfuse traces identically to prior Ollama calls
- [ ] Token spend checked and confirmed to be cents-level, not dollars
- [ ] `terraform destroy` run and documented — confirm no lingering billable resources
- [ ] PROJECT_CONTEXT.md updated: Bedrock model ID used, IAM policy summary, cost observed

---

## Phase 5 (Optional Capstone) — Deploy to Local Kubernetes (kind)

**Objective**
Convert the working Docker Compose stack into Kubernetes manifests running on a
local `kind` cluster (zero EKS billing), practicing agent-orchestration concepts —
resource requests/limits, and a retry pattern expressed as a Kubernetes Job rather
than in-app logic. This maps directly to the original post's "agent orchestration on
Kubernetes — how agents scale, retry, and hand off tasks" point.

**Files / resources touched**
- `k8s/agent-deployment.yaml`, `k8s/agent-service.yaml`
- `k8s/langfuse-*.yaml` (or decision to point at Langfuse Cloud free tier instead — see Open Decisions)
- `k8s/retry-job.yaml` (Job manifest demonstrating retry/backoff)
- `PROJECT_CONTEXT.md` (final update)

**What "done" looks like**
`kind create cluster` + `kubectl apply -f k8s/` brings the stack up, `kubectl
port-forward` lets you hit /api/chat exactly as before, and a deliberately-failing
Job demonstrates Kubernetes-native retry/backoff behavior instead of app-level retry.

**Checklist**
- [ ] kind cluster created, kubectl context confirmed
- [ ] agent-service and dependencies deployed via manifests (or Langfuse Cloud used to simplify)
- [ ] Resource requests/limits explicitly set (not left as cluster defaults)
- [ ] Retry-as-Job pattern demonstrated with a deliberately failing task
- [ ] Full stack reachable via port-forward, /api/chat works end-to-end
- [ ] PROJECT_CONTEXT.md finalized — decision on kind-only vs future real-EKS documented

---

## Cross-Phase Rules (see PROJECT_CONTEXT.md for full list)
Never hardcode AWS credentials. Never leave billable AWS resources running
unattended. Never extend agent logic before it's traceable. Never grant broad IAM
permissions. One phase per branch, merged only when its checklist is fully ticked.
Never move to Bedrock (Phase 4) before Ollama+Langfuse works completely locally.
