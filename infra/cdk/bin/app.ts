#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { readInfraContext } from '../lib/context';
import { ComputeStack } from '../lib/compute-stack';
import { EcrStack } from '../lib/ecr-stack';
import { EdgeStack } from '../lib/edge-stack';
import { MonitoringStack } from '../lib/monitoring-stack';
import { NetworkStack } from '../lib/network-stack';

const app = new cdk.App();
const context = readInfraContext(app);
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const networkStack = new NetworkStack(app, 'AiOpsNetworkStack', {
  env,
  useExistingVpc: context.useExistingVpc,
  vpcId: context.vpcId,
  publicSubnetIds: context.publicSubnetIds,
  privateSubnetIds: context.privateSubnetIds,
  maxAzs: context.networkMaxAzs,
  natGateways: context.networkNatGateways,
});

const ecrStack = new EcrStack(app, 'AiOpsEcrStack', {
  env,
  projectName: context.projectName,
  repositoryName: context.ecrRepositoryName,
});

const computeStack = new ComputeStack(app, 'AiOpsComputeStack', {
  env,
  projectName: context.projectName,
  vpc: networkStack.vpc,
  privateSubnets: networkStack.privateSubnets,
  ecrRepository: ecrStack.repository,
  imageTag: context.imageTag,
  desiredCount: context.desiredCount,
  containerPort: context.containerPort,
  appEnv: context.appEnv,
  appLlmProvider: context.appLlmProvider,
  appRateLimitPerMinute: context.appRateLimitPerMinute,
});

new EdgeStack(app, 'AiOpsEdgeStack', {
  env,
  projectName: context.projectName,
  loadBalancer: computeStack.loadBalancer,
});

new MonitoringStack(app, 'AiOpsMonitoringStack', {
  env,
  projectName: context.projectName,
  alarmEmail: context.alarmEmail,
  loadBalancer: computeStack.loadBalancer,
  targetGroup: computeStack.targetGroup,
  service: computeStack.service,
});
