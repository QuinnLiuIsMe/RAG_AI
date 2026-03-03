import * as cdk from 'aws-cdk-lib';
import { Stack, StackProps } from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export interface ComputeStackProps extends StackProps {
  projectName: string;
  vpc: ec2.IVpc;
  privateSubnets: ec2.ISubnet[];
  ecrRepositoryName: string;
  imageTag: string;
  desiredCount: number;
  containerPort: number;
  appEnv: string;
  appLlmProvider: string;
  appRateLimitPerMinute: string;
}

export class ComputeStack extends Stack {
  public readonly cluster: ecs.Cluster;
  public readonly service: ecs.FargateService;
  public readonly targetGroup: ecs_patterns.ApplicationLoadBalancedFargateService['targetGroup'];
  public readonly loadBalancer: ecs_patterns.ApplicationLoadBalancedFargateService['loadBalancer'];

  constructor(scope: Construct, id: string, props: ComputeStackProps) {
    super(scope, id, props);

    const logGroup = new logs.LogGroup(this, 'BackendLogGroup', {
      logGroupName: `/ecs/${props.projectName}`,
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    this.cluster = new ecs.Cluster(this, 'Cluster', {
      vpc: props.vpc,
      clusterName: `${props.projectName}-cluster`,
      containerInsights: true,
    });

    const imageUri = `${Stack.of(this).account}.dkr.ecr.${Stack.of(this).region}.amazonaws.com/${props.ecrRepositoryName}:${props.imageTag}`;

    const pattern = new ecs_patterns.ApplicationLoadBalancedFargateService(this, 'Service', {
      cluster: this.cluster,
      serviceName: `${props.projectName}-service`,
      cpu: 512,
      memoryLimitMiB: 1024,
      desiredCount: props.desiredCount,
      publicLoadBalancer: true,
      taskSubnets: { subnets: props.privateSubnets },
      loadBalancerName: `${props.projectName}-alb`,
      taskImageOptions: {
        containerName: 'backend',
        image: ecs.ContainerImage.fromRegistry(imageUri),
        containerPort: props.containerPort,
        logDriver: ecs.LogDrivers.awsLogs({
          streamPrefix: 'ecs',
          logGroup,
        }),
        environment: {
          APP_APP_ENV: props.appEnv,
          APP_LLM_PROVIDER: props.appLlmProvider,
          APP_RATE_LIMIT_PER_MINUTE: props.appRateLimitPerMinute,
        },
      },
    });

    pattern.targetGroup.configureHealthCheck({
      path: '/health',
      healthyHttpCodes: '200',
    });

    this.service = pattern.service;
    this.targetGroup = pattern.targetGroup;
    this.loadBalancer = pattern.loadBalancer;

    new cdk.CfnOutput(this, 'AlbDnsName', {
      value: this.loadBalancer.loadBalancerDnsName,
    });

    new cdk.CfnOutput(this, 'EcsClusterName', {
      value: this.cluster.clusterName,
    });

    new cdk.CfnOutput(this, 'EcsServiceName', {
      value: this.service.serviceName,
    });
  }
}
