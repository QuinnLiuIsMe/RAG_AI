import * as cdk from 'aws-cdk-lib';

export interface InfraContext {
  projectName: string;
  useExistingVpc: boolean;
  vpcId?: string;
  ecrRepositoryName: string;
  publicSubnetIds: string[];
  privateSubnetIds: string[];
  networkMaxAzs: number;
  networkNatGateways: number;
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

  const optional = (name: string): string | undefined => {
    const value = app.node.tryGetContext(name);
    if (value === undefined || value === null) {
      return undefined;
    }
    const text = String(value).trim();
    return text === '' ? undefined : text;
  };

  const optionalList = (name: string): string[] => {
    const value = optional(name);
    if (!value) {
      return [];
    }
    return value
      .split(',')
      .map((item) => item.trim())
      .filter((item) => item.length > 0);
  };

  const projectName = String(app.node.tryGetContext('projectName') ?? 'ai-ops-copilot');
  const vpcId = optional('vpcId');
  const useExistingVpc =
    String(app.node.tryGetContext('useExistingVpc') ?? (vpcId ? 'true' : 'false')).toLowerCase() === 'true';
  const publicSubnetIds = useExistingVpc ? list('publicSubnetIds') : optionalList('publicSubnetIds');
  const privateSubnetIds = useExistingVpc ? list('privateSubnetIds') : optionalList('privateSubnetIds');

  if (useExistingVpc && !vpcId) {
    throw new Error('Missing required CDK context: vpcId when useExistingVpc=true');
  }

  return {
    projectName,
    useExistingVpc,
    vpcId,
    ecrRepositoryName: String(app.node.tryGetContext('ecrRepositoryName') ?? `${projectName}-backend`),
    publicSubnetIds,
    privateSubnetIds,
    networkMaxAzs: Number(app.node.tryGetContext('networkMaxAzs') ?? 2),
    networkNatGateways: Number(app.node.tryGetContext('networkNatGateways') ?? 1),
    imageTag: String(app.node.tryGetContext('imageTag') ?? 'latest'),
    desiredCount: Number(app.node.tryGetContext('desiredCount') ?? 2),
    containerPort: Number(app.node.tryGetContext('containerPort') ?? 8000),
    appEnv: String(app.node.tryGetContext('appEnv') ?? 'prod'),
    appLlmProvider: String(app.node.tryGetContext('appLlmProvider') ?? 'mock'),
    appRateLimitPerMinute: String(app.node.tryGetContext('appRateLimitPerMinute') ?? '120'),
    alarmEmail: String(app.node.tryGetContext('alarmEmail') ?? ''),
  };
}
