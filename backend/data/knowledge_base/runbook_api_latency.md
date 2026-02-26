# Runbook: API Latency And Timeout Spikes

## Symptoms
- P95 latency spikes above 2 seconds.
- Increased upstream timeout errors from gateway.
- CPU and connection pool saturation on application nodes.

## Immediate actions
1. Confirm blast radius by service version and availability zone.
2. Scale application replicas by 30% and monitor queue depth.
3. Reduce query fan-out and apply temporary cache TTL for hot endpoints.
4. Increase timeout budgets only after dependency latency is validated.

## Validation
- Error rate should drop below 2%.
- P95 latency should return to baseline within 15 minutes.
