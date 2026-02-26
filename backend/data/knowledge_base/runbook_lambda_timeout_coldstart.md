# Runbook: Lambda Timeout And Cold Start Regression

## Symptoms
- API Gateway returns intermittent 502/504 responses.
- Lambda `Duration` frequently approaches configured timeout.
- `Init Duration` increases after deployment and scales with concurrency spikes.

## Likely causes
- Package size growth increased cold start cost.
- VPC-enabled Lambda has ENI initialization overhead.
- Downstream dependency latency increased request critical path.

## Immediate actions
1. Confirm the affected function version and alias traffic split.
2. Increase provisioned concurrency for critical aliases.
3. Raise function memory to improve CPU share and reduce init latency.
4. Review timeout settings to ensure they exceed downstream p95 latency with safety margin.
5. Enable connection reuse for external calls and reduce SDK client re-initialization.

## Validation
- `Errors` and 5xx rate drop to baseline.
- p95 `Duration` remains below 70% of timeout.
- `Init Duration` stabilizes during traffic bursts.

## Follow-up
- Move heavyweight initialization out of hot path.
- Keep deployment artifact minimal and remove unused dependencies.
