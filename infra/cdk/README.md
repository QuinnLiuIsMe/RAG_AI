# AWS CDK Deployment (TypeScript, Week 4)

This CDK app provisions a production-like baseline on AWS with dedicated stacks:
- `AiOpsNetworkStack`: creates a new VPC by default, or imports existing VPC/subnets
- `AiOpsEcrStack`: creates backend ECR repository (auto-clean on stack delete)
- `AiOpsComputeStack`: ECS Fargate, ALB, task logging
- `AiOpsEdgeStack`: API Gateway HTTP API proxy to ALB
- `AiOpsMonitoringStack`: CloudWatch dashboard/alarms + optional SNS email

## Prerequisites

- Node.js 22+
- AWS CDK v2
- AWS credentials with permissions for ECS, ELB, API Gateway, CloudWatch, SNS, IAM

## Install

```bash
cd infra/cdk
npm install
```

## Bootstrap (first time per account/region)

```bash
npx cdk bootstrap
```

## Deploy (New AWS Account / Auto-create VPC)

This is the default mode. It creates:
- a new VPC
- public and private subnets across 2 AZs
- NAT Gateway count defaults to `1` (cost-aware)

```bash
npx cdk deploy --all \
  --require-approval never \
  -c projectName=ai-ops-copilot \
  -c imageTag=latest \
  -c networkMaxAzs=2 \
  -c networkNatGateways=1 \
  -c alarmEmail=oncall@example.com
```

## Deploy (Use Existing VPC)

Pass environment-specific values as CDK context:

```bash
npx cdk deploy --all \
  --require-approval never \
  -c projectName=ai-ops-copilot \
  -c useExistingVpc=true \
  -c vpcId=vpc-xxxxxxxx \
  -c publicSubnetIds=subnet-public-a,subnet-public-b \
  -c privateSubnetIds=subnet-private-a,subnet-private-b \
  -c ecrRepositoryName=ai-ops-copilot-backend \
  -c imageTag=latest \
  -c alarmEmail=oncall@example.com
```

## Required Context

When `useExistingVpc=true`, these become required:
- `vpcId`
- `publicSubnetIds` (comma-separated)
- `privateSubnetIds` (comma-separated)

## Deployment Order

When using `--all`, CDK resolves cross-stack references and deploys in dependency order.

## Optional Context

- `projectName` (default `ai-ops-copilot`)
- `imageTag` (default `latest`; recommend commit SHA/version tag in production)
- `containerPort` (default `8000`)
- `desiredCount` (default `2`)
- `networkMaxAzs` (default `2`)
- `networkNatGateways` (default `1`)
- `useExistingVpc` (default `false`; auto true when `vpcId` is provided)
- `ecrRepositoryName` (default `${projectName}-backend`)
- `appEnv` (default `prod`)
- `appLlmProvider` (default `mock`)
- `appRateLimitPerMinute` (default `120`)
- `alarmEmail` (default empty)

## Where To Put AWS Config

### Local deployment

AWS account/region come from your active AWS credentials/profile (`CDK_DEFAULT_ACCOUNT`, `CDK_DEFAULT_REGION`).

You provide infra/app values via `-c` context flags (examples above), or store defaults in `cdk.json` under `context`.

### GitHub Actions deployment

Set these repository secrets (used by `.github/workflows/backend-ci-cd.yml`):

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REPOSITORY`
- `ALARM_EMAIL` (optional)

If you deploy with existing VPC mode in CI, also set:
- `VPC_ID`
- `PUBLIC_SUBNET_IDS`
- `PRIVATE_SUBNET_IDS`

### ECS note

This CDK app creates both ECR and ECS resources for you (`AiOpsEcrStack` + `AiOpsComputeStack`). Keep `imageTag` aligned with the image you pushed.
