# Week 4 Demo Script (3-5 minutes)

## 1. Open with architecture (45s)

- Show `README.md` architecture diagram.
- Explain request path: Frontend -> API Gateway -> ALB -> ECS FastAPI.
- Explain RAG path: FastAPI -> local knowledge retrieval -> grounded response with citations.
- Highlight observability path: app logs/metrics -> CloudWatch dashboard/alarms.

## 2. Prove CI/CD + deployment posture (60s)

- Show GitHub Actions workflow `.github/workflows/backend-ci-cd.yml`.
- Mention stages: test, build+push image to ECR, deploy ECS rolling refresh.
- Mention required GitHub secrets and CDK context values used to wire environment.

## 3. Run functional API flow (90s)

- Call `GET /health` and `GET /ready`.
- Send `POST /ask` with an incident-style prompt.
- Show response includes `answer`, `citations`, and `confidence`.
- Send `POST /recommend-remediation` and highlight concise action plan output.

## 4. Show ops observability (45s)

- Open `/metrics` endpoint and point out request counters and latency fields.
- Open CloudWatch dashboard and alarms for 5xx + latency.

## 5. Close with reliability and SLO framing (30s)

- State current SLO target from README.
- Explain known gaps and next hardening steps (TLS, WAF, Redis, OTel exporter).
