import * as cdk from 'aws-cdk-lib';

export interface InfraContext {
  projectName: string;
  vpcId: string;
  ecrRepositoryName: string;
  publicSubnetIds: string[];
  privateSubnetIds: string[];
  imageTag: string;
  desiredCount: number;
  containerPort: number;
  appEnv: string;
  appLlmProvider: string;
  appRateLimitPerMinute: string;
  alarmEmail: string;
}

export function readInfraContext(app: cdk.App): InfraContext {
  const required = (name: string): string => {
    const value = app.node.tryGetContext(name);
    if (!value || String(value).trim() === '') {
      throw new Error(`Missing required CDK context: ${name}`);
    }
    return String(value);
  };

  const list = (name: string): string[] =>
    required(name)
      .split(',')
      .map((item) => item.trim())
      .filter((item) => item.length > 0);

  return {
    projectName: String(app.node.tryGetContext('projectName') ?? 'ai-ops-copilot'),
    vpcId: required('vpcId'),
    ecrRepositoryName: required('ecrRepositoryName'),
    publicSubnetIds: list('publicSubnetIds'),
    privateSubnetIds: list('privateSubnetIds'),
    imageTag: String(app.node.tryGetContext('imageTag') ?? 'latest'),
    desiredCount: Number(app.node.tryGetContext('desiredCount') ?? 2),
    containerPort: Number(app.node.tryGetContext('containerPort') ?? 8000),
    appEnv: String(app.node.tryGetContext('appEnv') ?? 'prod'),
    appLlmProvider: String(app.node.tryGetContext('appLlmProvider') ?? 'mock'),
    appRateLimitPerMinute: String(app.node.tryGetContext('appRateLimitPerMinute') ?? '120'),
    alarmEmail: String(app.node.tryGetContext('alarmEmail') ?? ''),
  };
}
