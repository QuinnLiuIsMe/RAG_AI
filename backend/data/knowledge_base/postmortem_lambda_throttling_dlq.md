# Postmortem: Lambda Throttling Caused Event Backlog

## Incident summary
A sudden traffic burst exceeded Lambda reserved concurrency. Invocations were throttled, SQS event age increased, and downstream processing delayed by more than 40 minutes.

## Impact
- Event processing SLO breached for order workflow.
- Partial retries increased duplicate processing attempts.
- Customer-facing status updates were delayed.

## Root cause
- Reserved concurrency was set below expected peak.
- Retry behavior from upstream produced retry storms.
- DLQ alarm threshold was too high and fired late.

## Effective remediation
1. Increase reserved concurrency and apply account-level concurrency guardrails.
2. Configure SQS batch size and visibility timeout to reduce hot-loop retries.
3. Add idempotency key checks in handler to tolerate duplicate deliveries.
4. Tighten alarms on `Throttles`, queue age, and DLQ message count.

## Preventive controls
- Load-test peak traffic before major releases.
- Add auto-scaling policy for provisioned concurrency.
- Add runbook drill for Lambda throttling response.
