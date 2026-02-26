# Postmortem: Database Connection Pool Exhaustion

## Incident summary
A deployment introduced a blocking query pattern. During peak traffic the connection pool saturated, causing 5xx errors and timeout retries.

## Root cause
- Missing index on frequently filtered field.
- Burst traffic triggered lock contention.
- Retry policy amplified load on primary database.

## Effective remediation
1. Roll back the deployment and invalidate stale cache keys.
2. Add query index and tune connection pool limits.
3. Introduce canary release guardrail with automatic rollback on error rate threshold.

## Preventive controls
- Alert on DB pool usage > 85% for 5 minutes.
- Add synthetic query latency checks in pre-deploy pipeline.
